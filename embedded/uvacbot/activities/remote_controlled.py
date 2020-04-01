'''
Created on 30 mar. 2020

@author: David
'''
from micropython import const
from uvacbot.io.esp8266 import Connection


class _RemoteConnection(Connection):
    
    async def onReceived(self, message):
        
        cmd = message.strip()
        if cmd != "":
            self._extraObj.dispatchCommand(cmd)
                    

class RemoteControlledActivity(object):
    
    DRIVE_THROTTLE = const(80)
    SLOW_THROTTLE = const(60)
    ROTATION_THROTTLE = const(60)
    
    
    def __init__(self, motion, esp):
        
        self._motion = motion
        self._motion.setRotation(RemoteControlledActivity.ROTATION_THROTTLE)
        
        self._esp = esp
        self._esp.start()
        assert self._esp.isPresent()
        self._esp.setStaIpAddress("192.168.1.200", "192.168.1.1")
        
        self._isrunning = False
        
            
    async def start(self):
        
        self._isrunning = True
        self._esp.initServer(_RemoteConnection, self)
    
    
    async def stop(self):
        
        self._esp.stopServer()
        self._isrunning = False
        
    
    def cleanup(self):
        
        self._motion.stop()
        
    
    def isRunning(self):
        
        return self._isrunning
    
    
    def dispatchCommand(self, message):
        
        cmd = message.strip()
        
        if cmd != "":
            
            if cmd == "FWD":
                self._motion.setThrottle(RemoteControlledActivity.DRIVE_THROTTLE)
                self._motion.goForwards()
            elif cmd == "BAK":
                self._motion.setThrottle(RemoteControlledActivity.SLOW_THROTTLE)
                self._motion.goBackwards()
            elif cmd == "TLE":
                self._motion.turnLeft()
            elif cmd == "TRI":
                self._motion.turnRight()
            else:
                self._motion.stop()
