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
       


    def _setMotionVectorOnDriveMode(self):
        '''
        Set the motion vector on drive mode.        
        '''
        
        if self._throttle != 0.0:
            
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
                    
            self._leftMotor.setThrottle(leftThrottle)
            self._rightMotor.setThrottle(rightThrottle)
    
        else:
            
            self._leftMotor.stop()
            self._rightMotor.stop()
            
            
    def _setMotionVectorOnRotateMode(self):
        '''
        Set the motion vector on rotate driving mode.        
        '''
        
        if self._direction != 0:
        
            leftThrottle = self._direction
            rightThrottle = -self._direction
    
            self._leftMotor.setThrottle(leftThrottle)
            self._rightMotor.setThrottle(rightThrottle)
            
        else:
            
            self._leftMotor.stop()
            self._rightMotor.stop()
               
            
    def setMode(self, mode):
        '''
        Set driver mode
        
        @param mode: Driving mode. See Driver.MODE_*        
        '''
        
        if self._mode != mode:
            
            self.setNeutral()
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
