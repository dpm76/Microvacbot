
from pyb import Pin
from utime import sleep, sleep_us, ticks_diff, ticks_us


class Ultrasound(object):
    '''
    Driver for the HC-SR04 ultrasonic distance sensor
    '''

    PULSE2CM = 17241.3793 # cm/s
    MAX_RANGE = 3500 # cm
    OUT_OF_RANGE = 0xffffffff

    def __init__(self, triggerPort, echoPort, nSamples = 3):
        '''
        Constructor
        @param triggerPort: Port number of the trigger signal
        @param echoPort: Port number of the echo port
        @param nSamples: Number of samples to measure the distance
        '''

        self._nSamples = nSamples

        #Configure ports	
        self._trigger = Pin(triggerPort, Pin.OUT)
        self._trigger.value(0)

        self._echo = Pin(echoPort, Pin.IN)

        sleep(1)


    def read(self):
        '''
        Measures distance
        @return: Distance as centimeters
        '''

        POLL_TIMEOUT = 500000 # microseconds
        i = 0
        dist = 0

        while i < self._nSamples and dist != Ultrasound.OUT_OF_RANGE:
        
            # Send start signal
            self._trigger.on()
            sleep_us(10)
            self._trigger.off()
            
            # Wait for response
            pollStart = ticks_us()
            while self._echo.value() == 0:
                if ticks_diff(ticks_us(), pollStart) > POLL_TIMEOUT:
                    raise Exception("Timeout waiting for echo HIGH")            

            # Measure signal length
            pulseStart = ticks_us()
            while self._echo.value() == 1:
                if ticks_diff(ticks_us(), pollStart) > POLL_TIMEOUT:
                    raise Exception("Timeout waiting for echo LOW")

            pulseEnd = ticks_us()

            pulseDuration = ticks_diff(pulseEnd, pulseStart) # as microseconds
            distSample = pulseDuration * Ultrasound.PULSE2CM / 1e6 # cm

            if distSample < Ultrasound.MAX_RANGE:
                dist += distSample
            else:
                dist = Ultrasound.OUT_OF_RANGE
            
            i+=1

        return dist / i if dist != Ultrasound.OUT_OF_RANGE else Ultrasound.OUT_OF_RANGE


    def cleanup(self):
        '''
        Frees resources
        '''

        #self._trigger.cleanup()
        #self._echo.cleanup()
        pass
