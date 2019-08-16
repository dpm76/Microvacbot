import pyb

from uvacbot.signal.pwm import Pwm

class Motor(object):
    '''
    Controls a motor
    '''

    PWM_FREQ = 50.0
    MIN_DUTY = 40.0
    MAX_DUTY = 90.0
    DIFF_DUTY = MAX_DUTY - MIN_DUTY

    def __init__(self, pwmPin, pwmTimer, pwmChannel, reversePin):
        '''
        Constructor
        
        @param pwmPin: Pin where the PWM-signal comes from
        @param pwmTimer: Timer to produce the PWM signal
        @param pwmChannel: Channel of the timer
        @param reversePin: Pin which controls the reverse signal
        '''
    
        self._pwm = Pwm(pwmPin, pwmTimer, pwmChannel, Motor.PWM_FREQ)
        self._reversePin = pyb.Pin(reversePin, pyb.Pin.OUT)
        self._reversePin.off()
        
        
    def cleanup(self):
        '''
        Finishes and releases the resources
        '''
        
        self.stop()
        self._pwm.cleanup()
        self._reversePin.off()
        
        
    def setThrottle(self, throttle):
        '''
        Makes the motor spin
        
        @param throttle: Percentage to spin the motor. This value can be negative, in that case, the motor spins reversed.
        '''
    
        if throttle != 0:
            if throttle > 0:       
                self._reversePin.off()
            else:
                self._reversePin.on()
            
            modThrottle = abs(throttle)
            if modThrottle > 100.0:
                modThrottle = 100.0
            
            duty = Motor.MIN_DUTY + modThrottle * Motor.DIFF_DUTY / 100.0 
            
            self._pwm.setDutyPerc(duty)
                
        else:
        
            self._pwm.setDutyPerc(0)
            
            
    def stop(self):
        '''
        Stops the motor
        '''
        
        self.setThrottle(0)
