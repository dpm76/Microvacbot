'''
Created on 16 ago. 2019

@author: David
'''
from sys import path
path.append("/flash/userapp")

#20200727 DPM Import Mpu6050 at first, because of its size. 
from uvacbot.sensor.mpu6050 import Mpu6050
from uvacbot.io.esp8266 import Esp8266
from uvacbot.robot import Robot
from pyb import Pin
from uvacbot.activities.random_motion import RandomMotionActivity
from uvacbot.activities.remote_controlled import RemoteControlledActivity
from uvacbot.activities.musical_instrument import MusicalInstrumentActivity
from uvacbot.engine.driver import Driver
from uvacbot.engine.motion import MotionController
from uvacbot.engine.motor import Motor
from uvacbot.sensor.ultrasound import Ultrasound
from uvacbot.sensor.stepper import Stepper

PID_KP = 250.0
PID_KI = 0.0
PID_KD = 0.0


def main():
    '''
    Main application function
    Initializes the resources, launches the activity and performs a heart-beat led running 
    '''
    
    #TODO: 20200917 DPM Move the ultra-sound initialization to the robot-class
    distanceSensor = Ultrasound(Pin.board.D2, Pin.board.D4)
    
    motorLeft = Motor(Pin.board.D10, 4, 1, Pin.board.D11)
    motorRight = Motor(Pin.board.D9, 8, 2, Pin.board.D8)
    motorDriver = Driver(motorLeft, motorRight)
    
    #TODO: 20200918 DPM Move the MPU initialization to the robot-class
    mpu=Mpu6050(1)
    mpu.start()
    
    #TODO: 20200918 DPM Move the motion-controller initialization to the robot-class
    motion = MotionController(mpu, motorDriver, PID_KP, PID_KI, PID_KD).setStepper(Stepper(Pin.board.D7, Pin.PULL_UP))
    
    #TODO: 20200918 DPM Move the wifi-module initialization to the robot-class
    esp = Esp8266(3, Pin.board.D3, 115200, debug=True)
    esp.start()
    
    robot = Robot()
    
    # Add activities here:
    robot.addActivity(RandomMotionActivity(motion, distanceSensor)) #.setObstacleLed(pyb.LED(3))
    robot.addActivity(RemoteControlledActivity(motion, esp, distanceSensor))
    robot.addActivity(MusicalInstrumentActivity(distanceSensor))
    
    try:
    
        robot.run()   
    
    finally:
        
        robot.cleanup()
        #TODO: 20200918 DPM move devices' cleanup into robot's 
        esp.cleanup()
        mpu.cleanup()
        motorDriver.cleanup()
        distanceSensor.cleanup()
        

if __name__ == '__main__':
    main()
