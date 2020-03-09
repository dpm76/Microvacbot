'''
Created on 16 ago. 2019

@author: David
'''
from sys import path
path.append("/flash/userapp")

from pyb import Pin
from uvacbot.activities.goandback import GoAndBackActivity
from uvacbot.engine.driver import SmartDriver
from uvacbot.engine.motor import Motor
from uvacbot.robot import Robot
from uvacbot.sensor.mpu6050 import Mpu6050
from uvacbot.sensor.ultrasound import Ultrasound

PID_KP = 1.05
PID_KI = 0.000001
PID_KD = 0.012

PID_DIR_KP = 1.0
PID_DIR_KI = 0.0
PID_DIR_KD = 0.0

LPF_ALPHA = 0.3

def main():
    '''
    Main application function
    Initializes the resources, launch the activity and performs a heart-beat led running 
    '''
    
    distanceSensor = Ultrasound(Pin.board.D2, Pin.board.D4)
    
    motorLeft = Motor(Pin.board.D10, 4, 1, Pin.board.D11)
    motorRight = Motor(Pin.board.D9, 8, 2, Pin.board.D8)
    motorDriver = SmartDriver(motorLeft, 3, Pin.board.D5, motorRight, 1, Pin.board.D7)
    motorDriver.setMotionSensor(Mpu6050(1))
    motorDriver.setPidConstants([PID_KP]*2 + [PID_DIR_KP], [PID_KI]*2 + [PID_DIR_KI], [PID_KD]*2 + [PID_DIR_KD])
    motorDriver.setLpfAlphaConstant(LPF_ALPHA)
    
    activity = GoAndBackActivity(motorDriver, distanceSensor) #.setObstacleLed(pyb.LED(3))
    
    robot = Robot().setActivity(activity)
    
    try:
    
        robot.run()   
    
    finally:
        
        robot.cleanup()        


if __name__ == '__main__':
    main()