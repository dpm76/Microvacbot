import time

def sleep(s):
    
    time.sleep(s)
    

def sleep_ms(ms):
    
    time.sleep(ms/1e3)
    
    
def sleep_us(us):
    
    time.sleep(us/1e6)
    
    
def ticks_us():
    
    time.time() * 1e6
    
    
def ticks_ms():
    
    time.time() * 1e3
    
    
def ticks_diff(timeEnd, timeStart):
    
    return timeEnd-timeStart
