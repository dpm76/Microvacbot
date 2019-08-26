
class Board(object):
    
    def __init__(self):
    
        self.D0 = Pin()
        self.D1 = Pin()
        self.D2 = Pin()
        self.D3 = Pin()
        self.D4 = Pin()
        self.D5 = Pin()
        self.D6 = Pin()
        self.D7 = Pin()
        self.D8 = Pin()
        self.D9 = Pin()
        self.D10 = Pin()
        self.D11 = Pin()
        self.D12 = Pin()
        self.D13 = Pin()
        self.D14 = Pin()
        self.D15 = Pin()

class Pin(object):
    
    IN = 0
    OUT = 1
    
    board = Board()
    
    def __init__(self, pin, mode=None):
        
        self._value = 0
        self._pin = pin
        self._mode = mode
        
    def value(self, value = None):
        
        if value != None:
            self._value = value
        else:
            return self._value
        
    def on(self):
        
        self.value(1)
        
        
    def off(self):
        
        self.value(0)
            
    
class LED(Pin):
    
    def __init__(self, index):
        
        pass
    

class Switch():
    
    pass    


class Timer():
    
    PWM = 0
    IC = 1
    RISING = 0
    FALLING = 1
    