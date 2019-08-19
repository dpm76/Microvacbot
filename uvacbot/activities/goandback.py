import uasyncio
from uvacbot.engine.driver import Driver

class GoAndBackActivity(object):
    '''
    This activity drives the robot forward until any obstacle,
    then go back a while and try to go forward again
    '''
    
    DRIVE_THROTTLE = 50.0
    SLOW_THROTTLE = 25.0
    
    DISTANCE_TO_OBSTACLE = 40 # cm
    AFTER_STOP_TIME = 1 #seconds
    DELAY_TIME = 500 # milliseconds
    
    def __init__(self, motorDriver, distanceSensor, backTime=2):
        '''
        Constructor
        
        @param motorDriver: @see uvacbot.engine.driver.Driver 
            Object to drive the robot
        @param distanceSensor: @see uvacbot.sensor.ultrasound.Ultrasound
            Distance sensor
        @param backTime: Seconds meanwhile the robot drives back        
        '''
        
        self._motorDriver = motorDriver
        self._distanceSensor = distanceSensor
        self._backTime = backTime
        self._running = False
        
        self._obstacleLed = None
        
        loop = uasyncio.get_event_loop()
        loop.create_task(self.run())
    

    def setObstacleLed(self, obstacleLed):
        '''
        Set a led to indicate an obstacle was found
        
        @param obstacleLed: Led to indicate an obstacle was found
        @return The instance itself
        '''

        self._obstacleLed = obstacleLed
        
        return self
        
    
    def _obstacleLedOn(self):
        
        if self._obstacleLed != None:
            self._obstacleLed.on()
            
            
    def _obstacleLedOff(self):
        
        if self._obstacleLed != None:
            self._obstacleLed.off()
    
        
    def cleanup(self):
        '''
        Finalizes and releases the used resources
        '''
        
        self._motorDriver.cleanup()
        self._distanceSensor.cleanup()        
        self._obstacleLedOff()
    
    
    def isRunning(self):
        '''
        Reports the activity is currently running
        @return: True or False depending the activity is running or not
        '''
        
        return self._running
    
    
    def start(self):
        '''
        Starts the activity
        '''

        self._running = True        
                
        
    def stop(self):
        '''
        Stops the activity
        '''
        
        self._running = False
        
        
    async def run(self):
        '''
        Executes the activity:
            Check for space enough.
            In case there's space, drives forward until any obstacle
            Otherwise, it drives backwards during a short time
        '''
        
        self._motorDriver.stop()
        self._motorDriver.setMode(Driver.MODE_DRIVE)
        
        try:
            
            while True:
            
                if self._running:
                
                    distance = self._distanceSensor.read()
                    if distance < GoAndBackActivity.DISTANCE_TO_OBSTACLE:
                        
                        self._obstacleLedOn()
                            
                        self._motorDriver.stop()
                        await uasyncio.sleep(GoAndBackActivity.AFTER_STOP_TIME)
                        self._motorDriver.setThrottle(-GoAndBackActivity.SLOW_THROTTLE)
                        await uasyncio.sleep(self._backTime)
                        self._motorDriver.stop()
                        
                        self._obstacleLedOff()
                        
                    elif self._motorDriver.getThrottle() != GoAndBackActivity.DRIVE_THROTTLE:
                        
                        self._motorDriver.setThrottle(GoAndBackActivity.DRIVE_THROTTLE)
    
                        
                await uasyncio.sleep_ms(GoAndBackActivity.DELAY_TIME)
                
        finally:
            
            self._motorDriver.stop()
            
            