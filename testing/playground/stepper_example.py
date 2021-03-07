'''
Created on 10 feb. 2021

@author: David
'''
from sys import path
path.append("/flash/userapp")

from pyb import Pin
from uvacbot.sensor.stepper import Stepper
from utime import sleep

def onTrigger(sender, data):

    print("ontrigger")
    sender.stopCounting()
    print("trigger: {0}".format(data))


def main():

    count = 3
    print("Stepper example. It counts {0} steps and exits.".format(count))
    stepper = Stepper(Pin.board.D7, Pin.PULL_UP).setStepTrigger(count).setCallback(onTrigger, "hello world").startCounting()
    sleep(5)
    stepper.stopCounting()
    print("finished")

if __name__ == '__main__':
    main()