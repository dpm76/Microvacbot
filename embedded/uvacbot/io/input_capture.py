'''
Created on 4 sept. 2019

@author: David
'''
from machine import freq
from pyb import Timer
from stm import mem32, TIM1, TIM2, TIM3, TIM4, TIM5, TIM6, TIM7, TIM8, TIM15, TIM16, TIM17, TIM_SMCR, TIM_CCER, TIM_CCMR1, TIM_CCR1


class InputCapture(object):
    '''
    Captures periodic signals on a pin
    '''
    
    _addresses = {
        1: TIM1,
        2: TIM2,
        3: TIM3,
        4: TIM4,
        5: TIM5,
        6: TIM6,
        7: TIM7,
        8: TIM8,
        15: TIM15,
        16: TIM16,
        17: TIM17}
    
    def __init__(self, timerId, pin):
        '''
        Constructor. Initializes a input-capture timer
        
        @param timerId: Id-number of the timer
        @param pin: Pin where the capture will be performed
        '''
        
        self._timerId = timerId
        self._timerAddr = InputCapture._addresses[timerId]
        self._pin = pin
        
        self._timer = Timer(self._timerId, prescaler=(freq()[0]//1000000)-1, period=0xffff)
        
        # Set the timer and channel into input mode
        self._channel = self._timer.channel(1, mode=Timer.IC, pin=self._pin, polarity=Timer.FALLING)
        
        mem32[self._timerAddr + TIM_SMCR] = 0
        mem32[self._timerAddr + TIM_SMCR] = (mem32[self._timerAddr + TIM_SMCR] & 0xfffe0000) | 0x54
        mem32[self._timerAddr + TIM_CCER] = 0b1001
        
        self.reset()        
        
    
    def reset(self):
        '''
        Resets the captured value to zero
        '''
        
        # Set the timer and channel into output mode in order to reset the capture value
        mem32[self._timerAddr + TIM_CCMR1] = 0
        mem32[self._timerAddr + TIM_CCR1] = 0
        mem32[self._timerAddr + TIM_CCMR1] = 1
       
    
    def capture(self):
        '''
        @return: The captured value
        '''
        
        return self._channel.capture()
    
        
    def stop(self):
        '''
        Stops the input capture
        '''
        
        self._timer.deinit()
        
        
    def cleanup(self):
        '''
        Releases the resources
        '''
        
        self.stop()
        self.reset()
        