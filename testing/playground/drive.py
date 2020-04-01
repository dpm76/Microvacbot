import sys
sys.path.append("/flash/userapp")

import pyb
from uvacbot.engine.motor import Motor
from uvacbot.engine.driver import Driver

import utime

def main():
    ml = Motor(pyb.Pin.board.D10, 4, 1, pyb.Pin.board.D11)
    mr = Motor(pyb.Pin.board.D9, 8, 2, pyb.Pin.board.D8)
    d = Driver(ml, mr)
    d.setMode(Driver.MODE_DRIVE)
    try:
        d.setMotionVector(80, 0)
        utime.sleep(3)
        d.stop()
        utime.sleep(1)
        d.setMotionVector(-80, 0)
        utime.sleep(3)
        d.stop()
    finally:
        d.cleanup()

if __name__=="__main__":
    main()
    