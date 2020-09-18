'''
Created on 26 ago. 2019

@author: David
'''
from pyb import Timer
from uasyncio import sleep_ms, get_event_loop
from utime import ticks_us, ticks_diff
from uvacbot.modular_math import modularDiff


class Pid(object):
    '''
    Proportional Integrative Derivative stabilizer
    '''

    def __init__(self, length, readInputDelegate, setOutputDelegate, pidName = ""):
        '''
        Constructor
        
        @param length: Number of items to stabilize
        @param readInputDelegate: Method to gather current values.
         Must return an array with the same number of items to stabilize
        @param setOutputDelegate: Delegate's param is an array with the values to react,
         one for each item to stabilize. 
        @param pidName: (optional) Name to identify the PID-thread among other ones.
        '''
        
        self._pidName = pidName
        
        self._targets = [0.0] * length        
        
        self._integrals = [0.0] * length
        self._lastErrors = [0.0] * length
        self._outputArray = [0.0] * length
        
        self._previousTime = 0        
        
        self._kp = [0.0] * length
        self._ki = [0.0] * length
        self._kd = [0.0] * length
        
        self._readInput = readInputDelegate
        self._setOutput = setOutputDelegate
    
        self._isRunning = False
        
        self._length = length
        
        self._integralLocked = [False] * length
        
        self._modulus = [0.0] * length
        
    
    def setProportionalConstants(self, kpMatrix):
        '''
        @param kpMatrix: Proportional constant array. One for each item to stabilize
        '''
        
        if self._length == len(kpMatrix):
            self._kp = kpMatrix            
        else:
            raise Exception("Wrong matrix length")
        
        return self
    
    
    def setIntegralConstants(self, kiMatrix):
        '''
        @param kiMatrix: Integral constant array. One for each item to stabilize
        '''
        
        if self._length == len(kiMatrix):
            self._ki = kiMatrix
        else:
            raise Exception("Wrong matrix length")
        
        return self
        
    
    def setDerivativeConstants(self, kdMatrix):
        '''
        @param kdMatrix: Derivative constant array. One for each item to stabilize
        '''
        
        if self._length == len(kdMatrix):
            self._kd = kdMatrix
        else:
            raise Exception("Wrong matrix length")
        
        return self
    
    
    def setModulus(self, modulus):
        '''
        Set modulus vector for error calculation.
        In case the modulus is not required for any dimension, just set as 0 
        '''
        
        self._modulus = modulus
    
    
    def getProportionalConstants(self):
        '''
        @return: Proportional constants array
        '''
        
        return self._kp
    
    
    def getIntegralConstants(self):
        '''
        @return: Integral constants array
        '''

        return self._ki
    
    
    def getDerivativeConstants(self):
        '''
        @return: Derivative constants array
        '''

        return self._kd
    
        
    def _calculate(self):
        '''
        Performs the stabilization
        '''
        
        currentValues = self._readInput()        
        currentTime = ticks_us()
        dt = ticks_diff(currentTime, self._previousTime)
        
        for i in range(self._length):
            
            if self._modulus[i] != 0.0:
                error = modularDiff(self._targets[i], currentValues[i], self._modulus[i])
            else:
                error = self._targets[i] - currentValues[i]
                        
            #Proportional stabilization
            pPart = self._kp[i] * error
            
            #Integral stabilization
            if not self._integralLocked[i]:
                self._integrals[i] += error * dt
            iPart = self._ki[i] * self._integrals[i]
            
            #Derivative stabilization
            dPart = self._kd[i] * (error - self._lastErrors[i]) / dt            
            self._lastErrors[i] = error
            
            #Join partial results
            self._outputArray[i] = pPart + iPart + dPart

        self._previousTime = currentTime
        self._setOutput(self._outputArray)
    
    
    def setTarget(self, index, target):
        '''
        Sets target for any item
        
        @param index: Item to change
        @param target: Value to reach
        '''
        
        self._targets[index] = target
        
    
    def setTargets(self, targets):
        '''
        Sets targets
        @param targets: Array with the targets to reach. One for each item to stabilize.
        '''
        
        self._targets = targets
        
        
    def getTarget(self, index):
        '''
        Gets the current target for an item
        
        @param index: Item index
        @return: Current target
        '''
        
        return self._targets[index]
    
    
    def getTargets(self):
        '''
        Gets all current targets
        
        @return: Array of current targets
        '''
        
        return self._targets

    
    def lockIntegral(self, index):
        '''
        Locks the result's integral part of any item
        @param index: Item index 
        '''
        
        self._integralLocked[index] = True
        
    
    def unlockIntegral(self, index):
        '''
        Unlocks the result's integral part of any item
        @param index: Item index
        '''
        
        self._integralLocked[index] = False
        
    
    def resetIntegral(self, index):
        '''
        Sets to zero the integral of any item
        @param index: Item index
        '''
        
        self._integrals[index] = 0.0
        

    def resetIntegrals(self):
        '''
        Sets to zero all integrals
        '''
    
        length = len(self._kp)
        self._integrals = [0.0] * length
    
    
    def resetTime(self):
        '''
        Resets the time
        '''
        
        self._previousTime = ticks_us()
        
    
    def init(self, freq, initRunning=True):
        '''
        Initializes stabilization as a coroutine.
        Initializes a thread to perform calculations in background
        
        @param freq: Frequency of the stabilization. This value is ignored if period is provided
        @param initRunning: Starts stabilization immediately
        '''
        
        raise Exception("Abstract method is not implemented!")
    
    
    def stop(self):
        '''
        Stops the coroutine
        '''
        
        raise Exception("Abstract method is not implemented!")
        
        
        
class PidCoroutine(Pid):
    '''
    Implements the PID-stabilization algorithm as a coroutine
    '''    
    
    def __init__(self, length, readInputDelegate, setOutputDelegate, pidName):
        '''
        Constructor
        
        @param length: Number of items to stabilize
        @param readInputDelegate: Method to gather current values.
         Must return an array with the same number of items to stabilize
        @param setOutputDelegate: Delegate's parameter is an array with the values to react,
         one for each item to stabilize. 
        @param pidName: (optional) Name to identify the PID-thread among other ones.
        '''
        
        super().__init__(length, readInputDelegate, setOutputDelegate, pidName)
        
    
    async def _do(self, period): 
        '''
        Performs the stabilization as a coroutine
        
        @param period: Time rate as milliseconds to perform the stabilization
        '''
        
        while True:
            self.resetTime()
            await sleep_ms(period)
            while self._isRunning:
            
                self._calculate()
                await sleep_ms(period)
        
    
    def init(self, freq, initRunning=True):
        '''
        Initializes stabilization as a coroutine.
        Initializes a thread to perform calculations in background
        
        @param freq: Frequency of the stabilization. This value is ignored if period is provided
        @param initRunning: Starts stabilization immediately    
        '''
        
        # Period from frequency as milliseconds 
        period = int(1e3/freq)
        
        #Reset PID variables
        length = len(self._kp)
        self._integrals = [0.0] * length
        self._lastErrors = [0.0] * length
        
        self._isRunning = initRunning
        loop = get_event_loop()
        loop.create_task(self._do(period))
            
        
    def stop(self):
        '''
        Stops the stabilization
        '''

        self._isRunning = False
        
        
    def resume(self):
        '''
        Resumes the stabilization
        '''
        
        self._isRunning = True
        
        
    def isRunning(self):
        '''
        @return: Reports whether the PID stabilization is currently running
        '''
        
        return self._isRunning
    


class PidTimer(Pid):
    '''
    Implements the PID-stabilization algorithm as a Timer callback
    
    IMPORTANT!!! It seems it is not allowed to allocate memory within the timer callback. 
    Therefore, this class won't work.
    '''
    
    def __init__(self, timerId, length, readInputDelegate, setOutputDelegate, pidName):
        '''
        Constructor
        
        @param timerId: Timer to be used
        @param length: Number of items to stabilize
        @param readInputDelegate: Method to gather current values.
         Must return an array with the same number of items to stabilize
        @param setOutputDelegate: Delegate's parameter is an array with the values to react,
         one for each item to stabilize. 
        @param pidName: (optional) Name to identify the PID-thread among other ones.
        '''
        
        super().__init__(length, readInputDelegate, setOutputDelegate, pidName)
        
        self._timer = Timer(timerId)
        
        
    def _doCalculate(self, timer):

        print("_doCalculate")        
        self._calculate()
        
        
    def init(self, freq, initRunning=True):
        '''
        Initializes stabilization as a coroutine.
        Initializes a thread to perform calculations in background
        
        @param freq: Frequency of the stabilization. This value is ignored if period is provided
        @param initRunning: Starts stabilization immediately
        '''
        
        self._timer.init(freq=freq)
        self._timer.callback(lambda t: self._doCalculate(t))
    
    
    def stop(self):
        '''
        Stops the coroutine
        '''
        
        self._timer.callback(None)
        self._timer.deinit()
    