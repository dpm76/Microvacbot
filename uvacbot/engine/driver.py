import machine
import pyb
from stm import mem32, TIM_SMCR, TIM_CCER
from uvacbot.engine.pid import PidCoroutine


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
        
        self.stop()

    
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
    PID_KP = 0.7
    PID_KI = 0.0000001
    PID_KD = 0.00000012
    
    TARGET_MIN = 20.0
    TARGET_MAX = 50.0
    TARGET_DIFF = (TARGET_MAX - TARGET_MIN) / 100.0
    
    LPF_ALPHA = 0.3

    @staticmethod
    def _initIcTimer(timerId, timerAddr, pin):
        '''
        Inits a input-capture timer
        
        @param timerId: Id-number of the timer
        @param timerAddr: Memory address of the timer
        @param pin: Pin where the capture will be performed
        @return: A pair (timer, channel)
        '''
    
        ictimer = pyb.Timer(timerId, prescaler=(machine.freq()[0]//1000000)-1, period=0xffff)
        icchannel = ictimer.channel(1, pyb.Timer.IC, pin=pin, polarity=pyb.Timer.FALLING)
        icchannel.capture(0)
        
        mem32[timerAddr + TIM_SMCR] = 0
        mem32[timerAddr + TIM_SMCR] = (mem32[timerAddr + TIM_SMCR] & 0xfffe0000) | 0x54
        mem32[timerAddr + TIM_CCER] = 0b1001
        
        return (ictimer, icchannel)

    
    def __init__(self, leftMotor, leftIcTimerId, leftIcTimerAddr, leftIcPin, rightMotor, rightIcTimerId, rightIcTimerAddr, rightIcPin):
        '''
        Constructor
        
        @param leftMotor: The left motor
        @param leftIcTimerId: The id-number of the timer for input-capturing on the left motor
        @param leftIcTimerAddr: The memory address of the timer for input-capturing on the left motor
        @param leftIcPin: The pin where the capture of pulses on the left motor will be performed
        @param rightIcTimerId: The id-number of the timer for input-capturing on the right motor
        @param rightIcTimerAddr: The memory address of the timer for input-capturing on the right motor
        @param rightIcPin: The pin where the capture of pulses on the right motor will be performed
        '''
        
        super().__init__(leftMotor, rightMotor)
        
        self._leftThrottle = 0.0
        self._rightThrottle = 0.0
        
        self._leftTimer, self._leftIcChannel = SmartDriver._initIcTimer(leftIcTimerId, leftIcTimerAddr, leftIcPin)
        self._rightTimer, self._rightIcChannel = SmartDriver._initIcTimer(rightIcTimerId, rightIcTimerAddr, rightIcPin)
        
        self._pidInputValues = [0.0]*2 
        
        self._pid = PidCoroutine(2, self._readPidInput, self._setPidOutput, "SmartDriver-PID")
        self._pid.setProportionalConstants([SmartDriver.PID_KP]*2)
        self._pid.setIntegralConstants([SmartDriver.PID_KI]*2)
        self._pid.setDerivativeConstants([SmartDriver.PID_KD]*2)
        self._pid.init(SmartDriver.PID_FREQ)
        self._pid.setTargets([0.0]*2)
        
        
    def cleanup(self):
        '''
        Releases and finishes all used resources
        '''
        
        self._pid.stop()
        self._leftTimer.deinit()
        self._rightTimer.deinit()
        super().cleanup()
        
        
    def _setThrottles(self, leftThrottle, rightThrottle):
        '''
        Sets the throttles
        
        @param leftThrottle: Throttle of the left motor
        @param rightThrottle: Throttle of the right motor 
        '''
        
        self._leftThrottle = leftThrottle
        self._rightThrottle = rightThrottle
        
        leftTarget = SmartDriver.TARGET_MIN + abs(self._leftThrottle) * SmartDriver.TARGET_DIFF
        rightTarget = SmartDriver.TARGET_MIN + abs(self._rightThrottle) * SmartDriver.TARGET_DIFF
        self._pid.setTargets([leftTarget, rightTarget])
        
    
    @staticmethod
    def _readMotorPidInput(icChannel, value, throttle):
        '''
        Reads the input value of a motor for the PID algorithm
        
        @param icChannel: Channel to be read
        @param value: Previously read value
        @param throttle: Throttle requested
        @return: Frequency of the motor's step-holes or zero if the throttle is also zero
        '''

        if throttle != 0:
            
            cap = icChannel.capture()
            numTry = 5
            while cap == 0 and numTry != 0:
                cap = icChannel.capture()
                numTry -= 1
        
            currentValue = 1e6/cap if cap != 0 else 0
            value +=  SmartDriver.LPF_ALPHA * (currentValue - value)
            
        else:
            value = 0
        
        return value
    
    
    def _readPidInput(self):
        '''
        Reads the input values for the PID algorithm
        '''
        
        self._pidInputValues[0] = SmartDriver._readMotorPidInput(self._leftIcChannel, self._pidInputValues[0], self._leftThrottle)
        self._pidInputValues[1] = SmartDriver._readMotorPidInput(self._rightIcChannel, self._pidInputValues[1], self._rightThrottle)
    
        return self._pidInputValues

    
    @staticmethod
    def _setMotorPidOutput(motor, throttle, output):
        '''
        Sets the output from the PID algorithm on a motor
        
        @param motor: Motor to set
        @param throttle: Requested throttle to determine the direction of the motor
        @param ouput: Output returned by the PID algorithm
        '''
        
        if throttle != 0:            
            motor.setAbsThrottle(output, throttle < 0)
        else:
            motor.stop()
                
    
    def _setPidOutput(self, output):
        '''
        Sets the PID output
        
        @param output: The ouput of the PID algorithm
        '''
        
        SmartDriver._setMotorPidOutput(self._leftMotor, self._leftThrottle, output[0])
        SmartDriver._setMotorPidOutput(self._rightMotor, self._rightThrottle, output[1])
        
    