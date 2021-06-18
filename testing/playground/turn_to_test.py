'''
Created on 22 mar. 2021

@author: David
'''

from sys import path
path.append("/flash/userapp")

from uvacbot.sensor.mpu6050 import Mpu6050
from math import radians
from micropython import alloc_emergency_exception_buf
from pyb import Pin, Switch
from uasyncio import run as uasyncio_run, sleep_ms
from uvacbot.engine.driver import Driver
from uvacbot.engine.motion import MotionController
from uvacbot.engine.motor import Motor
from uvacbot.sensor.stepper import Stepper



alloc_emergency_exception_buf(100)



async def mainTask(mc):

    print("Press user switch to start.")
    userSwitch = Switch()
    while not userSwitch.value():
        await sleep_ms(200)
    
    print("Starting")
    await sleep_ms(1000)

    await mc.turnTo(radians(30))
    await sleep_ms(1000)
    await mc.turnTo(0)
    await sleep_ms(1000)
    await mc.turnTo(radians(330))
    await sleep_ms(1000)
    await mc.turnTo(0)
    await sleep_ms(1000)
    await mc.turn(radians(15))
    await sleep_ms(1000)
    await mc.turn(radians(15))
    await sleep_ms(1000)
    await mc.turn(radians(-30))
    

def main():
        
    print("Turn_to test")
    
    #20210218 DPM: The code of this example is configured for the NUCLEO-L746RG board.
    #              Please, adapt according to the actual configuration.
    
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
        uasyncio_run(mainTask(mc))
    finally:
        mpu.cleanup()
        motorDriver.cleanup()


if __name__ == '__main__':
    main()