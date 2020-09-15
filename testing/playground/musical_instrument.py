import sys
sys.path.append("/flash/userapp")

from pyb import Switch, Pin
from uvacbot.sensor.ultrasound import Ultrasound
from uvacbot.ui.buzzer import Buzzer

from utime import sleep_ms

if __name__ == '__main__':

    PLAY_TIME = 100 # ms

    MIN_DIST = 10.0
    MAX_DIST = 100.0
    SPAN_DIST = MAX_DIST - MIN_DIST

    MIN_FREQ = 220.0
    MAX_FREQ = 880.0
    SPAN_FREQ = MAX_FREQ - MIN_FREQ

    meter = Ultrasound(Pin.board.D2, Pin.board.D4)
    buzzer = Buzzer(Pin.board.D12, 3, 1)
    
    switch = Switch()
        
    try:
        
        # Wait for switch button press the first time
        print("Press switch button to start")
        while not switch.value():
            sleep_ms(100)
    
        # Wait for switch button release        
        while switch.value():
            sleep_ms(100)
    
        # Wait for swith button press to finish
        print("Press switch button to finish")
        while not switch.value():
            dist = meter.read()
            if MIN_DIST <= dist <= MAX_DIST:
                freq = MAX_FREQ - ((dist - MIN_DIST) * SPAN_FREQ / SPAN_DIST)
                buzzer.buzz(freq, PLAY_TIME)
                sleep_ms(PLAY_TIME)
            else:
                sleep_ms(PLAY_TIME)
            
    finally:
        meter.cleanup()
        buzzer.cleanup()
