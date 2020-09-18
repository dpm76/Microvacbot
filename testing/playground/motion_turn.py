'''
Created on 18-sep-2020

@author: david
'''

import sys
sys.path.append("/flash/userapp")

from math import radians, pi, degrees
from utime import sleep_ms
from uvacbot.modular_math import modularDiff
from uvacbot.sensor.mpu6050 import Mpu6050


def _readMpu(mpu):
        
        return mpu.readAngles()[2]


def turn(mpu, rads):
        
        maxdiff = radians(5)
        pipi = 2*pi
        
        current = _readMpu(mpu)
        diff = modularDiff(rads, current, pipi)
        while abs(diff) > maxdiff:
         
            print("{0:.3f}".format(degrees(current)), end='\t')
            if  diff > 0:
                print("R")
            else:
                print("L")
                
            current = _readMpu(mpu)
            diff = modularDiff(rads, current, pipi)
            sleep_ms(500)
        
        print("{0:.3f}".format(degrees(current)), end='\t')
        print("OK")
        
        
def main():
    
    mpu=Mpu6050(1)
    mpu.start()
    
    try:
        turn(mpu, radians(45))
    finally:
        mpu.cleanup()


if __name__ == '__main__':
    main()
