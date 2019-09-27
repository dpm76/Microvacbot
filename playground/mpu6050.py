'''
Created on 21 sept. 2019

@author: David
'''
import pyb
import sys
sys.path.append("/flash/userapp")

from uvacbot.sensor.mpu6050 import Mpu6050
from uasyncio import sleep_ms, get_event_loop
from math import degrees

async def waitEnd():
    
    while not pyb.Switch().value():
        await sleep_ms(200)
        

async def readMpu(mpu):
    
    mpu.start()
    while True:
        print("temp: {0:.3f}C".format(mpu.readTemperature()))
        print(["{0:.3f}".format(degrees(a)) for a in mpu.readAngles()])
        await sleep_ms(500)
            
        
def main():
    
    print("MPU6050 test")
    mpu = Mpu6050(1)
        
    loop = get_event_loop()
    try:
        loop.create_task(readMpu(mpu))
        loop.run_until_complete(waitEnd())
    
    finally:
        mpu.cleanup()


if __name__ == "__main__":
    
    main()