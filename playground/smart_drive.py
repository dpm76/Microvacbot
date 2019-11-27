import sys
import uasyncio
sys.path.append("/flash/userapp")

import pyb
from uvacbot.engine.motor import Motor
from uvacbot.engine.driver import Driver, SmartDriver
from uvacbot.sensor.mpu6050 import Mpu6050

LPF_ALPHA = 0.3

PID_KP = 0.6
PID_KI = 0.000005
PID_KD = 0.000001

PID_DIR_KP = 1.0
PID_DIR_KI = 0.0
PID_DIR_KD = 0.0 


async def mainLoop(d):
    
    try:
        d.setMode(Driver.MODE_DRIVE)
        print("Driver @50")
        d.setMotionVector(50, 0)
        await uasyncio.sleep(5)
        print("Driver @10")
        d.setMotionVector(10, 0)
        await uasyncio.sleep(5)
        d.stop()
        await uasyncio.sleep(1)
        print("Driver @-5")
        d.setMotionVector(-5, 0)
        await uasyncio.sleep(3)
        d.stop()
        await uasyncio.sleep(1)
        print("Turn @1")
        d.setMode(Driver.MODE_ROTATE)
        d.setMotionVector(0, 1)
        await uasyncio.sleep(2)
        d.stop()
        await uasyncio.sleep(1)
        d.setMode(Driver.MODE_DRIVE)
        print("Driver @5")
        d.setMotionVector(5, 0)
        await uasyncio.sleep(5)
        d.stop()
    finally:
        d.cleanup()
        

def main():
    ml = Motor(pyb.Pin.board.D10, 4, 1, pyb.Pin.board.D11)
    mr = Motor(pyb.Pin.board.D9, 8, 2, pyb.Pin.board.D8)
    d = SmartDriver(ml, 3, pyb.Pin.board.D5, mr, 1, pyb.Pin.board.D7).setMotionSensor(Mpu6050(1))
    d.setPidConstants([PID_KP]*2 + [PID_DIR_KP], [PID_KI]*2 + [PID_DIR_KI], [PID_KD]*2 + [PID_DIR_KD])
    d.setLpfAlphaConstant(LPF_ALPHA)
    
    loop = uasyncio.get_event_loop()
    loop.run_until_complete(mainLoop(d))
    loop.close()
    

if __name__=="__main__":
    main()
    