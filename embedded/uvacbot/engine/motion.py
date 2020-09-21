'''
Created on 11 mar. 2020

@author: David
'''

from math import pi, radians

from micropython import const
from uasyncio import sleep_ms
from uvacbot.engine.driver import Driver
from uvacbot.modular_math import modularDiff
from uvacbot.stabilization.pid import PidCoroutine


class MotionController(object):
    '''
    Defines the basic actions for moving the robot
    '''
    
    PID_FREQ = 50
    
    DEFAULT_THROTTLE = 50.0
    DEFAULT_ROTATION = 50.0
    
    DEFAULT_TURN_ACCURACY = radians(5)
    DEFAULT_TURN_CHECK_PERIOD = const(20) # ms
    

    def __init__(self, mpu, driver, pidkp, pidki, pidkd):
        '''
        Constructor
        
        @param mpu: Motion processing unit object
        @param driver: Robot's driver object
        @param pidkp: PID proportional constant
        @param pidki: PID integrative constant
        @param pidkd: PID derivative constant
        '''
        self._mpu = mpu
        self._driver = driver
        self._pid = PidCoroutine(1, self._readMpu, self._setPidOutput, "MC")
        self._pid.setModulus([2*pi])
        self._pid.setProportionalConstants([pidkp])
        self._pid.setIntegralConstants([pidki])
        self._pid.setDerivativeConstants([pidkd])
        self._pid.init(MotionController.PID_FREQ, False)
        
        self._driver.start()
        
        self._throttle = MotionController.DEFAULT_THROTTLE
        self._rotation = MotionController.DEFAULT_ROTATION
        
        self._backwards = False
                
    
    def setThrottle(self, throttle):
        '''
        Set the throttle for straight motion. It will be used for the next motion command.
        @param throttle: the throttle
        '''
        
        self._throttle = throttle
        
        
    def setRotation(self, rotation):
        '''
        Set the rotation strength for rotation motion. It will be used for the next rotation command.
        @param rotation: the rotation
        '''
        
        self._rotation = rotation
    
    
    def goForwards(self):
        '''
        Go forwards
        '''
        
        self._backwards = False
        self._driver.setMode(Driver.MODE_DRIVE)
        self._driver.setMotionVector(self._throttle, 0)
        self._pid.setTarget(0, self._mpu.readAngles()[2])
        self._pid.resume()
        
    
    def goBackwards(self):
        '''
        Go backwards
        '''
        
        self._backwards = True
        self._driver.setMode(Driver.MODE_DRIVE)
        self._driver.setMotionVector(-self._throttle, 0)
        self._pid.setTarget(0, self._mpu.readAngles()[2])
        self._pid.resume()
        
    
    def turnLeft(self):
        '''
        Turns (rotates) to the left
        '''
        self._pid.stop()
        self._driver.setMode(Driver.MODE_ROTATE)
        self._driver.setMotionVector(0, -self._rotation)
    
    
    def turnRight(self):
        '''
        Turns (rotates) to the right
        '''
        self._pid.stop()
        self._driver.setMode(Driver.MODE_ROTATE)
        self._driver.setMotionVector(0, self._rotation)


    async def turnTo(self, rads):
        '''
        Turns to a concrete angle
        @param rads: Target angle as radians
        '''
                        
        pi2 = 2*pi
        rads = rads % pi2
        
        curAngle = self._readMpu()[0]
        diff = modularDiff(rads, curAngle, pi2)
        if  diff > 0:
            self.turnRight()
        elif diff <= 0:
            self.turnLeft()
        
        while abs(diff) > MotionController.DEFAULT_TURN_ACCURACY:
            curAngle = self._readMpu()[0]
            diff = modularDiff(rads, curAngle, pi2)
            await sleep_ms(MotionController.DEFAULT_TURN_CHECK_PERIOD)
        
        self.stop()

   
    def stop(self):
        '''
        Stops the robot
        '''
        
        self._pid.stop()
        self._driver.stop()

    
    def _readMpu(self):
        
        return [self._mpu.readAngles()[2]]
    
    
    def _setPidOutput(self, output):
        
        self._driver.setDirection(-output[0] if self._backwards else output[0])
    
    