'''
Created on 1 nov. 2019

@author: David
'''
import sys
sys.path.append("/flash/userapp")

from utime import sleep

from uvacbot.ui.bicolor_led_matrix import BiColorLedMatrix, K, R, Y

def main():

    matrices = [
#        [
#          [K,K,R,R,R,R,K,K],
#          [K,R,K,K,K,K,R,K],
#          [R,K,R,K,K,R,K,R],
#          [R,K,K,K,K,K,K,R],
#          [R,K,R,K,K,R,K,R],
#          [R,K,K,R,R,K,K,R],
#          [K,R,K,K,K,K,R,K],
#          [K,K,R,R,R,R,K,K]
#        ],
       [
         [K,R,R,K,R,R,K,K],
         [R,R,R,R,R,R,R,K],
         [R,R,R,R,R,R,R,K],
         [R,R,R,R,R,R,R,K],
         [K,R,R,R,R,R,K,K],
         [Y,Y,R,R,R,Y,Y,K],
         [Y,K,K,R,K,Y,K,Y],
         [Y,Y,K,K,K,Y,Y,K]
       ],
       [
         [K,R,R,K,R,R,K,K],
         [R,R,R,R,R,R,R,K],
         [R,R,R,R,R,R,R,K],
         [R,R,R,R,R,R,R,K],
         [K,R,R,R,R,R,K,K],
         [Y,Y,R,R,R,Y,Y,K],
         [Y,K,Y,R,K,Y,K,K],
         [Y,Y,K,K,K,Y,Y,K]
       ],
#        [
#          [K,K,R,R,R,R,K,K],
#          [K,R,R,R,R,R,R,K],
#          [R,R,R,R,R,R,R,R],
#          [R,R,R,R,R,R,R,R],
#          [R,R,R,R,R,R,R,R],
#          [R,R,R,R,R,R,R,R],
#          [K,R,R,R,R,R,R,K],
#          [K,K,R,R,R,R,K,K]
#        ],
#        [
#          [K,K,Y,Y,Y,Y,K,K],
#          [K,Y,Y,Y,Y,Y,Y,K],
#          [Y,Y,Y,Y,Y,Y,Y,Y],
#          [Y,Y,Y,Y,Y,Y,Y,Y],
#          [Y,Y,Y,Y,Y,Y,Y,Y],
#          [Y,Y,Y,Y,Y,Y,Y,Y],
#          [K,Y,Y,Y,Y,Y,Y,K],
#          [K,K,Y,Y,Y,Y,K,K]
#        ],
#        [
#          [K,K,G,G,G,G,K,K],
#          [K,G,G,G,G,G,G,K],
#          [G,G,G,G,G,G,G,G],
#          [G,G,G,G,G,G,G,G],
#          [G,G,G,G,G,G,G,G],
#          [G,G,G,G,G,G,G,G],
#          [K,G,G,G,G,G,G,K],
#          [K,K,G,G,G,G,K,K],
#        ]
    ]

    led = BiColorLedMatrix(1, 0x70)

    try:
        
        led.start()
        led.setDim(0x8)
        led.setBlink(BiColorLedMatrix.BLINK_1HZ)
    
        for m in matrices:
    
            led.dump(m)
            led.displayOn()
            sleep(5)
            led.displayOff()
    
    except:
        
        led.cleanup()


if __name__ == '__main__':

    main()
