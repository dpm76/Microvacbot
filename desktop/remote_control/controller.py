'''
Created on 6 jul. 2017

@author: david
'''
from socket import socket, AF_INET, SOCK_STREAM
from time import sleep

from device.joystick import BUTTON_BACK, AXIS_LEFT_H, AXIS_LEFT_V, BUTTON_X, BUTTON_Y,\
    BUTTON_A, BUTTON_B
from device.manager import JoystickManager


class Controller(object):
    '''
    Remote controller
    '''
    

    def __init__(self):
        '''
        Constructor
        '''
        
        self._started = False
                
        self._joystickManager = JoystickManager.getInstance()
        self._joystickManager.start()
        joysticks = self._joystickManager.getJoysticks()        
        
        if len(joysticks) != 0:
            self._joystick = joysticks[0]
            self._joystick.onAxisChanged += self._onJoystickAxisChanged
            self._joystick.onButtonPressed += self._onJoystickButtonPressed
        else:
            self._joystick = None
            
        self._socket = None         
            
            
    def start(self, remoteAddress, remotePort, testing=False, local=False):
        '''
        Starts controller activity
        
        @param remoteAddress: Robot's network address
        @param remotePort: Robot's server port
        @param testing: (default=False) Boolean value indicating whether it should run in testing context
        @param local: (default=False) If true runs on local machine instead of remotely 
        '''
        
        if not self._joystick:
            raise Exception("No joystick available!")

        if not self._started:
            
            self._socket = socket(AF_INET, SOCK_STREAM)
            self._socket.settimeout(5)
            self._socket.connect((remoteAddress, remotePort))
            
            self._started = True
            
            while self._started:
                sleep(0.2)
    
        
    def stop(self):
        '''
        Stops controller activity
        '''
        
        if self._socket:
            self._socket.close()
                   
        self._joystickManager.stop()
        
        self._started = False
        
    
    def _onJoystickAxisChanged(self, sender, axisIndex):
        '''
        Process axis changed event from joystick
        @param sender: Joystick object who raised the event
        @param axisIndex: Index of axis
        '''
        
        if sender == self._joystick:
            axisValue = sender.getAxisValue(axisIndex)
            
            if axisIndex == AXIS_LEFT_V:
                
                if axisValue > 10:
                    self._socket.send(b"BAK")
                    
                elif axisValue < -10:
                    self._socket.send(b"FWD")
                    
                else:
                    self._socket.send(b"STP")
            
            elif axisIndex == AXIS_LEFT_H:
                
                if axisValue > 10:
                    self._socket.send(b"TRI")
                    
                elif axisValue < -10:
                    self._socket.send(b"TLE")
                    
                else:
                    self._socket.send(b"STP")

    

    def _onJoystickButtonPressed(self, sender, index):
        '''
        Process button pressed event from joystick
        @param sender: Joystick object who raised the event
        @param index: Index of button
        '''
        
        if sender == self._joystick:
            
            if index == BUTTON_BACK: #Back
                
                self._socket.send(b"STP")
                self._started = False
                
            elif index == BUTTON_X:
                self._socket.send(b"EXP:2")
            elif index == BUTTON_Y:
                self._socket.send(b"EXP:3")            
            elif index == BUTTON_A:
                self._socket.send(b"EXP:0")            
            elif index == BUTTON_B:
                self._socket.send(b"EXP:1")
