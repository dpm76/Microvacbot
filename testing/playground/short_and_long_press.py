'''
Created on 2 may. 2020

@author: David
'''
from sys import path
path.append("/flash/userapp")

from pyb import Pin
from uvacbot.ui.button import Button


if __name__ == "__main__":
    
    from utime import sleep_ms
    from micropython import alloc_emergency_exception_buf
    
    alloc_emergency_exception_buf(100)
    global i
    i=3
    
    def callback(_):
        global i
        i -= 1
        print("long")
    
    print("Push the switch button. {0} long press to exit".format(i))
    
    # The switch button is connected to the PC13 CPU-line on the Nucleo-F767ZI and Nucleo-L476RG boards.
    # Please, check in case of different boards before proceed.
    b = Button(Pin.cpu.C13, 6, lowOnPress=False).setLongPressHandler(callback).setShortPressHandler(lambda _: print("short"))

    while i > 0:
        sleep_ms(100)
        