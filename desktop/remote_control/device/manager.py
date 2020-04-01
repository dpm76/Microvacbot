'''
Created on 22 de may. de 2016

@author: david
'''
from contextlib import contextmanager
import os
import sys
from threading import Thread
from time import sleep

from device.event import EventHook
from device.joystick import Joystick


try:
    import pygame
    _pygameLoaded = True
except:    
    _pygameLoaded = False



class JoystickManager(object):
    '''
    Implements the device update loop.
    '''
    
    _instance = None
    
    @staticmethod
    def getInstance():
        
        if JoystickManager._instance == None:            
            JoystickManager._instance = JoystickManager()
            
        return JoystickManager._instance 
    
    @contextmanager
    def suppressStdout(self):
        old_stdout = sys.stdout
        with open(os.devnull, "w") as devnull:        
            sys.stdout = devnull
            try:  
                yield
            finally:
                sys.stdout = old_stdout
                
    
    def __init__(self):
        
        self._isRunning = False
        self._pollingThread = None
        
        self._joysticks = []
        
        #Events        
        self.onStart = EventHook()
        self.onStop = EventHook()


    def start(self):
        
        if _pygameLoaded and (self._pollingThread == None or not self._pollingThread.isAlive()):
            
            # Initialize the joysticks
            pygame.init()
            pygame.joystick.init()

            joystickCount = pygame.joystick.get_count()
            
            if joystickCount != 0:
                        
                for joystickIndex in range(joystickCount):
                    joystick = pygame.joystick.Joystick(joystickIndex)
                    joystick.init()
                
                    #Get device parameters
                    name = joystick.get_name()            
                    axes = joystick.get_numaxes()
                    buttons = joystick.get_numbuttons()
                    hats = joystick.get_numhats()
                    
                    self._joysticks += [Joystick(name, joystickIndex, axes, buttons, hats)]
                
                #Init thread
                self._isRunning = True
                self._pollingThread = Thread(target=self._doPolling)
                self._pollingThread.start()
            
            self.onStart.fire(self)
        

    def stop(self):
        
        self._isRunning = False
        if self._pollingThread != None and self._pollingThread.isAlive():            
            self._pollingThread.join()            
            
            self.onStop.fire(self)            
            pygame.quit()


    def getJoysticks(self):
        
        return self._joysticks

        
    def _doPolling(self):
        
        while self._isRunning:
            
            for event in pygame.event.get(): # User did something
                if event.type == pygame.QUIT: # If user clicked close
                    self._isRunning=False            
            
            for joystick in self._joysticks:
                
                #Read core data
                with self.suppressStdout():
                    pygameJoystick = pygame.joystick.Joystick(joystick.getIndex())                    

                #Axes                
                for axisIndex in range(joystick.axesCount()):
                    with self.suppressStdout():
                        axisValue = pygameJoystick.get_axis(axisIndex)                       
                    
                    if joystick._axes[axisIndex] != axisValue:                        
                        joystick._setAxisValue(axisIndex, axisValue)
                                         
                    
                #Buttons
                for buttonIndex in range(joystick.buttonsCount()):
                    with self.suppressStdout():
                        buttonValue = pygameJoystick.get_button(buttonIndex)
                    if joystick._buttons[buttonIndex] != buttonValue:
                        joystick._setButtonValue(buttonIndex, buttonValue)                        

                #Hats                    
                for hatIndex in range(joystick.hatsCount()):
                    with self.suppressStdout():
                        hatValue = pygameJoystick.get_hat(hatIndex)
                    if joystick._hats[hatIndex] != hatValue:
                        joystick._setHatValue(hatIndex, hatValue)
                        
            sleep(0.02)
