'''
Created on 16 ago. 2019

@author: David
'''
from sys import path
path.append("/flash/userapp")

from pyb import Pin
#from uvacbot.activities.random_motion import RandomMotionActivity
from uvacbot.activities.remote_controlled import RemoteControlledActivity
from uvacbot.engine.driver import Driver
from uvacbot.engine.motion import MotionController
from uvacbot.engine.motor import Motor
from uvacbot.io.esp8266 import Esp8266
from uvacbot.robot import Robot
from uvacbot.sensor.mpu6050 import Mpu6050
#from uvacbot.sensor.ultrasound import Ultrasound

PID_KP = 250.0
PID_KI = 0.0
PID_KD = 0.0


def main():
    '''
    Main application function
    Initializes the resources, launches the activity and performs a heart-beat led running 
    '''
    
    #distanceSensor = Ultrasound(Pin.board.D2, Pin.board.D4)
    
    motorLeft = Motor(Pin.board.D10, 4, 1, Pin.board.D11)
    motorRight = Motor(Pin.board.D9, 8, 2, Pin.board.D8)
    motorDriver = Driver(motorLeft, motorRight)
    
    mpu=Mpu6050(1)
    mpu.start()
    
    motion = MotionController(mpu, motorDriver, PID_KP, PID_KI, PID_KD)
    
    esp = Esp8266(3, Pin.board.D3, 115200)
    
    #activity = RandomMotionActivity(motion, distanceSensor) #.setObstacleLed(pyb.LED(3))
    activity = RemoteControlledActivity(motion, esp)
    robot = Robot().setActivity(activity)
    
    try:
    
        robot.run()   
    
    finally:
        
        robot.cleanup()
        esp.cleanup()
        mpu.cleanup()
        motorDriver.cleanup()
        

if __name__ == '__main__':
    main()
