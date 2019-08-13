
class Board(object):
    
    def __init__(self):
    
        self.D10 = Pin()
        self.D0 = Pin()

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
    
    
