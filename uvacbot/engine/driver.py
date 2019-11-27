from uvacbot.engine.pid import PidCoroutine
from uvacbot.io.input_capture import InputCapture
from math import pi


class Driver(object):
    '''
    Controls a motor set
    '''

    #Driver modes    
    MODE_DRIVE = 0
    MODE_ROTATE = 1

    #Thresholds for throttle ranges. For each range a different turning method will be used. 
    THROTTLE_RANGE_THRESHOLD_1 = 25.0
    THROTTLE_RANGE_THRESHOLD_2 = 75.0
    THROTTLE_RANGE_THRESHOLD_DIFF = THROTTLE_RANGE_THRESHOLD_2 - THROTTLE_RANGE_THRESHOLD_1 

    #Direction divisors to set the wheels spinning at different speeds in order to turn the robot.  
    DIRECTION_DIV1 = 50.0
    DIRECTION_DIV2 = 200.0

    def __init__(self, leftMotor, rightMotor):
        '''
        Constructor
        
        @param leftMotor: The left motor
        @param rightMotor: The right motor
        '''
        
        self._leftMotor = leftMotor
        self._rightMotor = rightMotor
        
        self._throttle = 0.0
        self._direction = 0.0
        
        self._mode = Driver.MODE_DRIVE
        
        
    def start(self):
        '''
        Starts the driver.
        The driver starts stopped and in drive mode
        '''
        
        self.stop()
        self.setMode(Driver.MODE_DRIVE)

    
    def stop(self):
        '''
        Stop the motors
        '''
        
        self.setMotionVector(0.0, 0.0)
        
    
    def setThrottle(self, throttle):
        '''
        Set the throttle.
        @param throttle: Throttle range is [-100, 100], where negative values mean backwards and positive ones mean forwards.        
        '''
        self.setMotionVector(throttle, self.getDirection())
        
    
    def getThrottle(self):
        '''
        Get the throttle.
        @return: Throttle range is [-100, 100], where negative values mean backwards and positive ones mean forwards.
        '''
        return self._throttle
    
    
    def setDirection(self, direction):
        '''
        Set the direction.
        @param direction: Direction range is [-100, 100], where negative values mean left and positive ones mean right.
        '''
        self.setMotionVector(self.getThrottle(), direction)
        
    
    def getDirection(self):
        '''
        Get the direction.
        @return: Direction range is [-100, 100], where negative values mean left and positive ones mean right.
        '''
        return self._direction


    def setMotionVector(self, throttle, direction):
        '''
        Set the motion vector (both, throttle and direction) directly.
        Actual effect depends on the current driving mode.
        
        @param throttle: Throttle range is [-100, 100], where negative values mean backwards and positive ones mean forwards.
        @param direction: Direction range is [-100, 100], where negative values mean left and positive ones mean right.
        '''

        self._throttle = throttle
        self._direction = direction
               
        if self._mode == Driver.MODE_DRIVE:
            
            self._setMotionVectorOnDriveMode()

        else: #Driver.MODE_ROTATE
            
            self._setMotionVectorOnRotateMode()
       


    def _setThrottles(self, leftThrottle, rightThrottle):
        '''
        Sets the throttles to motors
        
        @param leftThrottle: [-100..100] Throttle of the left motor
        @param rightThrottle: [-100..100] Throttle of the right motor
        '''
        
        if leftThrottle != 0:
            self._leftMotor.setThrottle(leftThrottle)
        else:
            self._leftMotor.stop()
            
        if rightThrottle != 0:
            self._rightMotor.setThrottle(rightThrottle)
        else:
            self._rightMotor.stop()


    def _setMotionVectorOnDriveMode(self):
        '''
        Set the motion vector on drive mode.        
        '''
            
        modThrottle = abs(self._throttle)
    
        if modThrottle < Driver.THROTTLE_RANGE_THRESHOLD_1:
            
            if self._direction >= 0.0:
                
                leftThrottle = self._throttle + self._throttle * (self._direction/Driver.DIRECTION_DIV1)
                rightThrottle = self._throttle
                
            else:
                            
                leftThrottle = self._throttle
                rightThrottle = self._throttle - self._throttle * (self._direction/Driver.DIRECTION_DIV1)
                  
        elif Driver.THROTTLE_RANGE_THRESHOLD_1 <= modThrottle < Driver.THROTTLE_RANGE_THRESHOLD_2:
            
            if self._direction >= 0.0:
                
                leftThrottle  = self._throttle + self._throttle * (self._direction/Driver.DIRECTION_DIV1) * ((Driver.THROTTLE_RANGE_THRESHOLD_2 - modThrottle) / Driver.THROTTLE_RANGE_THRESHOLD_DIFF)
                rightThrottle = self._throttle - self._throttle * (self._direction/Driver.DIRECTION_DIV2) * ((modThrottle - Driver.THROTTLE_RANGE_THRESHOLD_1) / Driver.THROTTLE_RANGE_THRESHOLD_DIFF)
                
            else:
                            
                leftThrottle =  self._throttle + self._throttle * (self._direction/Driver.DIRECTION_DIV2) * ((modThrottle - Driver.THROTTLE_RANGE_THRESHOLD_1) / Driver.THROTTLE_RANGE_THRESHOLD_DIFF)
                rightThrottle = self._throttle - self._throttle * (self._direction/Driver.DIRECTION_DIV1) * ((Driver.THROTTLE_RANGE_THRESHOLD_2 - modThrottle) / Driver.THROTTLE_RANGE_THRESHOLD_DIFF)

        else:
            
            if self._direction >= 0.0:
                
                leftThrottle = self._throttle
                rightThrottle = self._throttle - self._throttle * (self._direction/Driver.DIRECTION_DIV2)
                
            else:
                
                leftThrottle = self._throttle + self._throttle * (self._direction/Driver.DIRECTION_DIV2)
                rightThrottle = self._throttle
        
        self._setThrottles(leftThrottle, rightThrottle)        
            
            
    def _setMotionVectorOnRotateMode(self):
        '''
        Set the motion vector on rotate driving mode.        
        '''
        
        leftThrottle = self._direction
        rightThrottle = -self._direction

        self._setThrottles(leftThrottle, rightThrottle)
            
            
    def setMode(self, mode):
        '''
        Set driver mode
        
        @param mode: Driving mode. See Driver.MODE_*        
        '''
        
        if self._mode != mode:
            
            self.stop()
            self._mode = mode
    
    
    def getMode(self):
        '''
        Get current driver mode
        
        @return: Any of Driver.MODE_*
        '''
        
        return self._mode
        
        
    def cleanup(self):
        '''
        Releases the used resources
        '''

        self.stop()
        self._leftMotor.cleanup()
        self._rightMotor.cleanup()


class SmartDriver(Driver):
    '''
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
        self._pid.setTargets([leftTarget, rightTarget])
        

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
    