'''
Created on 18-sep-2020

@author: david
'''

import sys
sys.path.append("/flash/userapp")

from math import radians, pi, degrees

from pyb import Pin
from utime import sleep_ms
from uvacbot.engine.driver import Driver
from uvacbot.engine.motion import MotionController
from uvacbot.engine.motor import Motor
from uvacbot.modular_math import modularDiff
from uvacbot.sensor.mpu6050 import Mpu6050


def _readMpu(mpu):
        
        return mpu.readAngles()[2]


def turn(motion, mpu, rads):
        
        maxdiff = radians(5)
        pi2 = 2*pi
        
        curAngle = _readMpu(mpu)
        diff = modularDiff(rads, curAngle, pi2)
        if  diff > 0:
                
            print("R")
            motion.turnRight()
            
        elif diff <= 0:
                            
            print("L")
            motion.turnLeft()
        
        while abs(diff) > maxdiff:
            print("{0:.3f}, {1:.3f}".format(degrees(curAngle), degrees(diff)), end='\t')
            curAngle = _readMpu(mpu)
            diff = abs(modularDiff(rads, curAngle, pi2))
            sleep_ms(20)

        
        print("{0:.3f}, {1:.3f}".format(degrees(curAngle), degrees(diff)), end='\t')
        print("OK")
        motion.stop()
        
        #Check angle after stop
        sleep_ms(1000)
        curAngle = _readMpu(mpu)
        print("Stoped at {0:.3f} with target {1}".format(degrees(curAngle), degrees(rads)))
        
        
def main():
    
    PID_KP = 250.0
    PID_KI = 0.0
    PID_KD = 0.0
    
    print("initializing MPU")
    mpu=Mpu6050(1)
    mpu.start()
    print("MPU initialized")
    
    motorLeft = Motor(Pin.board.D10, 4, 1, Pin.board.D11)
    motorRight = Motor(Pin.board.D9, 8, 2, Pin.board.D8)
    motorDriver = Driver(motorLeft, motorRight)
    
    motion = MotionController(mpu, motorDriver, PID_KP, PID_KI, PID_KD)
    motion.setRotation(60)
    
    
    try:
        turn(motion, mpu, radians(-45))
    finally:
        mpu.cleanup()
        motorDriver.cleanup()


if __name__ == '__main__':
    main()
