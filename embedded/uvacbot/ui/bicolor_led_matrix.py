'''
Created on 18/02/2019

@author: david
'''

from micropython import const
from uvacbot.io.i2c import I2CDevice


K = BLACK = const(0)
G = GREEN = const(1)
R = RED = const(2)
Y = YELLOW = const(3)


class BiColorLedMatrix(I2CDevice):
    '''
    Controller for the Adafruit's Bicolor LED 8x8 Matrix, which uses the HT16K33 chip
    Ref. https://www.adafruit.com/product/902
    '''

    DEFAULT_ADDRESS = const(0x70)
    
    BLINK_OFF = const(0)
    BLINK_2HZ = const(1)
    BLINK_1HZ = const(2)
    BLINK_HALF_HZ = const(3)
    
    
    def __init__(self, channel=1, address=DEFAULT_ADDRESS):
        '''
        Constructor

        @param channel: I2C channel where the device is connected to
        @param address: I2C address of the device
        '''
    
        super().__init__(channel, address)
        
        self._displaySetup = 0
        
        
    def start(self):
        '''
        Wakes up the device
        '''
        
        self._writeByte(0x21, 0)
    
    
    def cleanup(self):
        '''
        Shuts the device down
        '''

        self.displayOff()
        self._writeByte(0x20, 0)
        
        
    def clear(self):
        '''
        Clears the screen
        '''
        
        for row in range(0, 16):
        
            self._writeByte(row, 0)
        
    
    def setBlink(self, mode):
        '''
        Set the blink mode
        
        @param mode: Blink mode. See constants BLINK_*
        '''

        self._displaySetup = (self._displaySetup & 0x6) | (mode << 1)
        self._writeByte(0x80 | self._displaySetup, 0)
    
    
    def setDisplayState(self, on):
        '''
        Turns the display on or off
        '''
        
        self._displaySetup = (self._displaySetup & 0xe) | on
        self._writeByte(0x80 | self._displaySetup, 0)
    
        
    def displayOn(self):
        '''
        Set the display on
        '''
        
        self.setDisplayState(True)
        
        
    def displayOff(self):
        '''
        Set the display off 
        '''
        
        self.setDisplayState(False)
        

    def setDim(self, dim):
        '''
        Set the dim level

        @param dim: value between 0 and 15
        '''

        self._writeByte(0xe0 | (dim & 0x0f), 0)

        
    def dump(self, matrix):
        '''
        Dump the matrix into the device's memory.
        It doesn't care about the size of the matrix, because it uses the first 8 rows and first 8
        columns. Whenever smaller the size, it fills in with zeros.
        '''
        
        for row in range(0, 8):
        
            memGreen = 0
            memRed = 0
            
            for col in range(0, 8):
                
                memGreen |= (matrix[row][col] & GREEN) << col
                memRed |= ((matrix[row][col] & RED)>>1) << col
                
            self._writeByte(row * 2, memGreen)
            self._writeByte((row * 2) + 1, memRed)
