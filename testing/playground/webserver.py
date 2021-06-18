'''
Created on 31 mar. 2020

@author: David
'''
from sys import path
path.append("/flash/userapp")

from pyb import Switch, Pin
from uasyncio import get_event_loop, sleep_ms as ua_sleep_ms
from uvacbot.io.esp8266 import Connection, Esp8266


class WebserverConnection(Connection):
    
    async def onConnected(self):
    
        print("Connected: {0}".format(self._clientId))
        

    def onClose(self):
        
        print("Closed: {0}".format(self._clientId))
        
    
    async def onReceived(self, message):
        
        self.send('HTTP/1.1 200 OK\r\n')
        self.send('Content-Type: text/html\r\n')
        self.send('Connection: close\r\n\r\n')
        self.send("<html><head><title>web-server test</title></head><body>Hola mundo</body></html>\r\n")
        self.close()
                
                        
    
async def serve(esp):
    
    esp.initServer(WebserverConnection, port=80)
    print("Waiting for connections...")
    
    sw = Switch()        
    while not sw.value():
        await ua_sleep_ms(200)
        
    esp.stopServer()
    print("Server stopped.")
            

def main():

    print("*** Esp8266 web-server test ***")
    print("Press switch button to finish.")
    
    #Change this flag and setting properly
    clientMode = True
    ssid = "Nenukines-Haus"
    passwd = "8V83QGJR773E9767"
    ip = "192.168.1.200"
    gateway = "192.168.1.1"
    
    esp = None # Uncomment ESP8266 configuration properly
    #esp = Esp8266(3, Pin.board.D3, 115200, debug=True) #NUCLEO-L476RG
    # On NUCLEO-F767ZI TX6 is on CN7-01 (PC6) and RX6 is on CN7-11 (PC7)
    #esp = Esp8266(6, Pin.board.D8, 115200, debug=True) #NUCLEO-F767ZI
    
    if not esp:
        raise Exception("Create a Esp8266 object first.") 
    
    loop = get_event_loop()
    
    esp.start()
    assert esp.isPresent()
    try:
        if clientMode:
            esp.setOperatingMode(Esp8266.OP_MODE_CLIENT)
            esp.join(ssid, passwd)
            esp.setStaIpAddress(ip, gateway)
        else:
            esp.setOperatingMode(Esp8266.OP_MODE_AP)
            esp.setAccessPointConfig("ESP8266-AP", "", 1, Esp8266.SECURITY_OPEN)
        loop.run_until_complete(serve(esp))
        
    finally:
        esp._flushRx()
        esp.cleanup()
        print("Program finished")


if __name__ == "__main__":
        
    main()
