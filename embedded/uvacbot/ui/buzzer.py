'''
Created on 3 abr. 2020

@author: David
'''

from micropython import const
from pyb import Timer
from utime import sleep_ms, ticks_ms, ticks_diff


class Buzzer(object):
    '''
    Plays sounds through the buzzer module
    '''

    def __init__(self, pin, timerId, channelId):
        '''
        Constructor
        
        @param pin: Pin where the module is attached to
        @param timerId: Timer associated to the pin
        @param channelId: Channel of the timer
        '''
        
        self._pin = pin
        #20200407 DPM: The timer must be initialized with a frequency, otherwise it won't beep.
        self._timer = Timer(timerId, freq=440)
        self._channel = self._timer.channel(channelId, Timer.PWM, pin=self._pin,  pulse_width=0)
        
    
    def buzz(self, freq, millisecs):
        '''
        Beeps a sound
        
        @param freq: Frequency of the sound
        @param millisecs: Time to play
        '''
        
        self._timer.init(freq=freq)
        self._channel.pulse_width_percent(50.0)
        sleep_ms(millisecs)
        self._channel.pulse_width(0)
        
            
    def trill(self, freq, millisecs, playTime=10, muteTime=10):
        '''
        Makes a vibrating sound
        
        @param freq: Frequency of the sound
        @param millisecs: Duration of the sound
        @param playTime: (default=10) Time the buzzer beeps, as milliseconds
        @param muteTime: (default=10) Time the buzzer is muted, as millisecondss
        '''
        
        startTime = ticks_ms()
        
        while millisecs > ticks_diff(ticks_ms(), startTime):
            self._timer.init(freq=freq)
            self._channel.pulse_width_percent(50.0)
            sleep_ms(playTime)
            self._channel.pulse_width(0)
            sleep_ms(muteTime)
            
            
    def slide(self, freq1, freq2, millisecs):
        '''
        Slides sound between frequencies
        
        @param freq1: Starting frequency
        @param freq2: End frequency
        @param millisecs: Duration of the effect
        '''
        
        step = (freq2 - freq1) / millisecs
        freq = freq1
        t = 0
        while t < millisecs:            
            self._timer.freq(freq)
            self._channel.pulse_width_percent(50.0)
            sleep_ms(1)
            t += 1
            freq += step
            
        self._channel.pulse_width(0)
        
            
        
    def cleanup(self):
        '''
        Removes resources
        '''
        
        self._timer.deinit()
        
        
class Sequencer(object):
    '''
    Sequences a string to play music
    '''
    
    _SCALE = {
        "c": -9,
        "d": -7,
        "e": -5,
        "f": -4,
        "g": -2,
        "a": 0,
        "b": 2
        }
    
    MODE_NORMAL = const(0)
    MODE_OCTAVE = const(1)
    
    
    def __init__(self, buzzer):
        '''
        Constructor
        
        @param buzzer: Buzzer to play sounds
        '''
        
        self._buzzer = buzzer
        self._duration = 500
        self._octave = 4
        self._shift = 0
        self._mode = Sequencer.MODE_NORMAL
        
        
    def _playNote(self, octaveBase, note):
        
        freq = 440.0 * (2.0 ** ((octaveBase * 12 + note + self._shift)/ 12.0))
        self._buzzer.buzz(freq, self._duration)
        self._shift = 0
        
        
    def play(self, seq):
        '''
        Plays a string
        
        @param seq: String coding a score.
        
        1-9:    set note duration: 1 for round, 2 for white, 3 for black and so on...
                once set, it is valid for the following notes until a new duration command
        a-g:    notes in English notation
        A-G:    notes for the upper octave
        .:      increases the duration of the next note a half of the current duration
        #:      sharp: increases the next note a semitone
        $:      flat: decreases the next note a semitone
        /:      triplet (in the current implementation the note duration must be explicitly restored)
        space(' ') : mutes the sound the time of the current duration
        O:      Sets the current octave as the following number (from 1 to 9, where the default is 4)
        ( and ):    Repeats its contents. THIS IS CURRENTLY NOT IMPLEMENTED
        _:        legato: joins the following note to the former. THIS IS CURRENTLY NOT IMPLEMENTED
        '''
        
        print("Playing: ", end='')
        
        for item in seq:
            
            print(item, end='')
            
            if self._mode == Sequencer.MODE_NORMAL:
                            
                if '1' <= item <= '9':
                    
                    self._duration = 1000//(ord(item)-48)
                    
                elif 'a' <= item <= 'g':
                    
                    self._playNote(self._octave - 4, Sequencer._SCALE[item])
                    
                    
                elif 'A' <= item <= 'G':
                    
                    self._playNote(self._octave - 3, Sequencer._SCALE[item.lower()])
                    
                    
                elif item == '.':
                    
                    self._duration += self._duration//2
                    
                elif item == '#':
                    
                    self._shift = 1
                    
                elif item == '$':
                    
                    self._shift = -1
                
                elif item == ' ':
                    
                    sleep_ms(self._duration)
                    
                elif item == 'O':
                    
                    self._mode = Sequencer.MODE_OCTAVE
                    
                elif item == '/':
                    
                    self._duration = (self._duration * 2) // 3
                    
                elif item == '(':
                    pass
                
                elif item == ')':
                    pass
                
                elif item == '|':
                    pass
                
                elif item == '_':
                    pass
                
                elif item == '\r' or item == '\n':
                    pass
                
                else:
                    raise Exception("Unknown item '{0}'".format(item))
            
            elif self._mode == Sequencer.MODE_OCTAVE:
                
                if '1' <= item <= '9':
                    
                    self._octave = int(item)
                    
                else:
                    
                    raise Exception("Octave '{0}' out of range".format(item))
                
                self._mode = Sequencer.MODE_NORMAL
                
                
    def cleanup(self):
        '''
        Removes resources
        '''
        
        self._buzzer.cleanup()
