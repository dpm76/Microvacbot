import pyb

from uvacbot.signal.pwm import Pwm

class Motor(object):

    PWM_FREQ = 50.0
    MAX_THROTTLE = 90.0

    def __init__(self, pwmPin, pwmTimer, pwmChannel, reversePin):
    
        self._pwm = Pwm(pwmPin, pwmTimer, pwmChannel, Motor.PWM_FREQ)
        self._reversePin = pyb.Pin(reversePin, pyb.Pin.OUT)
        self._reversePin.off()
        
        
    def cleanup(self):
    
        self._pwm.cleanup()
        self._reversePin.off()
        
        
    def setThrottle(self, throttle):
    
        if throttle > 0:       
            self._reversePin.off()
        else:
            self._reversePin.on()
        
        if -Motor.MAX_THROTTLE < throttle < Motor.MAX_THROTTLE: 
            self._pwm.setDutyPerc(abs(throttle))
        else:
            self._pwm.setDutyPerc(Motor.MAX_THROTTLE)
