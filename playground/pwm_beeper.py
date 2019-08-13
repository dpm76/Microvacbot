import pyb
import utime

from uvacbot.signal.pwm import Pwm

alarm1 = {
             'repeat': 10, 
             'sleep1': 15,
             'sleep2': 10,
             'sleep3': 300}
             
alarm2 = {
             'repeat': 4, 
             'sleep1': 100,
             'sleep2': 50,
             'sleep3': 200}


def playAlarm(params):

    pwm = Pwm(pyb.Pin.board.D10, 4, 3, 880.0)
    for i in range(10):
        for j in range (params['repeat']):
            pwm.setDutyPerc(50.0)
            utime.sleep_ms(params['sleep1'])
            pwm.setDutyPerc(0)
            utime.sleep_ms(params['sleep2'])
            
        utime.sleep_ms(params['sleep3'])

    pwm.cleanup()
    
playAlarm(alarm2)