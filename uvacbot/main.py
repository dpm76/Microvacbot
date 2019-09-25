'''
Created on 16 ago. 2019

@author: David
'''
import sys
sys.path.append("/flash/userapp")

import pyb
from uvacbot.activities.goandback import GoAndBackActivity
from uvacbot.engine.driver import SmartDriver
from uvacbot.engine.motor import Motor
from uvacbot.robot import Robot
from uvacbot.sensor.ultrasound import Ultrasound


PID_KP = 1.05
PID_KI = 0.000001
PID_KD = 0.012

LPF_ALPHA = 0.3

def main():
    '''
    Main application function
    Initializes the resources, launch the activity and performs a heart-beat led running 
    '''
    
    distanceSensor = Ultrasound(pyb.Pin.board.D2, pyb.Pin.board.D4)
    
    motorLeft = Motor(pyb.Pin.board.D10, 4, 1, pyb.Pin.board.D11)
    motorRight = Motor(pyb.Pin.board.D9, 8, 2, pyb.Pin.board.D8)
    motorDriver = SmartDriver(motorLeft, 3, pyb.Pin.board.D5, motorRight, 1, pyb.Pin.board.D7).setPidConstants([PID_KP]*2, [PID_KI]*2, [PID_KD]*2).setLpfAlphaConstant(LPF_ALPHA)
    
    activity = GoAndBackActivity(motorDriver, distanceSensor) #.setObstacleLed(pyb.LED(3))
    
    robot = Robot().setActivity(activity)
    
    try:
    
        robot.run()   
    
    finally:
        
        robot.cleanup()        


if __name__ == '__main__':
    main()