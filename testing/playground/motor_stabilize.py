import sys
sys.path.append("/flash/userapp")

import machine
import pyb
from stm import mem32, TIM3, TIM_SMCR, TIM_CCER
import uasyncio
from uvacbot.engine.motor import Motor
from uvacbot.stabilization.pid import PidCoroutine


icchannel = None
motor = None
lastValue = 0

def readPidInput():
    
    global lastValue
    
    pyb.LED(1).toggle()
    cap = icchannel.capture()
    numTry = 5
    while cap == 0 and numTry != 0:
        cap = icchannel.capture()
        numTry -= 1

    currentValue = 1e6/cap if cap != 0 else 0
    value = 0.7 * lastValue + 0.3 * currentValue
    lastValue = value
    print(value)

    return [value]


def setPidOutput(output):
    
    print("output: {0}".format(output[0]))
    motor.setAbsThrottle(output[0], False)
    
async def userLoop():
    
    done = False
    while not done:
        '''
        i.e. target=50; cmd = 2000
        kp = int(cmd) / 1e6 = 0.002
        pid.setProportionalConstants([kp])
        output = 0.002*15000 = 30 
        '''
        done = pyb.Switch().value()
        await uasyncio.sleep_ms(300)
        

def main():
    
    global icchannel
    global motor
    
    ictimer = pyb.Timer(3, prescaler=(machine.freq()[0]//1000000)-1, period=0xffff)
    icchannel = ictimer.channel(1, pyb.Timer.IC, pin=pyb.Pin.board.D5, polarity=pyb.Timer.FALLING)
    icchannel.capture(0)
    
    mem32[TIM3 + TIM_SMCR] = 0
    mem32[TIM3 + TIM_SMCR] = (mem32[TIM3 + TIM_SMCR] & 0xfffe0000) | 0x54
    mem32[TIM3 + TIM_CCER] = 0b1001
    
    motor = Motor(pyb.Pin.board.D9, 8, 2, pyb.Pin.board.D8)
    pid = PidCoroutine(1, readPidInput, setPidOutput, "")
    pid.setProportionalConstants([0.7])
    pid.setIntegralConstants([0.0000001])
    pid.setDerivativeConstants([0.00000012])
    try:
        pid.init(50)
        pid.setTargets([30])
        loop = uasyncio.get_event_loop()
        loop.run_until_complete(userLoop())
        loop.close()        
            
    finally:
        pid.stop()
        motor.cleanup() 
        ictimer.deinit()


if __name__ == "__main__":
    main()
    