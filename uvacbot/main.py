'''
Created on 16 ago. 2019

@author: David
'''
import uasyncio
import pyb
import sys

sys.path.append("/flash/userapp")
from uvacbot.activities.goandback import GoAndBackActivity
from uvacbot.sensor.ultrasound import Ultrasound
from uvacbot.engine.driver import Driver
from uvacbot.engine.motor import Motor
from uvacbot.ui.heartbeat import Heartbeat

async def killer(duration):
    '''
    Let execute the activity during a time.
    '''
    
    await uasyncio.sleep(duration)
    

def main():
    '''
    Main application function
    Initializes the resources, launch the activity and performs a heart-beat led running 
    '''
    
    distanceSensor = Ultrasound(pyb.Pin.board.D0, pyb.Pin.board.D1)
    
    motorLeft = Motor(pyb.Pin.board.D10, 4, 3, pyb.Pin.board.D11)
    motorRight = Motor(pyb.Pin.board.D9, 4, 4, pyb.Pin.board.D8)
    motorDriver = Driver(motorLeft, motorRight)
    
    activity = GoAndBackActivity(motorDriver, distanceSensor)
    heartbeat = Heartbeat(pyb.LED(1))
    
    loop = uasyncio.get_event_loop()
    activity.start()
    heartbeat.setState(Heartbeat.States.Active)
    loop.create_task(heartbeat.run())
    loop.run_until_complete(killer(30))
    loop.close()
    activity.cleanup()


if __name__ == '__main__':
    main()