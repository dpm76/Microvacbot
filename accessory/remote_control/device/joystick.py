'''
Created on 22 de may. de 2016

@author: david
'''
from builtins import int

from device.event import EventHook

BUTTON_X = 2
BUTTON_Y = 3
BUTTON_A = 0
BUTTON_B = 1

BUTTON_LB = 4
BUTTON_RB = 5

BUTTON_BACK = 6
BUTTON_START = 7

AXIS_LEFT_H = 0
AXIS_LEFT_V = 1

AXIS_RIGHT_H = 4
AXIS_RIGHT_V = 3

AXIS_FRONT = 2


class Joystick(object):
    '''
    Throws events depending the user behavior
    '''
    
    BUTTON_X = 2
    BUTTON_Y = 3
    BUTTON_A = 0
    BUTTON_B = 1
    
    BUTTON_LB = 4
    BUTTON_RB = 5
    
    BUTTON_BACK = 6
    BUTTON_START = 7
    
    AXIS_LEFT_H = 0
    AXIS_LEFT_V = 1
    
    AXIS_RIGHT_H = 4
    AXIS_RIGHT_V = 3
    
    AXIS_FRONT = 2    
    
    #Below this threshold, the axis value is zero. 
    _AXIS_ZERO_THRESHOLD = 1.0

    def __init__(self, name, index, numAxes, numButtons, numHats):
    
        self._name = name #Name of the product
        self._index = index #Pygame's device index
        
        self._axes = [0.0]*numAxes
        self._buttons = [0]*numButtons
        self._hats = [0.0]*numHats
        
        #Events
        self.onChanged = EventHook()
        
        self.onAxisChanged = EventHook()
        
        self.onButtonChanged = EventHook()
        self.onButtonPressed = EventHook()
        self.onButtonReleased = EventHook()
        
        self.onHatChanged = EventHook()
        self.onHatPressedNegative = EventHook()
        self.onHatPressedPositive = EventHook()
        self.onHatReleased = EventHook()

        
    def getName(self):
        
        return self._name
    
    
    def getIndex(self):
        
        return self._index
    
    
    def _setAxisValue(self, index, value):
        
        self._axes[index] = value
        
        self.onChanged.fire(self)
        self.onAxisChanged.fire(self, index)
        
    
    def axesCount(self):
        
        return len(self._axes)
    
    
    def getAllAxisValues(self):
        
        return [Joystick._calculateAxisValue(value) for value in self._axes]
    
    
    def getAxisValue(self, index):
        
        return Joystick._calculateAxisValue(self._axes[index])
    
    
    @staticmethod
    def _calculateAxisValue(rawValue):
        
        axisValue = rawValue * rawValue * rawValue * 100.0
        if axisValue < Joystick._AXIS_ZERO_THRESHOLD and axisValue > -Joystick._AXIS_ZERO_THRESHOLD:
            axisValue = 0.0
            
        return axisValue                  
        
    
    def _setButtonValue(self, index, value):
        
        self._buttons[index] = value
        
        self.onChanged.fire(self)
        self.onButtonChanged.fire(self, index)
        if self.isButtonPressed(index):
            self.onButtonPressed.fire(self, index)
        else:
            self.onButtonReleased.fire(self, index)
        
    
    def buttonsCount(self):
        
        return len(self._buttons)
    
    
    def getAllButtonValues(self):
        
        return [value != 0 for value in self._buttons]
    
    
    def isButtonPressed(self, index):
        
        return self._buttons[index] != 0
    
    
    def _setHatValue(self, index, value):
        
        self._hats[index] = value
        
        self.onChanged.fire(self)
        self.onHatChanged.fire(self, index)
        
        if isinstance(self._hats[index], (int)): 
        
            if self._hats[index] < 0:
                self.onHatPressedNegative.fire(self, index)
            elif self._hats[index] > 0:
                self.onHatPressedPositive.fire(self, index)
            else:
                self.onHatReleased.fire(self, index)
                
    
    def hatsCount(self):
        
        return len(self._hats)
    
    
    def getAllHatValues(self):
        
        return self._hats
    
    
    def getHatValue(self, index):
        
        return self._hats[index]
        
