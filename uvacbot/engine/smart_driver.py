'''
Created on 11 mar. 2020

@author: David
'''
from uvacbot.engine.driver import Driver
from uvacbot.stabilization.pid import PidCoroutine
from uvacbot.io.input_capture import InputCapture
from math import pi

class SmartDriver(Driver):
    '''
    Probably obsolete!
    Drives motors using a PID stabilization algorithm
    '''
    
    PID_FREQ = 50 # Hz
    PID_RANGE = 3
    
    TARGET_MIN = 20.0
    TARGET_MAX = 50.0
    TARGET_DIFF = (TARGET_MAX - TARGET_MIN) / 100.0
    
    DEFAULT_LPF_ALPHA = 0.3
        
    
    def __init__(self, leftMotor, leftIcTimerId, leftIcPin, rightMotor, rightIcTimerId, rightIcPin):
        '''
        Constructor
        
        @param leftMotor: The left motor
        @param leftIcTimerId: The id-number of the timer for input-capturing on the left motor
        @param leftIcPin: The pin where the capture of pulses on the left motor will be performed
        @param rightIcTimerId: The id-number of the timer for input-capturing on the right motor
        @param rightIcPin: The pin where the capture of pulses on the right motor will be performed
        '''
        
        Driver.__init__(self, leftMotor, rightMotor)
        
        self._lpfAlpha = SmartDriver.DEFAULT_LPF_ALPHA
        
        self._leftThrottle = 0.0
        self._rightThrottle = 0.0
        
        self._leftTimer = InputCapture(leftIcTimerId, leftIcPin)
        self._rightTimer = InputCapture(rightIcTimerId, rightIcPin)
        
        
        self._pidInputValues = [0.0]*SmartDriver.PID_RANGE
        
        self._pid = PidCoroutine(SmartDriver.PID_RANGE, self._readPidInput, self._setPidOutput, "SmartDriver-PID")
        self._pid.setProportionalConstants([0.0]*SmartDriver.PID_RANGE)
        self._pid.setIntegralConstants([0.0]*SmartDriver.PID_RANGE)
        self._pid.setDerivativeConstants([0.0]*SmartDriver.PID_RANGE)
        self._pid.setModulus([0.0, 0.0, 2*pi])
        
        self._mpu = None

    
    def start(self):
        
        if self._mpu != None:
            self._mpu.start()
        
        Driver.start(self)
        
        self._pid.init(SmartDriver.PID_FREQ)
        self._pid.setTargets([0.0]*SmartDriver.PID_RANGE)
        
    
    def setPidConstants(self, kp, ki, kd):
        '''
        Set the constants for the underlying PID-algorithm
        
        @param kp: Proportional constant
        @param ki: Integral constant
        @param kd: Derivative constant
        @return The instance of the current object
        '''
        
        self._pid.setProportionalConstants(kp).setIntegralConstants(ki).setDerivativeConstants(kd)
        
        return self
    
    
    def setLpfAlphaConstant(self, lpfAlpha):
        '''
        Set the constant for the low pass filter of the wheels motion sensor
        The filter is implemented as V[n] = V[n-1] + a * (I[n] - V[n-1])
        Where V is the filtered value and I is the input value from sensor
        
        @param lpfAlpha: The low pass filter constant
        @return The object itself
        '''
        
        self._lpfAlpha = lpfAlpha
        
        return self
    
    
    def setMotionSensor(self, mpu):
        '''
        @param mpu: motion process unit
        @return The object itself
        '''
        
        self._mpu = mpu
        
        return self

        
    def cleanup(self):
        '''
        Releases and finishes all used resources
        '''
        
        self._pid.stop()
        self._leftTimer.cleanup()
        self._rightTimer.cleanup()
        if self._mpu != None:
            self._mpu.cleanup()
        Driver.cleanup(self)
        
        
    def _setThrottles(self, leftThrottle, rightThrottle):
        '''
        Sets the throttles
        
        @param leftThrottle: Throttle of the left motor
        @param rightThrottle: Throttle of the right motor 
        '''
        
        self._leftThrottle = leftThrottle
        self._rightThrottle = rightThrottle
        
        leftTarget = SmartDriver.TARGET_MIN + abs(self._leftThrottle) * SmartDriver.TARGET_DIFF if leftThrottle != 0 else 0
        rightTarget = SmartDriver.TARGET_MIN + abs(self._rightThrottle) * SmartDriver.TARGET_DIFF if rightThrottle != 0 else 0
        self._pid.setTarget(0, leftTarget)
        self._pid.setTarget(1, rightTarget)
        

    def _readMotorPidInput(self, timer, value, throttle):
        '''
        Reads the input value of a motor for the PID algorithm
        
        @param timer: Input-capture timer
        @param value: Previously read value
        @param throttle: Throttle requested
        @return: Frequency of the motor's step-holes or zero if the throttle is also zero
        '''

        if throttle != 0:
            
            cap = timer.capture()
            numTry = 5
            while cap == 0 and numTry != 0:
                cap = timer.capture()
                numTry -= 1
        
            currentValue = 1e6/cap if cap != 0 else 0
            value +=  self._lpfAlpha * (currentValue - value)
            
        else:
            value = 0
        
        return value
    
    
    def _readPidInput(self):
        '''
        Reads the input values for the PID algorithm
        '''
        
        self._pidInputValues[0] = self._readMotorPidInput(self._leftTimer, self._pidInputValues[0], self._leftMotor.getThrottle())
        self._pidInputValues[1] = self._readMotorPidInput(self._rightTimer, self._pidInputValues[1], self._rightMotor.getThrottle())
        self._pidInputValues[2] = self._mpu.readAngles()[2] if self._mpu != None else 0.0
    
        print("T: {0}".format(self._pid.getTargets()))
        print("I: {0}".format(self._pidInputValues))
    
        return self._pidInputValues

    
    @staticmethod
    def _setMotorPidOutput(motor, throttle, timer, output):
        '''
        Sets the output from the PID algorithm on a motor
        
        @param motor: Motor to set
        @param throttle: Requested throttle to determine the direction of the motor
        @param timer: It will be reset in case of stopping motor
        @param ouput: Output returned by the PID algorithm
        '''
        
        if throttle != 0:            
            motor.setAbsThrottle(output, throttle < 0)
        else:
            motor.stop()
            timer.reset()
                
    
    def _setPidOutput(self, output):
        '''
        Sets the PID output
        
        @param output: The output of the PID algorithm
        '''
        
        print("O: {0}".format(output))
        
        SmartDriver._setMotorPidOutput(self._leftMotor, self._leftThrottle, self._leftTimer, output[0])
        SmartDriver._setMotorPidOutput(self._rightMotor, self._rightThrottle, self._rightTimer, output[1])
        
        if self.getMode() == Driver.MODE_DRIVE:
            self.setDirection(output[2])
        
    
    def setMode(self, mode):
        
        Driver.setMode(self, mode)
        
        if self._mpu != None:
            if mode == Driver.MODE_DRIVE:
                self._pid.unlockIntegral(2)
                self._pid.setTarget(2, self._mpu.readAngles()[2])
                
            else:
                self._pid.lockIntegral(2)
