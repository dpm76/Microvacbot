'''
Created on 31 mar. 2020

@author: David
'''
from sys import path
path.append("/flash/userapp")

from pyb import LED, Switch, Pin
from uasyncio import get_event_loop, sleep_ms as ua_sleep_ms
from uvacbot.io.esp8266 import Connection, Esp8266


class LedToggleConnection(Connection):
    
    async def onConnected(self):
    
        print("Connected: {0}".format(self._clientId))
        

    def onClose(self):
        
        print("Closed: {0}".format(self._clientId))
        
    
    async def onReceived(self, message):
        
        if message.startswith("LED"):
            
            try:
                ledId = int(message.split(":")[1])
                #The Nucleo-F767ZI board has 3 on-board user leds
                if ledId >= 1 and ledId <= 3:                        
                    LED(ledId).toggle()
                    print("Led['{0}'] toggled.".format(ledId))
                else:
                    print("Led not found. Please, try again.")
            except:
                print("I don't understand '{0}'. Please, try again.".format(message))
                
                
class EchoConnection(Connection):
    
    async def onConnected(self):
        
        print("Connected!")
        
        
    async def onReceived(self, message):
        
        echo = message.strip()
        if echo != "":
            self.send("echo: '{0}'\r\n".format(echo))                
        
        
    def onClose(self):
        
        print("Closed.")
        
        
        
class RemoteExecConnection(Connection):
    
    async def onReceived(self, message):
        
        code = message.strip()
        
        if code != "":
            try:
                exec("{0}\r\n".format(str(code, Esp8266.BYTES_ENCODING)))
            except Exception as ex:
                self.send("Exception: {0}\r\n".format(ex))
        
        
    
async def serve(esp):
    
    esp.initServer(EchoConnection)
    print("Waiting for connections...")
    
    sw = Switch()        
    while not sw.value():
        await ua_sleep_ms(200)
        
    esp.stopServer()
    print("Server stopped.")
            

def main():

    print("*** Esp8266 communication test ***")
    print("Press switch button to finish.")
    
    esp = Esp8266(3, Pin.board.D3, 115200, debug=True) #NUCLEO-L476RG
    #esp = Esp8266(6, Pin.board.D2, 115200, debug=True) #NUCLEO-F767ZI
    
    loop = get_event_loop()
    
    esp.start()
    assert esp.isPresent()
    try:
        #esp.setOperatingMode(Esp8266.OP_MODE_CLIENT)
        #esp.join("SSID", "PASSWD")
        #esp.setStaIpAddress("192.168.1.200", "192.168.1.1")
        esp.setOperatingMode(Esp8266.OP_MODE_AP)
        esp.setAccessPointConfig("TestAP", "", 1, Esp8266.SECURITY_OPEN)
        loop.run_until_complete(serve(esp))
        
    finally:
        esp._flushRx()
        esp.cleanup()
        print("Program finished")


if __name__ == "__main__":
        
    main()
