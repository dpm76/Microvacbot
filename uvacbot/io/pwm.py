import pyb

class Pwm(object):
    '''
    Generates PWM signal
    '''

    def __init__(self, pin, timer, channel, freq):
        '''
        Constructor
        
        @param pin: Board pin where the PWM signal will be generated. Look at pinout schematics of the proper board in order to know valid pins
        @param timer: Timer to use for signal generation. Only the valid timer for the pin can be used. Look at pinout schematics.
        @param channel: Channel to use for signal generation. Look at pinout schematics for valid channel.
        @param freq: Frequency rate the signal will be generated.
        '''
    
        self._pin = pin
        self._timer = pyb.Timer(timer, freq=freq)
        self._channel = self._timer.channel(channel, pyb.Timer.PWM, pin=self._pin, pulse_width=0)
        
        
    def setDutyPerc(self, dutyPerc):
        '''
        Sets the duty percentage
        
        @param dutyPerc: Percentage of time the PWM signal will be high for each period.
        '''
        
        self._channel.pulse_width_percent(dutyPerc)
        
        
    def cleanup(self):
        '''
        Finishes and releases resources
        '''
    
        self._channel.pulse_width(0)
        self._timer.deinit()
        
        self._pin.init(0)
