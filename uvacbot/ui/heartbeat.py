import uasyncio

class Heartbeat(object):

    class States(object):
    
        Waiting = 0
        Active  = 1
        

    def __init__(self, led):
    
        self._led = led
        self._state = Heartbeat.States.Waiting
        
        
    def setState(self, state):
    
        self._state = state
        
        
    def getState(self):
    
        return self._state
        
        
    async def run(self):

        self._led.off()

        while True:

            if self._state == Heartbeat.States.Active:
                self._led.on()
                await uasyncio.sleep_ms(100)
                self._led.off()
                await uasyncio.sleep_ms(100)
                self._led.on()
                await uasyncio.sleep_ms(100)
                self._led.off()
                await uasyncio.sleep_ms(700)

            else:
	
                self._led.on()
                await uasyncio.sleep_ms(500)
                self._led.off()
                await uasyncio.sleep_ms(500)
