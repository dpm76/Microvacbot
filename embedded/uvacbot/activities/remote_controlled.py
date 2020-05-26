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
    
    #TODO: 20200511 DPM Get throttle values from settings
    DRIVE_THROTTLE = const(80)
    SLOW_THROTTLE = const(60)
    ROTATION_THROTTLE = const(60)
    
    STATE_MATRICES = [
        
        [
            0b00000000,
            0b00000000,
            0b00000000,
            0b00000000,
            0b01111100,
            0b00111000,
            0b00010000,
            0b00000000
        ],
        [
            0b00000000,
            0b00010000,
            0b00111000,
            0b01111100,
            0b00000000,
            0b00000000,
            0b00000000,
            0b00000000
        ],
        [
            0b00000000,
            0b00010000,
            0b00110000,
            0b01110000,
            0b00110000,
            0b00010000,
            0b00000000,
            0b00000000
        ],
        [
            0b00000000,
            0b00001000,
            0b00001100,
            0b00001110,
            0b00001100,
            0b00001000,
            0b00000000,
            0b00000000
        ]
    ]
    
    def __init__(self, motion, esp):
        
        self._motion = motion
        self._motion.setRotation(RemoteControlledActivity.ROTATION_THROTTLE)
        
        self._esp = esp
        self._esp.start()
        assert self._esp.isPresent()
        #TODO: 20200511 DPM Move ESP module initialization to the robot-class
        #TODO: 20200511 DPM Get IP configuration from settings
        self._esp.setStaIpAddress("192.168.1.200", "192.168.1.1")
        
        self._isrunning = False
        
        self._ledMatrix = None
        
            
    async def start(self):
        
        self._isrunning = True
        self._esp.initServer(_RemoteConnection, self)
    
    
    async def stop(self):
        
        self._esp.stopServer()
        self._isrunning = False
        
        
    def setDeviceProvider(self, deviceProvider):
        '''
        Sets the object which provides the devices
        
        @param deviceProvider: The device provider
        '''
        
        self._ledMatrix = deviceProvider.getLedMatrix()
        
        
    def getIconRows(self):
        '''
        @return: The icon of this activity
        '''
        
        return ([            
            0b00000000,
            0b00111100,
            0b01000010,
            0b00011000,
            0b00100100,
            0b00000000,
            0b00011000,
            0b00000000
            ], None)
    
    
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
                self._ledMatrix.updateDisplayFromRows(greenRows=RemoteControlledActivity.STATE_MATRICES[0])
            elif cmd == "BAK":
                self._motion.setThrottle(RemoteControlledActivity.SLOW_THROTTLE)
                self._motion.goBackwards()
                self._ledMatrix.updateDisplayFromRows(redRows=RemoteControlledActivity.STATE_MATRICES[1]);
            elif cmd == "TLE":
                self._motion.turnLeft()
                #The led-matrix is placed with its base line to the forward direction, therefore left and right are reversed 
                self._ledMatrix.updateDisplayFromRows(RemoteControlledActivity.STATE_MATRICES[3],RemoteControlledActivity.STATE_MATRICES[3]);
            elif cmd == "TRI":
                self._motion.turnRight()
                self._ledMatrix.updateDisplayFromRows(RemoteControlledActivity.STATE_MATRICES[2],RemoteControlledActivity.STATE_MATRICES[2]);
            else:
                self._motion.stop()
                self._ledMatrix.displayOff()
                self._ledMatrix.clear()
