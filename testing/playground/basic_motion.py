'''
Created on 13 mar. 2020

@author: David
'''
import sys
sys.path.append("/flash/userapp")

from uasyncio import get_event_loop, sleep_ms

from pyb import Pin, Switch
from uvacbot.engine.driver import Driver
from uvacbot.engine.motion import MotionController
from uvacbot.engine.motor import Motor
from uvacbot.sensor.mpu6050 import Mpu6050


PID_KP = 250.0
PID_KI = 0.0
PID_KD = 0.0

async def _comain(mc):
  
    print("Press user switch to start.")
    userSwitch = Switch()
    while not userSwitch.value():
        await sleep_ms(200)
    
    print("Starting")    
    await sleep_ms(1000)
  
    try:
        print("Go!")
        mc.goForwards()
        await sleep_ms(5000)
        mc.stop()
        await sleep_ms(1000)
        mc.goBackwards()
        await sleep_ms(5000)
        mc.stop()
        await sleep_ms(1000)
        mc.turnRight()
        await sleep_ms(2000)
        mc.stop()
        await sleep_ms(1000)
        mc.turnLeft()
        await sleep_ms(2000)
    
    finally:
        print("Stopping")
        mc.stop()
        
    
def main():
    
    print("Initializing")
    ml = Motor(Pin.board.D10, 4, 1, Pin.board.D11)
    mr = Motor(Pin.board.D9, 8, 2, Pin.board.D8)
    d = Driver(ml, mr)
    
    mpu=Mpu6050(1)
    mpu.start()
    
    mc = MotionController(mpu, d, PID_KP, PID_KI, PID_KD)
    mc.setThrottle(80.0)
    mc.setRotation(60.0)
    
    loop = get_event_loop()
    loop.run_until_complete(_comain(mc))
    loop.close()
    
    mpu.cleanup()
    d.cleanup()
    print("Finished")
    
if __name__ == '__main__':
    main()
