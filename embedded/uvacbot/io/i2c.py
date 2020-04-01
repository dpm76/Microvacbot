'''
Created on 11 sept. 2019

@author: David
'''
from machine import I2C


class I2CDevice:
    '''
    Generic I2C device. Implements the common IO functionality
    '''


    def __init__(self, i2cId, address):
        '''
        Constructor
        '''
        
        self._bus = I2C(i2cId)        
        self._address = address
        
        
    def cleanup(self):
        
        #self._bus.deinit()
        pass
        
    
    def _readUnsignedByte(self, reg):
        
        return self._bus.readfrom_mem(self._address, reg, 1)[0]
        

    def _writeByte(self, reg, byte):
    
        self._bus.writeto_mem(self._address, reg, bytes([byte]))
    
        
    def _readWord(self, regH, regL):

        byteH = self._readUnsignedByte(regH)
        byteL = self._readUnsignedByte(regL)
        
        return (byteH << 8) | byteL
        
        
    def _readSignedWord(self, regH, regL):
    
        word = self._readWord(regH, regL)
       
        if (word & 0x8000) != 0:
            word = -(0xffff - word + 1)
    
        return word
    
    
    def _readUnsignedWordHL(self, reg):
        
        byteH, byteL = self._bus.readfrom_mem(self._address, reg, 2)
        return (byteH << 8) | byteL
    

    def _readSignedWordHL(self, reg):
    
        return self._readSignedWord(reg, reg+1)
    

    def _readSignedWordLH(self, reg):

        return self._readSignedWord(reg+1, reg)
    

    def _writeWord(self, regH, regL, word):
    
        byteH = (word >> 8) & 0xff
        byteL = word & 0xff
    
        self._writeByte(regH, byteH)
        self._writeByte(regL, byteL)


    def _writeWordHL(self, reg, word):
    
        self._writeWord(reg, reg+1, word)


    def _writeWordLH(self, reg, word):
    
        self._writeWord(reg+1, reg, word)


    def _readBit(self, reg, bitNum):
        
        b = self._readUnsignedByte(reg)
        data = b & (1 << bitNum)
        
        return data
    
    
    def _writeBit(self, reg, bitNum, data):
        
        b = self._readUnsignedByte(reg)
        
        if data != 0:
            b = (b | (1 << bitNum))
        else:
            b = (b & ~(1 << bitNum))
            
        self._writeByte(reg, b)
    
    
    def _readBits(self, reg, bitStart, length):
        # 01101001 read byte
        # 76543210 bit numbers
        #    xxx   args: bitStart=4, length=3
        #    010   masked
        #   -> 010 shifted  
        
        b = self._readUnsignedByte(reg)
        mask = ((1 << length) - 1) << (bitStart - length + 1)
        b &= mask
        b >>= (bitStart - length + 1)
        
        return b
        
    
    def _writeBits(self, reg, bitStart, length, data):
        #      010 value to write
        # 76543210 bit numbers
        #    xxx   args: bitStart=4, length=3
        # 00011100 mask byte
        # 10101111 original value (sample)
        # 10100011 original & ~mask
        # 10101011 masked | value
        
        b = self._readUnsignedByte(reg)
        mask = ((1 << length) - 1) << (bitStart - length + 1)
        data <<= (bitStart - length + 1)
        data &= mask
        b &= ~(mask)
        b |= data
            
        self._writeByte(reg, b)

    
    def _readBlock(self, reg, size):
        
        #TODO: 20190912 DPM Implement true burst read
        data = []
        while len(data) < size:
            data.append(self._readUnsignedByte(reg))
            
        return data
            