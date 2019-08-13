import uasyncio

class Heartbeat(object):
    '''
    Control LED lightning to provide a basic user communication
    '''

    class States(object):
        '''
        States
        '''
    
        Waiting = 0
        Active  = 1
        

    def __init__(self, led):
        '''
        Constructor
        
        Board led the instance is using
        '''
    
        self._led = led
        self._state = Heartbeat.States.Waiting
        
        
    def setState(self, state):
        '''
        Sets the state
        '''
    
        self._state = state
        
        
    def getState(self):
        '''
        Gets the current state
        '''
    
        return self._state
        
        
    async def run(self):
        '''
        Starts to light
        '''

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
