'''
Created on 18-sep-2020

@author: david
'''

import sys
sys.path.append("/flash/userapp")
from uvacbot.sensor.mpu6050 import Mpu6050
from math import radians
from micropython import alloc_emergency_exception_buf
from pyb import Pin, Switch
from uasyncio import run as uasyncio_run, sleep_ms
from uvacbot.engine.driver import Driver
from uvacbot.engine.motion import MotionController
from uvacbot.engine.motor import Motor


alloc_emergency_exception_buf(100)


async def mainTask(motion):
    
    print("Press user switch to start.")
    userSwitch = Switch()
    while not userSwitch.value():
        await sleep_ms(200)
    
    print("Starting")
    await sleep_ms(1000)
    
    print("turning counter clockwise")
    await motion.turn(radians(-30))
    await sleep_ms(1000)
    print("turning clockwise")
    await motion.turn(radians(60))
    print("finished")
    
    
def main():
    
    print("Turn test")
    
    #20210618 DPM: The code of this example is configured for the NUCLEO-L746RG board.
    #              Please, adapt according to the actual configuration.
    
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
    
    try:
        uasyncio_run(mainTask(motion))
    finally:
        motion.stop()
        mpu.cleanup()
        motorDriver.cleanup()


if __name__ == '__main__':
    main()
