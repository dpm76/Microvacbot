'''
Created on 26 sept. 2019

@author: David
'''

from utime import sleep_ms
from uvacbot.io.i2c import I2CDevice
from math import atan2, atan, sqrt

class Mpu6050(I2CDevice):
    
    BASE_DIR = "/flash/userapp/uvacbot/sensor/"
    FILE_PATH_DMP_MEMORY = BASE_DIR + "dmp_memory.bin"
    FILE_PATH_DMP_CONFIG = BASE_DIR + "dmp_config.bin"
    FILE_PATH_DMP_UPDATES = BASE_DIR + "dmp_updates.bin"
    
    MPU6050_RA_PWR_MGMT_1 = 0x6b
    MPU6050_RA_USER_CTRL = 0x6a
 
    @staticmethod
    def dmpGetQuaternion(packet):
        # We are dealing with signed bytes
        if packet[0] > 127:
            packet[0] -= 256

        if packet[4] > 127:
            packet[4] -= 256
            
        if packet[8] > 127:
            packet[8] -= 256            
          
        if packet[12] > 127:
            packet[12] -= 256          

        data = {
            'w' : ((packet[0] << 8) + packet[1]) / 16384.0,  
            'x' : ((packet[4] << 8) + packet[5]) / 16384.0,
            'y' : ((packet[8] << 8) + packet[9]) / 16384.0,
            'z' : ((packet[12] << 8) + packet[13]) / 16384.0}        
        
        return data
        
        
    @staticmethod    
    def dmpGetGravity(q):

        data = {
            'x' : 2.0 * (q['x'] * q['z'] - q['w'] * q['y']),
            'y' : 2.0 * (q['w'] * q['x'] + q['y'] * q['z']),
            'z' : q['w'] * q['w'] - q['x'] * q['x'] - q['y'] * q['y'] + q['z'] * q['z']}
        
        return data
        
    
    @staticmethod    
    def dmpGetYawPitchRoll(q, g):
        data = {
            # yaw: (about Z axis)
            'yaw' : -atan2(2.0*q['x']*q['y']-2.0*q['w']*q['z'], 2.0*q['w']*q['w']+2.0*q['x']*q['x']-1.0),
            # roll: (nose up/down, about Y axis)
            'roll' : -atan(g['x'] / sqrt(g['y']*g['y']+g['z']*g['z'])),
            # pitch: (tilt left/right, about X axis)
            'pitch' : atan(g['y'] / sqrt(g['x']*g['x']+g['z']*g['z']))}
            
        return data
    
    
    def __init__(self, i2cId, address = 0x68):
        '''
        Constructor
        '''
        super().__init__(i2cId, address)


    def setSleepEnabled(self, status):
        #MPU6050_PWR1_SLEEP_BIT = 6
        self._writeBit(Mpu6050.MPU6050_RA_PWR_MGMT_1, 6, status)
        
        
    def setMemoryBank(self, bank, prefetchEnabled = False, userBank = False):
        bank &= 0x1F
        
        if userBank:
            bank |= 0x20
        if prefetchEnabled:
            bank |= 0x40
         
        #MPU6050_RA_BANK_SEL = 0x6d
        self._writeByte(0x6d, bank)
    
    
    def setMemoryStartAddress(self, address):
        #MPU6050_RA_MEM_START_ADDR = 0x6e
        self._writeByte(0x6e, address)
           

    def setI2CBypassEnabled(self, enabled):
        #MPU6050_RA_INT_PIN_CFG = 0x37
        #MPU6050_INTCFG_I2C_BYPASS_EN_BIT = 1
        self._writeBit(0x37, 1, enabled)


    def writeMemoryBlock(self, data, dataSize, bank = 0, address = 0):
        self.setMemoryBank(bank)
        self.setMemoryStartAddress(address)
        
        i = 0
        while i < dataSize:
            #MPU6050_RA_MEM_R_W = 0x6f
            self._writeByte(0x6f, data[i])
                    
            # reset adress to 0 after reaching 255
            if address == 255:
                address = 0
                bank += 1

                self.setMemoryBank(bank)
            else:
                address += 1
            
            self.setMemoryStartAddress(address)

            # increase byte index
            i += 1
    
    
    def writeDMPConfigurationSet(self, data, dataSize):
        # config set data is a long string of blocks with the following structure:
        # [bank] [offset] [length] [byte[0], byte[1], ..., byte[length]]
        pos = 0
        while pos < dataSize:
            j = 0
            dmpConfSet = []
            while ((j < 4) or (j < dmpConfSet[2] + 3)):
                dmpConfSet.append(data[pos])
                j += 1
                pos += 1
         
            # write data or perform special action
            if dmpConfSet[2] > 0:
                # regular block of data to write  
                self.writeMemoryBlock(dmpConfSet[3:], dmpConfSet[2], dmpConfSet[0], dmpConfSet[1])
            else:
                # special instruction
                # NOTE: this kind of behavior (what and when to do certain things)
                # is totally undocumented. This code is in here based on observed
                # behavior only, and exactly why (or even whether) it has to be here
                # is anybody's guess for now.
                if dmpConfSet[3] == 0x01:
                    # enable DMP-related interrupts
                    #MPU6050_RA_INT_ENABLE = 0x38
                    self._writeByte(0x38, 0x32);  # single operation
                    
                    
    def setClockSource(self, source):
        #MPU6050_PWR1_CLKSEL_BIT = 2
        #MPU6050_PWR1_CLKSEL_LENGTH = 3
        self._writeBits(Mpu6050.MPU6050_RA_PWR_MGMT_1, 2, 3, source)        


    def setIntEnabled(self, status):
        #MPU6050_RA_INT_ENABLE = 0x38
        self._writeByte(0x38, status)        


    def setRate(self, value):
        #MPU6050_RA_SMPLRT_DIV = 0x19
        self._writeByte(0x19, value)
        
    
    def setExternalFrameSync(self, sync):
        #MPU6050_RA_CONFIG = 0x1a
        #MPU6050_CFG_EXT_SYNC_SET_BIT = 5
        #MPU6050_CFG_EXT_SYNC_SET_LENGTH = 3
        self._writeBits(0x1a, 5, 3, sync)
        
    
    def setDLPFMode(self, mode):
        #MPU6050_RA_CONFIG = 0x1a
        #MPU6050_CFG_DLPF_CFG_BIT = 2
        #MPU6050_CFG_DLPF_CFG_LENGTH = 3
        self._writeBits(0x1a, 2, 3, mode)
     
    
    def setFullScaleGyroRange(self, gyroRange):
        #MPU6050_RA_GYRO_CONFIG = 0x1b
        #MPU6050_GCONFIG_FS_SEL_BIT = 4
        #MPU6050_GCONFIG_FS_SEL_LENGTH = 2
        self._writeBits(0x1b, 4, 2, gyroRange)        
    
    
    def setDMPConfig1(self, config):
        #MPU6050_RA_DMP_CFG_1 = 0x70
        self._writeByte(0x70, config)        
        

    def setDMPConfig2(self, config):
        #MPU6050_RA_DMP_CFG_2 = 0x71
        self._writeByte(0x71, config)


    def setOTPBankValid(self, status):
        #MPU6050_RA_XG_OFFS_TC = 0x00
        #MPU6050_TC_OTP_BNK_VLD_BIT = 0
        self._writeBit(0x00, 0, status)


    def setXGyroOffsetUser(self, value):
        #MPU6050_RA_XG_OFFS_USRH = 0x13
        self._writeWordHL(0x13, value)
        

    def setYGyroOffsetUser(self, value):
        #MPU6050_RA_YG_OFFS_USRH = 0x15
        self._writeWordHL(0x15, value)
        

    def setZGyroOffsetUser(self, value):
        #MPU6050_RA_ZG_OFFS_USRH = 0x17
        self._writeWordHL(0x17, value)


    def getFIFOCount(self):
        #MPU6050_RA_FIFO_COUNTH = 0x72
        return self._readUnsignedWordHL(0x72)

    
    def resetFIFO(self):
        #MPU6050_USERCTRL_FIFO_RESET_BIT = 2
        self._writeBit(Mpu6050.MPU6050_RA_USER_CTRL, 2, True)
        

    def setMotionDetectionThreshold(self, treshold):
        #MPU6050_RA_MOT_THR = 0x1f
        self._writeByte(0x1f, treshold)
        

    def setZeroMotionDetectionThreshold(self, treshold):
        #MPU6050_RA_ZRMOT_THR = 0x21
        self._writeByte(0x21, treshold)
    

    def setMotionDetectionDuration(self, duration):
        #MPU6050_RA_MOT_DUR = 0x20
        self._writeByte(0x20, duration)
    

    def setZeroMotionDetectionDuration(self, duration):
        #MPU6050_RA_ZRMOT_DUR = 0x22
        self._writeByte(0x22, duration)
    
        
    def setFIFOEnabled(self, status):
        #MPU6050_USERCTRL_FIFO_EN_BIT = 6
        self._writeBit(Mpu6050.MPU6050_RA_USER_CTRL, 6, status)        
        

    def setDMPEnabled(self, status):
        #MPU6050_USERCTRL_DMP_EN_BIT = 7
        self._writeBit(Mpu6050.MPU6050_RA_USER_CTRL, 7, status)
    

    def resetDMP(self):
        #MPU6050_USERCTRL_DMP_RESET_BIT = 3
        self._writeBit(Mpu6050.MPU6050_RA_USER_CTRL, 3, True)
        

    def getFIFOBlock(self):    
        #MPU6050_RA_FIFO_R_W = 0x74
        return self._readBlock(0x74, self.getFIFOCount())

    
    def getIntStatus(self):
        #MPU6050_RA_INT_STATUS = 0x3a
        return self._readUnsignedByte(0x3a)


    def _dmpUpdate(self, pos, dpmUpdates):
        
        j = 0
        dmpUpdate = []
        while ((j < 4) or (j < dmpUpdate[2] + 3)):
            dmpUpdate.append(dpmUpdates[pos])
            j += 1
            pos += 1
        
        self.writeMemoryBlock(dmpUpdate[3:], dmpUpdate[2], dmpUpdate[0], dmpUpdate[1])
        
        return pos
    
    
    def reset(self):
        #MPU6050_PWR1_DEVICE_RESET_BIT = 7
        self._writeBit(Mpu6050.MPU6050_RA_PWR_MGMT_1, 7, True)       
        

    def dmpInitialize(self):
        
        # Reset MPU6050
        self.reset()
        sleep_ms(500) # wait after reset
        # Disable sleep mode
        self.setSleepEnabled(False)
        # get MPU hardware revision
        self.setMemoryBank(0x10, True, True) # Selecting user bank 16
        self.setMemoryStartAddress(0x06) # Selecting memory byte 6
        self.setMemoryBank(0, False, False) # Resetting memory bank selection to 0
        # Enable pass through mode
        self.setI2CBypassEnabled(True)
        # load DMP code into memory banks
        dmpMemory = bytes()
        with open(Mpu6050.FILE_PATH_DMP_MEMORY, "rb") as file:
            dmpMemory = bytes(file.read())
            file.close()
        #MPU6050_DMP_CODE_SIZE = 1929
        self.writeMemoryBlock(dmpMemory, len(dmpMemory), 0, 0)
        del dmpMemory
        # write DMP configuration
        dmpConfig = bytes()
        with open(Mpu6050.FILE_PATH_DMP_CONFIG, "rb") as file:
            dmpConfig = bytes(file.read())
            file.close()
        #MPU6050_DMP_CONFIG_SIZE = 192
        self.writeDMPConfigurationSet(dmpConfig, len(dmpConfig))
        del dmpConfig
        # Setting clock source to Z Gyro
        #MPU6050_CLOCK_PLL_ZGYRO = 0x03
        self.setClockSource(0x03)
        # Setting DMP and FIFO_OFLOW interrupts enabled
        self.setIntEnabled(0x12)
        # Setting sample rate to 200Hz
        self.setRate(4) # 1khz / (1 + 4) = 200 Hz [9 = 100 Hz]
        # Setting external frame sync to TEMP_OUT_L[0]
        #MPU6050_EXT_SYNC_TEMP_OUT_L = 0x01
        self.setExternalFrameSync(0x01)
        # Setting DLPF bandwidth to 42Hz
        #MPU6050_DLPF_BW_42 = 0x03
        self.setDLPFMode(0x03)
        # Setting gyro sensitivity to +/- 2000 deg/sec
        #MPU6050_GYRO_FS_2000 = 0x03
        self.setFullScaleGyroRange(0x03)
        # Setting DMP configuration bytes (function unknown)
        self.setDMPConfig1(0x03)
        self.setDMPConfig2(0x00)
        # Clearing OTP Bank flag
        self.setOTPBankValid(False)
        # Setting X/Y/Z gyro user offsets to zero
        self.setXGyroOffsetUser(0)
        self.setYGyroOffsetUser(0)
        self.setZGyroOffsetUser(0)
        # Writing final memory update 1/7 (function unknown)
        dmpUpdates = bytes()
        with open(Mpu6050.FILE_PATH_DMP_UPDATES, "rb") as file:
            dmpUpdates = bytes(file.read())
            file.close()
        pos = self._dmpUpdate(0,dmpUpdates)
        # Writing final memory update 2/7 (function unknown)
        pos = self._dmpUpdate(pos,dmpUpdates)
        # Resetting FIFO
        self.resetFIFO()
        # Setting motion detection threshold to 2
        self.setMotionDetectionThreshold(2)
        # Setting zero-motion detection threshold to 156
        self.setZeroMotionDetectionThreshold(156)
        # Setting motion detection duration to 80
        self.setMotionDetectionDuration(80)
        # Setting zero-motion detection duration to 0
        self.setZeroMotionDetectionDuration(0)
        # Resetting FIFO
        self.resetFIFO()  
        # Enabling FIFO
        self.setFIFOEnabled(True)
        # Enabling DMP
        self.setDMPEnabled(True)
        # Resetting DMP
        self.resetDMP()
        # Writing final memory update 3/7 (function unknown)
        pos = self._dmpUpdate(pos,dmpUpdates)
        # Writing final memory update 4/7 (function unknown)
        pos = self._dmpUpdate(pos,dmpUpdates)
        # Writing final memory update 5/7 (function unknown)
        pos = self._dmpUpdate(pos,dmpUpdates)
        # Waiting for FIFO count > 2
        fifoCount = self.getFIFOCount()
        while (fifoCount < 3):
            sleep_ms(1)
            fifoCount = self.getFIFOCount()
        
        # Reading FIFO data
        self.getFIFOBlock()
        
        # Writing final memory update 6/7 (function unknown)
        pos = self._dmpUpdate(pos,dmpUpdates)
        # Writing final memory update 7/7 (function unknown)
        pos = self._dmpUpdate(pos,dmpUpdates)
        del dmpUpdates
        # Disabling DMP (you turn it on later)
        self.setDMPEnabled(False)
        # Resetting FIFO and clearing INT status one last time
        self.resetFIFO()
        self.getIntStatus()
        
        
    def _readDmpPacket(self):
                
        self.resetFIFO()
        
        fifoCount = self.getFIFOCount()
        #DMP_PACKET_SIZE = 42
        while fifoCount < 42:
            sleep_ms(1)
            fifoCount = self.getFIFOCount()
        
        packet = self.getFIFOBlock()
                     
        return packet

    
    def _calibrate(self):
        '''
        Calibrates the sensor
        '''
        #Wait for stabilization
        #sleep_ms(20000)
        self.resetFIFO()
        
        #Wait for next packet
        sleep_ms(100)
        packet = self._readDmpPacket()
        
        q = Mpu6050.dmpGetQuaternion(packet)
        g = Mpu6050.dmpGetGravity(q)
                         
        ypr = Mpu6050.dmpGetYawPitchRoll(q, g)
        self._angleOffset = [ypr["pitch"], ypr["roll"], ypr["yaw"]]

    
    def readTemperature(self):
        '''
        @return: Celsius degrees
        '''
        
        #MPU6050_RA_TEMP_OUT_H = 0x41
        return (self._readSignedWordHL(0x41)/340.0) + 36.53


    def readAngles(self):
        '''
        @return: Angles as radians
        '''
        
        packet = self._readDmpPacket()       
        q = Mpu6050.dmpGetQuaternion(packet)
        g = Mpu6050.dmpGetGravity(q)
        
        ypr = Mpu6050.dmpGetYawPitchRoll(q, g)        
        angles = [ypr["pitch"]-self._angleOffset[0], ypr["roll"]-self._angleOffset[1], ypr["yaw"]-self._angleOffset[2]]
        
        return angles

    
    def start(self):
        
        self._angleOffset = [0]*3
        
        self.dmpInitialize()
        self.setDMPEnabled(True)
        
        self._calibrate()
        
        
    def stop(self):
    
        self.setDMPEnabled(False)
        self.setSleepEnabled(True)
        

    def cleanup(self):
        self.stop()        
        super().cleanup()
        
