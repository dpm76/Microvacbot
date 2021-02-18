'''
Created on 9 feb. 2021

@author: David
'''

from sys import path
path.append("/flash/userapp")

from uvacbot.sensor.mpu6050 import Mpu6050
from micropython import alloc_emergency_exception_buf
from pyb import Pin
from uasyncio import run as uasyncio_run
from uvacbot.sensor.stepper import Stepper
from uvacbot.engine.driver import Driver
from uvacbot.engine.motion import MotionController
from uvacbot.engine.motor import Motor

alloc_emergency_exception_buf(100)

async def mainTask(mc, count):
    await mc.goForwardsTo(count)
    await mc.goBackwardsTo(count)
    

def main():
        
    count = 40
    print("Motor with stepper sensor example. Moves {0} steps forwards, then {0} steps backwards and stops.".format(count))
    
    #20210218 DPM: The code of this example is configured for the NUCLEO-L746RG board.
    #              Please, adapt acording to the actual configuration.
    
    PID_KP = 250.0
    PID_KI = 0.0
    PID_KD = 0.0

    mpu=Mpu6050(1)
    mpu.start()

    motorLeft = Motor(Pin.board.D10, 4, 1, Pin.board.D11)
    motorRight = Motor(Pin.board.D9, 8, 2, Pin.board.D8)
    motorDriver = Driver(motorLeft, motorRight)

    mc = MotionController(mpu, motorDriver, PID_KP, PID_KI, PID_KD).setStepper(Stepper(Pin.board.D7, Pin.PULL_UP))
    
    try:
        uasyncio_run(mainTask(mc, count))
    finally:
        mpu.cleanup()
        motorDriver.cleanup()
    

if __name__ == '__main__':
    main()
