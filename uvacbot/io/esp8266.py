'''
Created on 28 dic. 2019

@author: david
'''
from machine import UART
from pyb import Pin
from utime import sleep_ms


class Esp8266(object):
    '''
    WiFi module
    '''
    
    BYTES_ENCODING = "ascii"
    
    OP_MODE_CLIENT = 1
    OP_MODE_AP = 2
    
    SECURITY_OPEN = 0
    SECURITY_WEP = 1
    SECURITY_WPA = 2
    SECURITY_WPA2 = 3
    SECURITY_WPA_WPA2 = 4

    def __init__(self, uartId, enablePin=None, baud=115200):
        '''
        Constructor
        
        @param uartId: Id of the UART port.
        @param enablePin: Pin to handle the enable signal of the ESP8266 module.
            If not provided here, this line should be provided using a different
            way to the module in order to activate it.
        @param baud: bit-rate of the communication (default 115200)
        '''
        
        self._uart = UART(uartId, baud)
        
        if enablePin != None:
            self._enablePin = Pin(enablePin, Pin.OUT)
        else:
            self._enablePin = None
    
    
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
    
    def reset(self):
        '''
        Resets the module
        '''
        
        self._write("AT+RST")
        sleep_ms(300)
        assert self._isOk()
    
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
            self._write("AT+CWJAP={0},{1}".format(ssid, passwd))
        else:
            self._write("AT+CWJAP={0}".format(ssid))
            
        data = self._readline()
        if not data.startswith(bytes("OK", Esp8266.BYTES_ENCODING)):
            if data.startswith(bytes("+CWJAP", Esp8266.BYTES_ENCODING)):
                error = data.split(bytes(":", Esp8266.BYTES_ENCODING))[1].strip()
                raise Exception("Cannot join to network: ERROR CODE {0}.".format(error))
            else:
                raise Exception("Cannot join to network: Undefined reason.")
            
        self._flushRx()
    
    def joinedNetwork(self):
        '''
        Gets the name of the joined network where the module is currently 
        connected to, if any.
        
        @return: Name of the network
        '''
        
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
        @param passwd: Password (optional for open AP)
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
    
    def getStaIpAddress(self):
        '''
        @return: The IP address when it is connected to a station or 
                empty if not enabled
        '''
        
        return self.getAddressByType("STAIP")
    
    def initServer(self, port=333):
        '''
        Initializes the socket server.
        
        @param port: Listening port (default 333)
        '''
        
        self._write("AT+CIPMUX=1")
        assert self._isOk()
        self._write("AT+CIPSERVER=1,{0}".format(port))
        assert self._isOk()
    
    def stopServer(self):
        '''
        Stops the socket server.
        '''
        
        self._write("AT+CIPSERVER=0")
        assert self._isOk()
    
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
        
        self._uart.write("{0}\r\n".format(data))
        print(data)
        sleep_ms(100)
        
        
    def _readline(self):
        
        data = self._uart.readline()
        print(data)
        return data
        
    
    def _flushRx(self):
        '''
        Flushes the RX-buffer
        '''
        
        while self._readline() != None:
            pass
    
    def _isOk(self, flush=True):
        '''
        @param flush: Flushes the RX-buffer after checking
        @return: True if OK return was found
        '''
        
        data = self._readline()
        isOk = data != None and data.startswith(bytes("OK", Esp8266.BYTES_ENCODING))
        while data != None and not isOk:
            data = self._readline()
            isOk = data != None and data.startswith(bytes("OK", Esp8266.BYTES_ENCODING))
        
        if flush:
            self._flushRx()    
            
        return isOk
    
    def listen(self, handler):
        '''
        TBD
        '''
        
        pass
    
    
if __name__ == "__main__":
        
    esp = Esp8266(6, Pin.board.D2, 115200)
    try:
        esp.enable()
        esp.setTxPower(10)
        assert esp.isPresent()
        print(esp.getVersion())
        esp.reset()
        esp.setTxPower(10)
        assert esp.isPresent()
        print("OP-Mode: {0}".format(esp.getOperatingMode()))
        esp.setOperatingMode(Esp8266.OP_MODE_AP | Esp8266.OP_MODE_CLIENT)
        assert esp.getOperatingMode() == (Esp8266.OP_MODE_AP | Esp8266.OP_MODE_CLIENT)
        esp.setOperatingMode(Esp8266.OP_MODE_AP)
        assert esp.getOperatingMode() == (Esp8266.OP_MODE_AP)
        esp.setAccessPointConfig("TestAP", "", 1, Esp8266.SECURITY_OPEN)
    finally:
        esp.disable()
    
    
