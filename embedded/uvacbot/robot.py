'''
Created on 17 ago. 2019

@author: david
'''
from pyb import LED, Switch
from uasyncio import get_event_loop, sleep_ms as ua_sleep_ms
from utime import sleep_ms as utime_sleep_ms
from uvacbot.ui.heartbeat import Heartbeat

from micropython import schedule
from uvacbot.ui.bicolor_led_matrix import BiColorLedMatrix


class Robot(object):
    '''
    Handles the common objects, launches activities and keeps them running
    '''

    _ledMatrix=None
    

    def __init__(self):
        '''
        Constructor
        '''
        
        self._heartbeatLed = LED(1)
        self._heartbeat = Heartbeat(self._heartbeatLed)
        self._running = False
        self._activity = None
        
        self._loop = get_event_loop()
        
        
    def getLedMatrix(self):
        
        if self._ledMatrix == None:
            #TODO: 20200511 DPM Get I2C channel from settings
            self._ledMatrix = BiColorLedMatrix(1)
            self._ledMatrix.start()
            #TODO: 20200511 DPM Get default dim from settings
            self._ledMatrix.setDim(0x8)
        
        return self._ledMatrix

        
    def setActivity(self, activity):
        
        self._activity = activity
        self._activity.setDeviceProvider(self)
        
        return self
    
    
    def run(self):
        '''
        Runs the execution of the activity 
        '''
        
        ledMatrix = self.getLedMatrix()
        ledMatrix.updateDisplayFromRows(greenRows=bytes([0xff]*8))
        utime_sleep_ms(500)
        ledMatrix.updateDisplayFromRows(redRows=bytes([0xff]*8))
        utime_sleep_ms(500)
        ledMatrix.updateDisplayFromRows(bytes([0xff]*8), bytes([0xff]*8))
        utime_sleep_ms(500)
        ledMatrix.displayOff()
        ledMatrix.clear()
        
        self._running = True
        Switch().callback(self._toggleActivity)
        
        self._heartbeat.setState(Heartbeat.States.Waiting)        
        self._loop.create_task(self._heartbeat.run())
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
        
    
    def _runActivity(self):
        
        self._heartbeat.setState(Heartbeat.States.Active)
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
    