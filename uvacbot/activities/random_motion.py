
from random import random, randrange
from uasyncio import get_event_loop, sleep_ms, sleep


class RandomMotionActivity(object):
    '''
    This activity drives the robot forward until any obstacle,
    then go back a while, turns, and try to go forward again
    '''
    
    DRIVE_THROTTLE = 80.0
    SLOW_THROTTLE = 60.0
    ROTATION_THROTTLE = 60.0    
    
    DISTANCE_TO_OBSTACLE = 30 # cm
    AFTER_STOP_TIME = 1 #seconds
    ROTATION_MIN_TIME = 500 #microseconds
    ROTATION_MAX_TIME = 1000 #microseconds
    COROUTINE_SLEEP_TIME = 500 # milliseconds
    
    def __init__(self, motion, distanceSensor, backTime=2):
        '''
        Constructor
        
        @param motion: @see uvacbot.engine.motion.MotionController 
            Object to controll the robot
        @param distanceSensor: @see uvacbot.sensor.ultrasound.Ultrasound
            Distance sensor
        @param backTime: Seconds meanwhile the robot drives back        
        '''
        
        self._motion = motion
        self._motion.setRotation(RandomMotionActivity.ROTATION_THROTTLE)
        self._distanceSensor = distanceSensor
        self._backTime = backTime
        self._running = False
        
        self._obstacleLed = None
        
        loop = get_event_loop()
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
        
        self._motion.stop()
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
        
        
    async def _rotate(self):
        
        if random() < 0.5:
            
            self._motion.turnRight()
            
        else:
            
            self._motion.turnLeft()
        
        await sleep_ms(randrange(RandomMotionActivity.ROTATION_MIN_TIME, RandomMotionActivity.ROTATION_MAX_TIME))
        self._motion.stop()
        await sleep(RandomMotionActivity.AFTER_STOP_TIME)

        
    async def run(self):
        '''
        Executes the activity:
            Check for space enough.
            In case there's space, drives forward until any obstacle
            Otherwise, it drives backwards during a short time and then rotates
        '''
        
        try:
            
            goingForwards = False
            
            while True:
            
                if self._running:
                
                    if self._distanceSensor.read() < RandomMotionActivity.DISTANCE_TO_OBSTACLE:
                        
                        # Obstacle detected
                        self._motion.stop()
                        self._obstacleLedOn()
                            
                        # Go back
                        goingForwards = False
                        await sleep(RandomMotionActivity.AFTER_STOP_TIME)
                        self._motion.setThrottle(RandomMotionActivity.SLOW_THROTTLE)
                        self._motion.goBackwards()
                        await sleep(self._backTime)
                        self._motion.stop()
                        await sleep(RandomMotionActivity.AFTER_STOP_TIME)
                        
                        # Rotate once at least
                        await self._rotate()
                        while self._distanceSensor.read()  < RandomMotionActivity.DISTANCE_TO_OBSTACLE:                        
                            await self._rotate()
                            
                        self._obstacleLedOff()
                        
                    elif not goingForwards:
                        
                        goingForwards = True
                        self._motion.setThrottle(RandomMotionActivity.DRIVE_THROTTLE)
                        self._motion.goForwards()
    
                        
                await sleep_ms(RandomMotionActivity.COROUTINE_SLEEP_TIME)
                
        finally:
            
            self._motion.stop()
            
            