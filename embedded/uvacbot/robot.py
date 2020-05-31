'''
Created on 17 ago. 2019

@author: david
'''
from micropython import schedule
from pyb import LED, Switch, Pin
from uasyncio import get_event_loop, sleep_ms as ua_sleep_ms
from utime import sleep_ms as utime_sleep_ms
from uvacbot.ui.bicolor_led_matrix import BiColorLedMatrix
from uvacbot.ui.button import Button
from uvacbot.ui.buzzer import Buzzer, Sequencer, E, S, Q, H
from uvacbot.ui.heartbeat import Heartbeat


class Robot(object):
    '''
    Handles the common objects, launches activities and keeps them running
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
        self._ledMatrix = None
        self._buzzer = None
        self._sequencer = None
        
        self._heartbeatLed = LED(1)
        self._heartbeat = Heartbeat(self._heartbeatLed)
        self._testUserInterface()
        self._running = False
        self._activity = None
        self._activities = []
        self._activityIndex = 0
        
        self._loop = get_event_loop()
        
        
    def getLedMatrix(self):
        
        if self._ledMatrix == None:
            #TODO: 20200511 DPM Get I2C channel from settings
            self._ledMatrix = BiColorLedMatrix(1)
            self._ledMatrix.start()
            #TODO: 20200511 DPM Get default dim from settings
            self._ledMatrix.setDim(0x8)
        
        return self._ledMatrix
    
    
    def getBuzzer(self):
        
        if self._buzzer == None:
            
            #TODO: 20200526 DPM Get buzzer pin and timer-channel pair from settings
            self._buzzer = Buzzer(Pin.board.D12, 3, 1)
            
        return self._buzzer
            
            
    def getSequencer(self):
        
        if self._sequencer == None:
            
            self._sequencer = Sequencer(self.getBuzzer())
            
        return self._sequencer


    def addActivity(self, activity):
        '''
        Adds an activity to the robot
        
        @param activity: Activity
        '''
        
        self._activities += [activity]
        
        
    def _selectActivity(self, button):
        '''
        Selects the activity and sets the robot into the ready mode
        '''
        
        button.cleanup()
        
        self._activity = self._activities[self._activityIndex]
        self._activity.setDeviceProvider(self)
        
        Switch().callback(self._toggleActivity)
        
        self._heartbeat.setState(Heartbeat.States.Waiting)        
        self._loop.create_task(self._heartbeat.run())        
        
    
    def _preselectActivity(self, _):
        '''
        Preselects an activity and shows its icon
        '''
        
        self._activityIndex = (self._activityIndex + 1) % len(self._activities)
        
        iconRows = self._activities[self._activityIndex].getIconRows()
        self.getLedMatrix().updateDisplayFromRows(iconRows[0], iconRows[1])
        
    
    def run(self):
        '''
        Runs the execution of the activity 
        '''
        
        #TODO: 20200515 DPM Get the Button's pin from settings. 
        #PC13 is the Switch (a.k.a. user button) for the NUCLEO_F767ZI and NUCLEO_L476RG boards.
        #Please, check for other boards. 
        Button(Pin.cpu.C13, lowOnPress=True).setLongPressHandler(self._selectActivity).setShortPressHandler(self._preselectActivity)       
        
        self._running = True
        self._loop.run_until_complete(self._keepRunning())
        self._loop.close()
        
    
    def cleanup(self):
        '''
        Finalizes and releases the used resources 
        '''
        
        Switch().callback(None)
        self._heartbeatLed.off()
        if self._activity != None:
            
            self._activity.cleanup()
            
        if self._ledMatrix != None:
            
            self._ledMatrix.cleanup()
            
        #20200526 DPM Note that the sequencer's cleanup-method calls the buzzer's already
        if self._sequencer != None:
            
            self._sequencer.cleanup()
            
        elif self._buzzer != None:
            
            self._buzzer.cleanup()
        
    
    def _testUserInterface(self):
        
        ledMatrix = self.getLedMatrix()
        buzzer = self.getBuzzer()
        
        ledMatrix.updateDisplayFromRows(greenRows=bytes([0xff]*8))
        
        buzzer.buzz(110, E-S)
        utime_sleep_ms(S)
        buzzer.buzz(110, E-S)
        utime_sleep_ms(S)
        buzzer.buzz(880, Q-S)
        utime_sleep_ms(H+S)
        
        ledMatrix.updateDisplayFromRows([0xf0,0xf0,0xf0,0xf0,0xff,0xff,0xff,0xff], [0xff,0xff,0xff,0xff,0x0f,0x0f,0x0f,0x0f])
        
        buzzer.buzz(440, E)
        buzzer.buzz(220, E)
        buzzer.buzz(110, E+S)
        utime_sleep_ms(S)

        ledMatrix.updateDisplayFromRows(redRows=bytes([0xff]*8))

        buzzer.buzz(880, E)
        buzzer.buzz(220, E)
        buzzer.buzz(440, E+S)
        utime_sleep_ms(S)

        ledMatrix.updateDisplayFromRows(bytes([0xff]*8), bytes([0xff]*8))

        buzzer.buzz(880, Q)
        buzzer.buzz(440, H+Q)
        
        ledMatrix.displayOff()
        ledMatrix.clear()
        
    
    def _runActivity(self):
        
        self._heartbeat.setState(Heartbeat.States.Active)
        self.getLedMatrix().displayOff()
        self.getLedMatrix().clear()
        if self._activity != None:
            self._loop.create_task(self._activity.start())

        
    def _stopActivity(self):
        
        self._heartbeat.setState(Heartbeat.States.Waiting)
        if self._activity != None:
            self._loop.create_task(self._activity.stop())
            
        self._running = False
        

    def _toggleActivity(self):
        
        # First at all try to debounce
        utime_sleep_ms(100)
        if Switch().value():
            if self._activity == None or self._activity.isRunning():
                
                schedule(Robot._stopActivity, self)
            
            else:                
                
                schedule(Robot._runActivity, self)
    
    
    async def _keepRunning(self):
        '''
        Let execute the activity until end request
        '''
        
        while self._running:
            await ua_sleep_ms(500)
    