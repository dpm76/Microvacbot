import utime
from pyb import Pin


class Ultrasound(object):
    '''
    Controls an ultrasound distance sensor
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

        utime.sleep(1)

		
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
            utime.sleep_ms(1)
            self._trigger.off()
            
            # Wait for response
            pollStart = utime.ticks_us()
            while self._echo.value() == 0:
                if utime.ticks_diff(utime.ticks_us(), pollStart) > POLL_TIMEOUT:
                    raise Exception("Timeout waiting for echo HIGH")            

            # Measure signal length
            pulseStart = utime.ticks_us()
            while self._echo.value() == 1:
                if utime.ticks_diff(utime.ticks_us(), pollStart) > POLL_TIMEOUT:
                    raise Exception("Timeout waiting for echo LOW")

            pulseEnd = utime.ticks_us()

            pulseDuration = utime.ticks_diff(pulseEnd, pulseStart) # as microseconds
            distSample = pulseDuration * Ultrasound.PULSE2CM / 1e6 #cm

            if distSample < Ultrasound.MAX_RANGE:
                dist += distSample
            else:
                dist = Ultrasound.OUT_OF_RANGE
            
            i+=1

        return dist / i if dist != Ultrasound.OUT_OF_RANGE else Ultrasound.OUT_OF_RANGE


    def cleanup(self):
        '''
        Frees ressources
        '''

        #self._trigger.cleanup()
        #self._echo.cleanup()
        pass
