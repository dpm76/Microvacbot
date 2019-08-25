import sys
sys.path.append("/flash/userapp")

import utime

from uvacbot.engine.motor import Motor
from pyb import Timer, Pin, LED
from stm import mem32, TIM1, TIM2, TIM3, TIM_SMCR, TIM_CCER

configset = {
    "F767_16bit": { 
        "timer": 1, 
        "timer-period": 0xffff,
        "timer-addr": TIM1,
        "pin-capture": Pin.board.D6,
        "led-timer": 8,
        "led-freq": 8,
        "led-id": 1,
        "motor-pwm-pin": Pin.board.D9,
        "motor-reverse-pin": Pin.board.D8,
        "motor-timer": 4,
        "motor-channel": 4
    },
    "F767_32bit": { 
        "timer": 2, 
        "timer-period": 0x3fffffff,
        "timer-addr": TIM2,
        "pin-capture": Pin.board.D13,
        "led-timer": 8,
        "led-freq": 8,
        "led-id": 1,
        "motor-pwm-pin": Pin.board.D9,
        "motor-reverse-pin": Pin.board.D8,
        "motor-timer": 4,
        "motor-channel": 4
    },
    "L476_32bit": { 
        "timer": 2, 
        "timer-period": 0x3fffffff,
        "timer-addr": TIM2,
        "pin-capture": Pin.board.D13,
        "motor-pwm-pin": Pin.board.D9,
        "motor-reverse-pin": Pin.board.D8,
        "motor-timer": 8,
        "motor-channel": 2,
        "led-timer": 4,
        "led-freq": 8,
        "led-id": 1,
    },
        "L476_16bit": { 
        "timer": 3, 
        "timer-period": 0xffff,
        "timer-addr": TIM3,
        "pin-capture": Pin.board.D5,
        "motor-pwm-pin": Pin.board.D9,
        "motor-reverse-pin": Pin.board.D8,
        "motor-timer": 8,
        "motor-channel": 2,
        "led-timer": 4,
        "led-freq": 8,
        "led-id": 1,
    }

}

config = configset["L476_16bit"]

            
def capture(channel, cycles):

    cap = channel.capture()
    i = cycles
    while i != 0:
            
        tmp = channel.capture()
        if tmp != 0 and tmp != cap:    
            print(tmp)
            cap = tmp
            i -= 1
            

def testMotor(channel, motor, throttle, cycles):
    motor.setThrottle(throttle)
    utime.sleep_ms(500) #wait some milliseconds until the motor spins stable
    print("capturing @{0}".format(throttle))
    capture(channel, cycles)
    motor.stop()
                
            
def main():
    # Configure the timer as a microsecond counter.
    tim = Timer(config["timer"], prescaler=(machine.freq()[0]//1000000)-1, period=config["timer-period"])
    print(tim)
    
    # Configure timer for led blinking
    if "led-id" in config:
        timLed = Timer(config["led-timer"], freq=config["led-freq"])
        timLed.callback(lambda t: LED(config["led-id"]).toggle())

    # Configure channel for timer IC.
    ch = tim.channel(1, Timer.IC, pin=config["pin-capture"], polarity=Timer.FALLING)

    # Slave mode disabled in order to configure
    mem32[config["timer-addr"] + TIM_SMCR] = 0

    # Reset on rising edge (or falling in case of inverted detection). Ref: 25.4.3 of STM32F76xxx_reference_manual.pdf
    mem32[config["timer-addr"] + TIM_SMCR] = (mem32[config["timer-addr"] + TIM_SMCR] & 0xfffe0000) | 0x54

    # Capture sensitive to rising edge. Ref: 25.4.9 of STM32F76xxx_reference_manual.pdf
    mem32[config["timer-addr"] + TIM_CCER] = 0b1001

    motor = Motor(config["motor-pwm-pin"], config["motor-timer"], config["motor-channel"], config["motor-reverse-pin"])
    try:
       testMotor(ch, motor, 10, 20)
       testMotor(ch, motor, 20, 20)
       testMotor(ch, motor, 40, 20)
       testMotor(ch, motor, 60, 20)
       testMotor(ch, motor, 80, 20)
    finally:
        motor.cleanup()
        timLed.deinit()
    

if __name__ == "__main__":
    main()
