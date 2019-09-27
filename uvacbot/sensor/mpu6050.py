'''
Created on 26 sept. 2019

@author: David
'''
import utime
from uvacbot.io.i2c import I2CDevice
from uvacbot.sensor.mpu6050_def import MPU6050_DMP_CODE_SIZE, DMP_MEMORY, DMP_CONFIG, MPU6050_DMP_CONFIG_SIZE, MPU6050_CLOCK_PLL_ZGYRO, MPU6050_EXT_SYNC_TEMP_OUT_L, MPU6050_DLPF_BW_42, MPU6050_GYRO_FS_2000, DMP_UPDATES, MPU6050_RA_PWR_MGMT_1, MPU6050_PWR1_SLEEP_BIT, MPU6050_RA_BANK_SEL, MPU6050_RA_MEM_START_ADDR, MPU6050_RA_INT_PIN_CFG, MPU6050_INTCFG_I2C_BYPASS_EN_BIT, MPU6050_RA_MEM_R_W, MPU6050_RA_INT_ENABLE, MPU6050_PWR1_CLKSEL_BIT, MPU6050_PWR1_CLKSEL_LENGTH, MPU6050_RA_SMPLRT_DIV, MPU6050_RA_CONFIG, MPU6050_CFG_EXT_SYNC_SET_BIT, MPU6050_CFG_EXT_SYNC_SET_LENGTH, MPU6050_CFG_DLPF_CFG_BIT, MPU6050_CFG_DLPF_CFG_LENGTH, MPU6050_RA_GYRO_CONFIG, MPU6050_GCONFIG_FS_SEL_BIT, MPU6050_GCONFIG_FS_SEL_LENGTH, MPU6050_RA_DMP_CFG_1, MPU6050_RA_DMP_CFG_2, MPU6050_RA_XG_OFFS_TC, MPU6050_TC_OTP_BNK_VLD_BIT, MPU6050_RA_FIFO_COUNTH, MPU6050_RA_USER_CTRL, MPU6050_USERCTRL_FIFO_RESET_BIT, MPU6050_RA_MOT_THR, MPU6050_RA_ZRMOT_THR, MPU6050_RA_MOT_DUR, MPU6050_RA_ZRMOT_DUR, MPU6050_USERCTRL_FIFO_EN_BIT, MPU6050_USERCTRL_DMP_EN_BIT, MPU6050_USERCTRL_DMP_RESET_BIT, MPU6050_RA_FIFO_R_W, MPU6050_RA_INT_STATUS, DMP_PACKET_SIZE, dmpGetQuaternion, dmpGetGravity, dmpGetYawPitchRoll, MPU6050_RA_TEMP_OUT_H, MPU6050_PWR1_DEVICE_RESET_BIT, MPU6050_RA_XG_OFFS_USRH, MPU6050_RA_YG_OFFS_USRH, MPU6050_RA_ZG_OFFS_USRH


class Mpu6050(I2CDevice):
    
    def __init__(self, i2cId, address = 0x68):
        '''
        Constructor
        '''
        super().__init__(i2cId, address)


    def setSleepEnabled(self, status):
        self._writeBit(MPU6050_RA_PWR_MGMT_1, MPU6050_PWR1_SLEEP_BIT, status)
        
        
    def setMemoryBank(self, bank, prefetchEnabled = False, userBank = False):
        bank &= 0x1F
        
        if userBank:
            bank |= 0x20
        if prefetchEnabled:
            bank |= 0x40
            
        self._writeByte(MPU6050_RA_BANK_SEL, bank)
    
    
    def setMemoryStartAddress(self, address):
        self._writeByte(MPU6050_RA_MEM_START_ADDR, address)
           

    def setI2CBypassEnabled(self, enabled):
        self._writeBit(MPU6050_RA_INT_PIN_CFG, MPU6050_INTCFG_I2C_BYPASS_EN_BIT, enabled)


    def writeMemoryBlock(self, data, dataSize, bank = 0, address = 0):
        self.setMemoryBank(bank)
        self.setMemoryStartAddress(address)
        
        i = 0
        while i < dataSize:  
            self._writeByte(MPU6050_RA_MEM_R_W, data[i])
                    
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
                    self._writeByte(MPU6050_RA_INT_ENABLE, 0x32);  # single operation
                    
                    
    def setClockSource(self, source):
        self._writeBits(MPU6050_RA_PWR_MGMT_1, MPU6050_PWR1_CLKSEL_BIT, MPU6050_PWR1_CLKSEL_LENGTH, source)        


    def setIntEnabled(self, status):
        self._writeByte(MPU6050_RA_INT_ENABLE, status)        


    def setRate(self, value):
        self._writeByte(MPU6050_RA_SMPLRT_DIV, value)
        
    
    def setExternalFrameSync(self, sync):
        self._writeBits(MPU6050_RA_CONFIG, MPU6050_CFG_EXT_SYNC_SET_BIT, MPU6050_CFG_EXT_SYNC_SET_LENGTH, sync)
        
    
    def setDLPFMode(self, mode):
        self._writeBits(MPU6050_RA_CONFIG, MPU6050_CFG_DLPF_CFG_BIT, MPU6050_CFG_DLPF_CFG_LENGTH, mode)
     
    
    def setFullScaleGyroRange(self, gyroRange):
        self._writeBits(MPU6050_RA_GYRO_CONFIG, MPU6050_GCONFIG_FS_SEL_BIT, MPU6050_GCONFIG_FS_SEL_LENGTH, gyroRange)        
    
    
    def setDMPConfig1(self, config):
        self._writeByte(MPU6050_RA_DMP_CFG_1, config)        
        

    def setDMPConfig2(self, config):
        self._writeByte(MPU6050_RA_DMP_CFG_2, config)


    def setOTPBankValid(self, status):
        self._writeBit(MPU6050_RA_XG_OFFS_TC, MPU6050_TC_OTP_BNK_VLD_BIT, status)


    def setXGyroOffsetUser(self, value):
        self._writeWordHL(MPU6050_RA_XG_OFFS_USRH, value)
        

    def setYGyroOffsetUser(self, value):
        self._writeWordHL(MPU6050_RA_YG_OFFS_USRH, value)
        

    def setZGyroOffsetUser(self, value):
        self._writeWordHL(MPU6050_RA_ZG_OFFS_USRH, value)


    def getFIFOCount(self):
        return self._readUnsignedWordHL(MPU6050_RA_FIFO_COUNTH)

    
    def resetFIFO(self):
        self._writeBit(MPU6050_RA_USER_CTRL, MPU6050_USERCTRL_FIFO_RESET_BIT, True)
        

    def setMotionDetectionThreshold(self, treshold):
        self._writeByte(MPU6050_RA_MOT_THR, treshold)
        

    def setZeroMotionDetectionThreshold(self, treshold):
        self._writeByte(MPU6050_RA_ZRMOT_THR, treshold)
    

    def setMotionDetectionDuration(self, duration):
        self._writeByte(MPU6050_RA_MOT_DUR, duration)
    

    def setZeroMotionDetectionDuration(self, duration):
        self._writeByte(MPU6050_RA_ZRMOT_DUR, duration)
    
        
    def setFIFOEnabled(self, status):
        self._writeBit(MPU6050_RA_USER_CTRL, MPU6050_USERCTRL_FIFO_EN_BIT, status)        
        

    def setDMPEnabled(self, status):
        self._writeBit(MPU6050_RA_USER_CTRL, MPU6050_USERCTRL_DMP_EN_BIT, status)
    

    def resetDMP(self):
        self._writeBit(MPU6050_RA_USER_CTRL, MPU6050_USERCTRL_DMP_RESET_BIT, True)
        

    def getFIFOBlock(self):    
        
        return self._readBlock(MPU6050_RA_FIFO_R_W, self.getFIFOCount())

    
    def getIntStatus(self):
        return self._readUnsignedByte(MPU6050_RA_INT_STATUS)


    def _dmpUpdate(self, pos):
        
        j = 0
        dmpUpdate = []
        while ((j < 4) or (j < dmpUpdate[2] + 3)):
            dmpUpdate.append(DMP_UPDATES[pos])
            j += 1
            pos += 1
        
        self.writeMemoryBlock(dmpUpdate[3:], dmpUpdate[2], dmpUpdate[0], dmpUpdate[1])
        
        return pos
    
    
    def reset(self):
        self._writeBit(MPU6050_RA_PWR_MGMT_1, MPU6050_PWR1_DEVICE_RESET_BIT, True)       
        

    def dmpInitialize(self):
        
        # Reset MPU6050
        self.reset()
        utime.sleep_ms(500) # wait after reset
        # Disable sleep mode
        self.setSleepEnabled(False)
        # get MPU hardware revision
        self.setMemoryBank(0x10, True, True) # Selecting user bank 16
        self.setMemoryStartAddress(0x06) # Selecting memory byte 6
        self.setMemoryBank(0, False, False) # Resetting memory bank selection to 0
        # Enable pass through mode
        self.setI2CBypassEnabled(True)
        # load DMP code into memory banks
        self.writeMemoryBlock(DMP_MEMORY, MPU6050_DMP_CODE_SIZE, 0, 0)
        # write DMP configuration
        self.writeDMPConfigurationSet(DMP_CONFIG, MPU6050_DMP_CONFIG_SIZE)
        # Setting clock source to Z Gyro
        self.setClockSource(MPU6050_CLOCK_PLL_ZGYRO)
        # Setting DMP and FIFO_OFLOW interrupts enabled
        self.setIntEnabled(0x12)
        # Setting sample rate to 200Hz
        self.setRate(4) # 1khz / (1 + 4) = 200 Hz [9 = 100 Hz]
        # Setting external frame sync to TEMP_OUT_L[0]
        self.setExternalFrameSync(MPU6050_EXT_SYNC_TEMP_OUT_L)
        # Setting DLPF bandwidth to 42Hz
        self.setDLPFMode(MPU6050_DLPF_BW_42)
        # Setting gyro sensitivity to +/- 2000 deg/sec
        self.setFullScaleGyroRange(MPU6050_GYRO_FS_2000)
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
        pos = self._dmpUpdate(0)
        # Writing final memory update 2/7 (function unknown)
        pos = self._dmpUpdate(pos)
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
        pos = self._dmpUpdate(pos)
        # Writing final memory update 4/7 (function unknown)
        pos = self._dmpUpdate(pos)
        # Writing final memory update 5/7 (function unknown)
        pos = self._dmpUpdate(pos)
        # Waiting for FIFO count > 2
        fifoCount = self.getFIFOCount()
        while (fifoCount < 3):
            utime.sleep_ms(1)
            fifoCount = self.getFIFOCount()
        
        # Reading FIFO data
        self.getFIFOBlock()
        
        # Writing final memory update 6/7 (function unknown)
        pos = self._dmpUpdate(pos)
        # Writing final memory update 7/7 (function unknown)
        pos = self._dmpUpdate(pos)
        # Disabling DMP (you turn it on later)
        self.setDMPEnabled(False)
        # Resetting FIFO and clearing INT status one last time
        self.resetFIFO()
        self.getIntStatus()
        
        
    def _readDmpPacket(self):
                
        self.resetFIFO()
        
        fifoCount = self.getFIFOCount()
        while fifoCount < DMP_PACKET_SIZE:
            utime.sleep_ms(1)
            fifoCount = self.getFIFOCount()
        
        packet = self.getFIFOBlock()
                     
        return packet

    
    def _calibrate(self):
        '''
        Calibrates the sensor
        '''
        utime.sleep(1)
        self.resetFIFO()
        
        #Wait for next packet
        utime.sleep_ms(1)
        packet = self._readDmpPacket()
        
        q = dmpGetQuaternion(packet)
        g = dmpGetGravity(q)
                        
        ypr = dmpGetYawPitchRoll(q, g)
        self._angleOffset = [ypr["pitch"], ypr["roll"], ypr["yaw"]]

    
    def readTemperature(self):
        
        return (self._readSignedWordHL(MPU6050_RA_TEMP_OUT_H)/340.0) + 36.53


    def readAngles(self):
        
        packet = self._readDmpPacket()       
        q = dmpGetQuaternion(packet)
        g = dmpGetGravity(q)
        
        ypr = dmpGetYawPitchRoll(q, g)        
        angles = [ypr["pitch"]-self._angleOffset[0], ypr["roll"]-self._angleOffset[1], ypr["yaw"]-self._angleOffset[2]]
        
        return angles

    
    def start(self):
        
        self._angleOffset = [0]*3
        
        self.dmpInitialize()
        self.setDMPEnabled(True)
        
        self._calibrate()


    def cleanup(self):
        
        self.setDMPEnabled(False)
        self.setSleepEnabled(True)
        super().cleanup()