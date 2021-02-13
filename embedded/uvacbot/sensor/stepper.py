'''
Created on 6 feb. 2021

@author: David
'''
from pyb import Pin
from micropython import schedule

class Stepper(object):
    '''
    Counts signals received on a pin and counts them.
    Also rises an event on a concrete step.
    '''

    def __init__(self, pin, pullMode=None, stepLevel=1):
        '''
        Constructor
        @param pin: Pin where the signal is received
        @param stepLevel: value on the pin indicating a step (values: 0, 1)
        @param pullMode: (default: None) specifies if the pin has a (weak) pull resistor attached.
        @see http://docs.micropython.org/en/latest/library/machine.Pin.html?highlight=pin#machine.Pin
        '''
        
        self._pin = Pin(pin, Pin.IN, pullMode)
        self._state = 0
        self._counter = 0
        self._stepTrigger = 0
        assert stepLevel in (0,1)
        self._stepLevel = stepLevel
        self._callback = None
        self._callbackArgs = None
        
        
    def setCallback(self, callback, args=None):
        '''
        Set the callback when the trigger step is reached
        
        @param callback: Callback method with at least one parameter: this object itself
        @param args: (optional) additional object passed to the callback
        @returns self
        '''
        
        self._callback = callback
        self._callbackArgs = args
        
        return self
    
    
    def setStepTrigger(self, stepTrigger):
        '''
        Set the step trigger
        
        @param stepTrigger: Positive integer. On this step the callback will be called
        @returns self
        '''
        
        self._stepTrigger = stepTrigger
        
        return self
    
    
    def reset(self):
        '''
        Set the step counter to zero
        '''
    
        self._counter = 0
        
        
    def startCount(self):
        '''
        Starts to count steps
        @returns self
        '''
        
        self._state = self._pin.value()
        self._pin.irq(self._onStep, Pin.IRQ_RISING if self._stepLevel == 1 else Pin.IRQ_FALLING)
        
        return self
        
        
    def stopCount(self):
        '''
        Stops to count steps
        '''
        
        self._pin.irq(None)
    
    
    def _execCallback(self):
        '''
        Execs the callback
        '''
        
        if self._callback:
            self._callback(self, self._callbackArgs)
        
        
    def _onStep(self, pin):
        '''
        Counts steps. It's used on the pin's IRQ
        
        @param pin: The pin which received the signal
        '''
        
        if pin.value() != self._state:
            
            self._state = pin.value()
            if self._state == self._stepLevel:
                self._counter+=1
                
                if self._counter == self._stepTrigger:
                    schedule(Stepper._execCallback, self)
            