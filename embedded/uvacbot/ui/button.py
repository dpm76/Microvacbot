'''
Created on 1 may. 2020

@author: David
'''
from micropython import schedule
from pyb import Pin, Timer
from utime import sleep_ms


class Button(object):
    '''
    This button can handle short and long press
    '''

    def __init__(self, pin, timerId = 1, thresholdTime = 1000):
        '''
        Constructor
        
        @param pin: Pin object where the button is
        @param timerId: (default=1) Timer to determine the long press
        @param thresholdTime: Waiting time to determine a long press as milliseconds
        '''
        
        self._pin = Pin(pin)
        self._pin.init(mode=Pin.IN)
        self._pin.irq(handler=self._onPinIrq)
        
        self._thresholdTime = thresholdTime
        self._pressTime = 0
        
        self._timer = Timer(timerId)
        
        self._shortPressHandler = None
        self._longPressHandler = None
        
        self._isTimeout = False
        
        
    def _onPinIrq(self, _):
        
        self._pin.irq(handler=None)
        self._timer.deinit()
        #debounce signal 
        sleep_ms(50)
        if self._pin.value() == 0:            
            
            if not self._isTimeout:        
                schedule(self._shortPressHandler, self)
        else:
        
            self._isTimeout = False
            self._timer.init(freq=1000/self._thresholdTime, callback=self._onTimeout)
            
        self._pin.irq(handler=self._onPinIrq)
        
    
    def _onTimeout(self, t):
        
        t.deinit()
        
        self._isTimeout = True
        schedule(self._longPressHandler, self)
    
        
    def setShortPressHandler(self, handler):
        '''
        Sets the handler for short press
        '''
        
        self._shortPressHandler = handler
        
        return self
    
    
    def setLongPressHandler(self, handler):
        '''
        Sets the handler for long press
        '''
        
        self._longPressHandler = handler
        
        return self
