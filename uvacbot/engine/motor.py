import pyb

from uvacbot.signal.pwm import Pwm

class Motor(object):
    '''
    Controls a motor
    '''

    PWM_FREQ = 50.0
    MIN_DUTY = 30.0
    MAX_DUTY = 90.0
    DIFF_DUTY = (MAX_DUTY - MIN_DUTY) / 100.0

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
        
        @param throttle: (-100..100) Percentage to spin the motor. This value can be negative, in that case, the motor spins reversed.        
        '''
    
        if throttle < 0:
            self.setAbsThrottle(-throttle, True)
        else:
            self.setAbsThrottle(throttle, False)
            
            
    def setAbsThrottle(self, throttle, reverse):
        '''
        Sets the motor throttle as absolute value (negative values are considered as 0)
        
        @param throttle: (0..100) Percentagle to spin the motor.
        @param reverse: Indicates whether the motor spins forwards or backwards (reversed)
        '''
        
        if throttle < 0.0:
            throttle = 0.0
        elif throttle > 100.0:
            throttle = 100.0
        
        if throttle != 0:
        
            if reverse:
                self._reversePin.on()
            else:
                self._reversePin.off()
                
            duty = Motor.MIN_DUTY + throttle * Motor.DIFF_DUTY
            self._pwm.setDutyPerc(duty)
            
        else:
            
            self._reversePin.off()
            self._pwm.setDutyPerc(0)
            
            
            
    def stop(self):
        '''
        Stops the motor
        '''
        
        self.setAbsThrottle(0, False)
        