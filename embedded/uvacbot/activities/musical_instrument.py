'''
Created on 17-sep-2020

@author: david
'''
from micropython import const
from uasyncio import sleep_ms


class MusicalInstrumentActivity(object):
    '''
    This activity plays the buzzer according to the 
    distance detected by the ultra-sound sensor.
    '''
    
    def __init__(self, distanceSensor):
        '''
        Constructor
        
        @para distanceSensor: The distance sensor. Usually the ultra-sound sensor.
        '''
        
        #TODO: 20200917 DPM get the distance sensor from the robot-class
        
        self._distanceSensor = distanceSensor
        self._buzzer = None
        
        self._isRunning = False
    
    
    async def start(self):
        '''
        Starts the activity
        '''
        
        self._isRunning = True
        await self._run()
        
        
    async def stop(self):
        '''
        Stops the activity
        '''
        
        self._isRunning = False
        
        
    def setDeviceProvider(self, deviceProvider):
        '''
        Sets the object which provides the devices
        
        @param deviceProvider: The device provider
        '''
        
        #TODO: 20200917 DPM get the distance sensor from the robot-class
        self._buzzer = deviceProvider.getBuzzer()
    
    
    def getIconRows(self):
        '''
        @return: The icon of this activity
        '''
        
        '''
        00000000 00
        00001000 08
        00001100 0c
        00001010 0a
        00001010 0a
        00111000 38
        00111000 38
        00000000 00
        '''
        
        return ([0,8,0xc,0xa,0xa,0x38,0x38,0], [0,8,0xc,0xa,0xa,0x38,0x38,0])
    
    
    def cleanup(self):
        '''
        Finalizes and releases the used resources
        '''
        
        pass
        
    
    def isRunning(self):
        '''
        Reports the activity is currently running
        @return: True or False depending the activity is running or not
        '''
        
        return self._isRunning
    
    
    async def _run(self):
        '''
        Performs the activity.
        Reads the distance sensor and according to the read data, it plays a beep tone.
        '''
        
        CHECK_TIME = const(10) # ms

        MIN_DIST = 10.0
        MAX_DIST = 100.0
        SPAN_DIST = MAX_DIST - MIN_DIST
    
        MIN_FREQ = 110.0
        MAX_FREQ = 880.0
        SPAN_FREQ = MAX_FREQ - MIN_FREQ
        
        while self._isRunning:
            dist = self._distanceSensor.read()
            if MIN_DIST <= dist <= MAX_DIST:
                freq = MAX_FREQ - ((dist - MIN_DIST) * SPAN_FREQ / SPAN_DIST)
                self._buzzer.startBuzz(freq)                
            else:
                self._buzzer.stopBuzz()
                
            await sleep_ms(CHECK_TIME)
