import pyb

class Pwm(object):

    def __init__(self, pin, timer, channel, freq):
    
    	self._pin = pin
        self._timer = pyb.Timer(timer, freq=freq)
        self._channel = self._timer.channel(channel, pyb.Timer.PWM, pin=self._pin, pulse_width=0)
        
        
    def setDutyPerc(self, dutyPerc):
        
        self._channel.pulse_width_percent(dutyPerc)
        
        
    def cleanup(self):
    
        self._channel.pulse_width(0)
        self._timer.deinit()
        
        self._pin.init(0)
