import sys
sys.path.append("/flash/userapp")

import utime
from pyb import Pin

from uvacbot.sensor.ultrasound import Ultrasound

if __name__ == '__main__':

    GPIO_TRIGGER = Pin.board.D2
    GPIO_ECHO    = Pin.board.D4

    try:
        print("Press Ctrl+C to finish")
        meter = Ultrasound(GPIO_TRIGGER, GPIO_ECHO, 1)

        while True:
            dist = meter.read()
            if dist != Ultrasound.OUT_OF_RANGE:
                print("~ {0:.3f} cm".format(dist))
            else:
                print("Out of range!")

            utime.sleep_ms(500)

    except KeyboardInterrupt:
        print("\nCtrl+C pressed.")

    finally:
        print("Bye!")
        meter.cleanup()
