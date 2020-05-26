'''
Created on 1 nov. 2019

@author: David
'''
import sys
sys.path.append("/flash/userapp")

from utime import sleep

from uvacbot.ui.bicolor_led_matrix import BiColorLedMatrix, K, R, Y, G

def main():

    matrices = [
        [
          [K,K,R,R,R,R,K,K],
          [K,R,K,K,K,K,R,K],
          [R,K,R,K,K,R,K,R],
          [R,K,K,K,K,K,K,R],
          [R,K,R,K,K,R,K,R],
          [R,K,K,R,R,K,K,R],
          [K,R,K,K,K,K,R,K],
          [K,K,R,R,R,R,K,K]
        ],
       
        [
          [K,K,R,R,R,R,K,K],
          [K,R,R,R,R,R,R,K],
          [R,R,R,R,R,R,R,R],
          [R,R,R,R,R,R,R,R],
          [R,R,R,R,R,R,R,R],
          [R,R,R,R,R,R,R,R],
          [K,R,R,R,R,R,R,K],
          [K,K,R,R,R,R,K,K]
        ],
        [
          [K,K,Y,Y,Y,Y,K,K],
          [K,Y,Y,Y,Y,Y,Y,K],
          [Y,Y,Y,Y,Y,Y,Y,Y],
          [Y,Y,Y,Y,Y,Y,Y,Y],
          [Y,Y,Y,Y,Y,Y,Y,Y],
          [Y,Y,Y,Y,Y,Y,Y,Y],
          [K,Y,Y,Y,Y,Y,Y,K],
          [K,K,Y,Y,Y,Y,K,K]
        ],
        [
          [K,K,G,G,G,G,K,K],
          [K,G,G,G,G,G,G,K],
          [G,G,G,G,G,G,G,G],
          [G,G,G,G,G,G,G,G],
          [G,G,G,G,G,G,G,G],
          [G,G,G,G,G,G,G,G],
          [K,G,G,G,G,G,G,K],
          [K,K,G,G,G,G,K,K],
        ]
    ]

    led = BiColorLedMatrix(1, 0x70)

    try:
        
        led.start()
        led.setDim(0x8) #dim range is [0..0xf]
        
        led.updateDisplayFromRows(greenRows=bytes([0xff]*8))
        sleep(3)
        led.updateDisplayFromRows(redRows=bytes([0xff]*8))
        sleep(3)
        led.updateDisplayFromRows(bytes([0xff]*8), bytes([0xff]*8), BiColorLedMatrix.BLINK_2HZ)
        sleep(3)
        led.displayOff()
        led.clear()
        led.displayOn()
        sleep(1)
        led.updateDisplayFromMatrix(matrices[0], BiColorLedMatrix.BLINK_HALF_HZ)
        sleep(3)
        led.displayOff()
        
        led.setBlink(BiColorLedMatrix.BLINK_1HZ)
        for m in matrices:
    
            led.dumpMatrix(m)
            led.displayOn()
            sleep(5)
            led.displayOff()
    
    except:
        
        led.cleanup()


if __name__ == '__main__':

    main()
