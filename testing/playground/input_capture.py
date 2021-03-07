import sys
sys.path.append("/flash/userapp")

import machine
from pyb import Timer, Pin
from stm import mem32, TIM1, TIM2, TIM_SMCR, TIM_CCER

configset = {
    "F767_16bit": { 
        "timer": 1, 
        "timer-period": 0xffff,
        "timer-addr": TIM1,
        "pin-capture": Pin.board.D6,
        "led-id": 1,
    },
    "F767_32bit": { 
        "timer": 2, 
        "timer-period": 0x3fffffff,
        "timer-addr": TIM2,
        "pin-capture": Pin.board.D13,
        "led-id": 1,
    },
    "L476_32bit": { 
        "timer": 2, 
        "timer-period": 0x3fffffff,
        "timer-addr": TIM2,
        "pin-capture": Pin.board.D13,
        "led-id": 1,
    }
}

config = configset["L476_32bit"]

            
def capture(channel, cycles):

    print("capturing")
    cap = channel.capture()
    i = cycles
    while i != 0:
            
        tmp = channel.capture()
        if tmp != cap:    
            print(tmp)
            cap = tmp
            i -= 1
                
            
def main():
    # Configure the timer as a microsecond counter.
    tim = Timer(config["timer"], prescaler=(machine.freq()[0]//1000000)-1, period=config["timer-period"])
    print(tim)   

    # Configure channel for timer IC.
    ch = tim.channel(1, Timer.IC, pin=config["pin-capture"], polarity=Timer.FALLING)

    # Slave mode disabled in order to configure
    mem32[config["timer-addr"] + TIM_SMCR] = 0

    # Reset on rising edge (or falling in case of inverted detection). Ref: 25.4.3 of STM32F76xxx_reference_manual.pdf
    mem32[config["timer-addr"] + TIM_SMCR] = (mem32[config["timer-addr"] + TIM_SMCR] & 0xfffe0000) | 0x54

    # Capture sensitive to rising edge. Ref: 25.4.9 of STM32F76xxx_reference_manual.pdf
    mem32[config["timer-addr"] + TIM_CCER] = 0b1001

    try:
        capture(ch, 50)
        
    finally:
        tim.deinit()

if __name__ == "__main__":
    main()
