'''
Created on 16 ago. 2019

@author: David
'''
import pyb
import sys

sys.path.append("/flash/userapp")

from uvacbot.robot import Robot
from uvacbot.activities.goandback import GoAndBackActivity
from uvacbot.sensor.ultrasound import Ultrasound
from uvacbot.engine.driver import Driver
from uvacbot.engine.motor import Motor
    

def main():
    '''
    Main application function
    Initializes the resources, launch the activity and performs a heart-beat led running 
    '''
    
    distanceSensor = Ultrasound(pyb.Pin.board.D14, pyb.Pin.board.D15)
    
    motorLeft = Motor(pyb.Pin.board.D10, 4, 1, pyb.Pin.board.D11)
    motorRight = Motor(pyb.Pin.board.D9, 8, 2, pyb.Pin.board.D8)
    motorDriver = Driver(motorLeft, motorRight)
    
    activity = GoAndBackActivity(motorDriver, distanceSensor) #.setObstacleLed(pyb.LED(3))
    
    robot = Robot().setActivity(activity)
    
    try:
    
        robot.run()   
    
    finally:
        
        robot.cleanup()        


if __name__ == '__main__':
    main()