'''
Created on 28 dic. 2019

@author: david
'''
from machine import UART
from micropython import const
from pyb import Pin
from uasyncio import get_event_loop
from utime import sleep_ms


class Esp8266(object):
    '''
    WiFi module
    
    TODO: 20200326 DPM: This class is intended for having a single client. Another limitation is that any request 
    to the module should not be performed meanwhile it is in server mode. Further improvements must be done
    to avoid these limitations.
    A possible solution could be capturing all messages from the module in a IRQ-handler where the contents 
    could be processed to rise events or send data through queues or even change the status of the object.
    '''
    
    BYTES_ENCODING = "ascii"
    
    OP_MODE_CLIENT = const(1)
    OP_MODE_AP = const(2)
    
    SECURITY_OPEN = const(0)
    SECURITY_WEP = const(1)
    SECURITY_WPA = const(2)
    SECURITY_WPA2 = const(3)
    SECURITY_WPA_WPA2 = const(4)

    def __init__(self, uartId, enablePin=None, baud=115200, debug=False):
        '''
        Constructor
        
        @param uartId: Id of the UART port.
        @param enablePin: (default=None) Pin to handle the enable signal of the ESP8266 module.
            If not provided here, this line should be provided using a different
            way to the module in order to activate it.
        @param baud: (default=115200) bit-rate of the communication
        @param debug: (default=False) prints debug information on the repl
        '''
        
        self._uart = UART(uartId, baud)
        
        if enablePin != None:
            self._enablePin = Pin(enablePin, Pin.OUT)
        else:
            self._enablePin = None
    
        self._debug = debug

    
    def start(self, txPower=40):
        '''
        Starts the module.
        Enable the module and set the TX-power.
        
        @param txPower: (default=10) the tx-power
        '''
        
        self.enable()
        self.setTxPower(txPower)
        

    def cleanup(self):
        self.disable()
        self._uart.deinit()
        
    
    def enable(self):
        '''
        Enables the module, if enable pin was provided
        '''
        
        if self._enablePin != None:
            self._enablePin.on()
            sleep_ms(500)
            self._flushRx()

    
    def disable(self):
        '''
        Disables the module, if enable pin was provided
        '''
        
        if self._enablePin != None:
            self._enablePin.off()
            
    
    def isPresent(self):
        '''
        Checks if the module is present. Just sends a "AT" command.
        
        @return: True if it's present
        '''
        
        self._write("AT")
        return self._isOk()
    
    
    def reset(self, txPower=40):
        '''
        Resets the module
        
        @param txPower: (default=10) The tx-power
        '''
        
        self._write("AT+RST")
        sleep_ms(300)
        assert self._isOk()
        self.setTxPower(txPower)
        
    
    def getVersion(self):
        '''
        Gets the firmware version
        @return: array with the version information as follows: 
            [AT version, SDK version, compile time]
        '''
        
        version = []
        
        self._write("AT+GMR")
        data = self._readline()
        while data != None and not data.startswith(bytes("OK", Esp8266.BYTES_ENCODING)):
            if not data.startswith(bytes("AT+GMR", Esp8266.BYTES_ENCODING)):
                version.append(data.strip())
            data = self._readline()
            
        return version
    
    
    def getOperatingMode(self):
        '''
        @return: The operating mode
        @raise Exception: On non reading mode
        '''
        
        self._write("AT+CWMODE?")
        data = self._readline()
        while data != None and not data.startswith(bytes("+CWMODE", Esp8266.BYTES_ENCODING)):
            data = self._readline()
        
        if data != None:
            mode = int(data.split(bytes(":", Esp8266.BYTES_ENCODING))[1].strip())
            self._flushRx()
        else:
            raise Exception("Cannot read operating mode.")
                
        return mode
    
    
    def setOperatingMode(self, mode):
        '''
        @param mode: The operating mode. Modes can be added using the or-operator.
        '''
        
        self._write("AT+CWMODE={0}".format(mode))
        assert self._isOk()
        
    
    def join(self, ssid, passwd=None):
        '''
        Joins to a wireless network. Only when client mode is enabled.
        
        @param ssid: Network name
        @param passwd: Password (Optional for open networks). Max 64 bytes ASCII
        @raise Exception: On join error.
            Error codes:
                1: connection timeout.
                2: wrong password.
                3: cannot find the target AP.
                4: connection failed.
        '''
        
        if passwd != None and passwd != "":
            self._write("AT+CWJAP_CUR=\"{0}\",\"{1}\"".format(ssid, passwd))
        else:
            self._write("AT+CWJAP_CUR=\"{0}\"".format(ssid))
            
        data = self._readline() or ""
        isError = data.startswith(bytes("FAIL", Esp8266.BYTES_ENCODING)) 
        while not isError and not data.startswith(bytes("OK", Esp8266.BYTES_ENCODING)):
            sleep_ms(100)
            data = self._readline() or ""
            isError = data.startswith(bytes("FAIL", Esp8266.BYTES_ENCODING))
        
        self._flushRx()
        if isError:
            raise Exception("Error: Cannot join to network.")
        
    
    def joinedNetwork(self):
        '''
        Gets the name of the joined network where the module is currently 
        connected to, if any.
        
        @return: Name of the network
        '''
        
        name = ""
        self._write("AT+CWJAP?")
        data = self._readline()
        self._flushRx()
        if data.startswith(bytes("+CWJAP", Esp8266.BYTES_ENCODING)):
            networkData = data.split(bytes(":", Esp8266.BYTES_ENCODING))[1]
            name = networkData.split(bytes(",", Esp8266.BYTES_ENCODING))[0]
            
        return name
    
    
    def discover(self):
        '''
        List available discovered networks. This list may not be exhaustive.
        
        @return: List of networks
        '''
        
        pass
    
    def disconnect(self):
        '''
        Disconnects the current network. Only when it is already joined.
        '''
        
        pass
    
    def setAccessPointConfig(self, ssid, passwd=None, channel=1, security=SECURITY_OPEN):
        '''
        Sets up the AP configuration.
        
        @param ssid: Name of the network
        @param passwd: Password (not used for open AP)
        @param channel: WiFi channel (default 1)
        @param security: Security mode, like WEP, WPA or WPA2 (default open)
        '''
        
        if security != Esp8266.SECURITY_OPEN:
            self._write("AT+CWSAP=\"{0}\",\"{1}\",{2},{3}".format(ssid, passwd, channel, security))

        else:
            self._write("AT+CWSAP=\"{0}\",\"\",{1},{2}".format(ssid, channel, security))
            
        assert self._isOk()
        
    
    def getAccessPointConfig(self):
        '''
        Queries the current access point configuration. This works when AP mode is
        enabled.
        '''
        
        pass
    
    def getAddresses(self):
        '''
        Gets the addresses and MACs of the module depending of the operating mode. It returns 
        addresses for the currently active modes.
        Possible address-types are: APIP, APMAC, STAIP, STAMAC
        
        @return: Dictionary of addresses and MACs with the format {address-type, address}
        ''' 
        
        addresses = {}
        
        self._write("AT+CIFSR")
        data = self._readline()
        #TODO: Seems not reading the contents
        while data != None and data.startswith(bytes("+CIFSR", Esp8266.BYTES_ENCODING)):
            addressInfo = data.strip().split(bytes(":", Esp8266.BYTES_ENCODING))[1].split(bytes(",", Esp8266.BYTES_ENCODING))
            addresses[addressInfo[0]] = addressInfo[1]

        return addresses
    
    
    def getAddressByType(self, addrType):
        '''
        Get the module address of a concrete type, if enabled.
        @param addrType: Possible address-types are: APIP, APMAC, STAIP, STAMAC
        @return: The address or none if the type is not enabled
        '''
        
        address = b"";
        addresses = self.getAddresses()
        apIpKey = bytes(addrType, Esp8266.BYTES_ENCODING) 
        if apIpKey in addresses.keys():
            address = addresses[apIpKey]
            
        return address
    
    
    def getApIpAddress(self):
        '''
        @return: The IP address of the module's access point or empty if not enabled.
        '''
        
        return self.getAddressByType("APIP")
    
    
    def setApIpAddress(self, ip, gateway, netmask="255.255.255.0"):
        '''
        Sets the IP address of the module's access point
        
        @param ip: IP address
        @param gateway: Network's gateway
        @param netmask: (default="255.255.255.0") Network's mask of the IP addresses 
        '''
        
        self._write("AT+CIPAP_CUR=\"{0}\",\"{1}\",\"{2}\"".format(ip, gateway, netmask))
        assert self._isOk()
    
    
    def getStaIpAddress(self):
        '''
        @return: The IP address when it is connected to a station or 
                empty if not enabled
        '''
        
        return self.getAddressByType("STAIP")
    
    
    def setStaIpAddress(self, ip, gateway, netmask="255.255.255.0"):
        '''
        Sets the IP address when it is connected to a station
        
        @param ip: IP address
        @param gateway: Network's gateway
        @param netmask: (default="255.255.255.0") Network's mask for the IP addresses 
        '''
        
        self._write("AT+CIPSTA_CUR=\"{0}\",\"{1}\",\"{2}\"".format(ip, gateway, netmask))
        #This command is returning b"O" instead of b"OK\r\n"
        assert self._startsLineWith("O")
        
    
    def initServer(self, connectionClass, extraObj=None, port=333):
        '''
        Initializes the socket server.
        20200325 DPM:   There is a limitation of the length of the received messages: 
                        It can receive up to 53 bytes at once and therefore further bytes will be missed.
                        
                        In instance, the client could send:
                            '123456789012345678901234567890123456789012345678901234567890' (70 bytes)
                        But it receives:
                            b'+IPD,0,70:12345678901234567890123456789012345678901234567890123'
                        The strange thing is, it knows that it should be 70 bytes, but it misses the
                        last 17 bytes, which won't came in any further input either.
        
        @see: Connection class
        @param connectionClass: (instance of Connection class) Class which implements connection actions
        @param extraObj: (default=None) Extra object to pass to the ConnectionClass new instances
        @param port: (default=333) Listening port 
        '''
        
        self._write("AT+CIPMUX=1")
        assert self._isOk()
        self._write("AT+CIPSERVER=1,{0}".format(port))
        assert self._isOk()
        
        #TODO: 20200326 DPM: Enabling IRQ here makes any request to the module not working properly.
        self._enableRxIrq()
        
        self._connections = {}
        self._connectionClass = connectionClass
        self._extraObj = extraObj
        
    
    def stopServer(self):
        '''
        Stops the socket server.
        '''
        
        self._disableRxIrq()
        self._write("AT+CIPSERVER=0")
        assert self._isOk()
        
        
    def _send(self, clientId, data):
        
        #TODO: 20200326 DPM: Disabling the IRQ during the send will miss any new client connection. 
        #        Therefore a single client can be used safely for the moment.
        
        #TODO: 20200326 DPM: Implement with a lock to avoid different coroutines sending at the same time. 
        #         Otherwise the concurrent send requests could be messed.
        self._disableRxIrq()
        self._write("AT+CIPSEND={0},{1}".format(clientId, len(data)))
        self._flushRx()
        self._write(data)
        line = self._readline()
        while line != None and not line.startswith("SEND"):
            line = self._readline()
        
        self._enableRxIrq()
            
        assert line != None and "OK" in line
        
    
    def getTimeout(self):
        '''
        Gets the socket client disconnect timeout
        (AT+CIPSTO?)
        @return: The timeout as seconds
        '''
        
        pass
    
    def setTimeout(self, timeout):
        '''
        Sets the socket client disconnect timeout
        (AT+CIPSTO=nn)
        @param timeout: The timeout as seconds
        '''
        
        pass
    
    def setTxPower(self, value):
        '''
        Sets the RF power for transmission
        
        @param value: [0..82]; unit 0.25 dBm
        '''
        
        self._write("AT+RFPOWER={0}".format(value))
        assert self._isOk()
        
        
    def _write(self, data):
        
        if self._debug:
            print("=> {0}".format(bytes(data, Esp8266.BYTES_ENCODING)))
        
        self._uart.write("{0}\r\n".format(data))
        sleep_ms(100)
        
        
    def _readline(self):
        
        data = self._uart.readline()
        
        if self._debug:
            print("<= {0}".format(data))
            
        return data
        
    
    def _flushRx(self):
        '''
        Flushes the RX-buffer
        '''
        
        while self._readline() != None:
            pass
        
    
    def _startsLineWith(self, text, flush=True):
        '''
        Checks whether the next line starts with a text
        
        @param text: Text to find
        @param flush: Flushes the RX-buffer after checking
        @return: True if the line starts with the text
        '''
        
        data = self._readline()
        startsWith = data != None and data.startswith(bytes(text, Esp8266.BYTES_ENCODING))
        while data != None and not startsWith:
            data = self._readline()
            startsWith = data != None and data.startswith(bytes(text, Esp8266.BYTES_ENCODING))
        
        if flush:
            self._flushRx()    
            
        return startsWith
    
    
    def _isOk(self, flush=True):
        '''
        @param flush: Flushes the RX-buffer after checking
        @return: True if OK return was found
        '''
        
        return self._startsLineWith("OK", flush)
    
    
    def _isError(self, flush=True):
        '''
        @param flush: Flushes the RX-buffer after checking
        @return: True if Error return was found
        '''
        
        return self._startsLineWith("ERROR", flush)
    
    
    def _enableRxIrq(self):
        
        self._uart.irq(trigger=UART.IRQ_RXIDLE, handler=self._onDataReceived)
        
    
    def _disableRxIrq(self):
        
        self._uart.irq(trigger=UART.IRQ_RXIDLE, handler=None)
    
    
    def _onDataReceived(self, _):
        
        line = None
        while self._uart.any():
            line = self._readline()
            
            if line.startswith(b"+IPD"):
                #Message from client
                contents = line.split(b":",1)
                data = contents[0].split(b",")
                clientId = int(data[1])
                message = str(contents[1][:int(data[2])], Esp8266.BYTES_ENCODING)
                get_event_loop().create_task(self._connections[clientId].onReceived(message))
                
                
            else: 
                line = line.strip()
                contents = line.split(b",",1)
                
                if len(contents) > 1:                    
                    if contents[1]==b"CONNECT":
                        #New client
                        clientId = int(contents[0])
                        self._connections[clientId] = self._connectionClass(clientId, self, self._extraObj)
                        get_event_loop().create_task(self._connections[clientId].onConnected())
                        
                    elif contents[1]==b"CLOSED":
                        #Client gone
                        clientId = int(contents[0])
                        self._connections[clientId].onClose()
                        del self._connections[clientId]
                

class Connection(object):
    '''
    Handles connections
    
    This class must be sub-classed for client dispatching.

    Possible methods to extend are:
        onConnected
        onClose
        onReceived
        
    #TODO: 31032020 DPM: Decouple service handling and connection handling
    '''
    
    def __init__(self, clientId, module, extraObj):
        '''
        Constructor
        
        The object will be always instantiated by the module-object, so this method should not be overridden
        
        @param clientId: Number of the client (it will be provided by the module-object)
        @param module: The module-object itself
        @param extraObj: Extra object
        '''
        
        self._clientId = clientId
        self._module = module
        self._extraObj = extraObj

        
    def send(self, message):
        '''
        Sends a message to the client.
        
        @param message: string sent to the client
        '''
        
        self._module._send(self._clientId, message)
        
        
    def receiveSync(self, timeout=0):
        '''
        Waits for data from the client during a time.
        If no data comes a timeout exception will be risen
        TODO: Not implemented yet!
        
        @param timeout: (default 0) milliseconds after a timeout exception. 
                        If value <=0 it waits for ever. In this case, handle with care. 
        '''
        
        raise Exception("Not implemented yet!")
    
        
    async def onConnected(self):
        '''
        Dispatches the event of a new client is connected
        It does nothing by default.
        '''
        pass
        
    
    def onClose(self):
        '''
        Dispatches the event of a client is gone
        It does nothing by default.
        '''
        pass
    
    
    async def onReceived(self, message):
        '''
        Dispatches the event of a message form client is received
        It does nothing by default.
        '''
        pass
