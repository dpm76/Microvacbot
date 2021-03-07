'''
Created on 9 feb. 2021

@author: David
'''

from sys import path
path.append("/flash/userapp")

from micropython import alloc_emergency_exception_buf
from pyb import Pin
from uasyncio import run as uasyncio_run
from uvacbot.sensor.stepper import Stepper
from uvacbot.io.irq_event import IrqEvent

alloc_emergency_exception_buf(100)

syncEvent = IrqEvent()

def onTrigger(sender):
    
    global syncEvent
    
    print("triggered")
    sender.stopCounting()
    syncEvent.set()
    

async def mainTask():

    global syncEvent
    
    print("waiting for event")
    await syncEvent.wait()
    print("completed")


def main():
        
    count = 3
    print("Stepper asynchronous example. Counts {0} steps and exits.".format(count))
    Stepper(Pin.board.D7, Pin.PULL_UP).setStepTrigger(count).setCallback(onTrigger).startCounting()
    uasyncio_run(mainTask())
    

if __name__ == '__main__':
    main()