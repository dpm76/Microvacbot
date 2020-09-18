'''
Created on 18-sep-2020

@author: david
'''

import sys
sys.path.append("/flash/userapp")

from math import radians, pi, degrees

from micropython import const
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
        
        STATE_STOP = const(0)
        STATE_RIGHT = const(1)
        STATE_LEFT = const(2)
        
        maxdiff = radians(5)
        pipi = 2*pi
        
        state = STATE_STOP
        
        current = _readMpu(mpu)
        diff = modularDiff(rads, current, pipi)
        while abs(diff) > maxdiff:
         
            print("{0:.3f}".format(degrees(current)), end='\t')
            if  diff > 0 and state != STATE_RIGHT:
                
                print("R")
                motion.turnRight()
                state = STATE_RIGHT
                
            elif diff <= 0 and state != STATE_LEFT:
                                
                print("L")
                motion.turnLeft()
                state = STATE_LEFT
                
            current = _readMpu(mpu)
            diff = modularDiff(rads, current, pipi)
            sleep_ms(100)
        
        print("{0:.3f}".format(degrees(current)), end='\t')
        print("OK")
        motion.stop()
        state = STATE_STOP
        
        
def main():
    
    PID_KP = 250.0
    PID_KI = 0.0
    PID_KD = 0.0
    
    mpu=Mpu6050(1)
    mpu.start()
    
    motorLeft = Motor(Pin.board.D10, 4, 1, Pin.board.D11)
    motorRight = Motor(Pin.board.D9, 8, 2, Pin.board.D8)
    motorDriver = Driver(motorLeft, motorRight)
    
    motion = MotionController(mpu, motorDriver, PID_KP, PID_KI, PID_KD)
    
    
    try:
        turn(motion, mpu, radians(-45))
    finally:
        mpu.cleanup()
        motorDriver.cleanup()


if __name__ == '__main__':
    main()
