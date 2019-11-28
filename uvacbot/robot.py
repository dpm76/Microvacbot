'''
Created on 17 ago. 2019

@author: david
'''
from pyb import LED, Switch
from uasyncio import get_event_loop, sleep_ms as ua_sleep_ms
from utime import sleep_ms as utime_sleep_ms
from uvacbot.ui.heartbeat import Heartbeat


class Robot(object):
    '''
    Handles the common objects, launches activities and keeps them running
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
        self._heartbeatLed = LED(1)
        self._heartbeat = Heartbeat(self._heartbeatLed)
        self._running = False
        self._activity = None
        
        
    def setActivity(self, activity):
        
        self._activity = activity
        
        return self
    
    
    def run(self):
        '''
        Runs the execution of the activity 
        '''
        
        self._running = True
        Switch().callback(self._toggleActivity)
        
        loop = get_event_loop()
        self._heartbeat.setState(Heartbeat.States.Waiting)        
        loop.create_task(self._heartbeat.run())
        loop.run_until_complete(self._keepRunning())
        loop.close()        
    
    
    def finish(self):
        '''
        finalizes the execution 
        '''
        
        self._running = False
        
    
    def cleanup(self):
        '''
        Finalizes and releases the used resources 
        '''
        
        Switch().callback(None)
        self._heartbeatLed.off()
        if self._activity != None:
            
            self._activity.cleanup()
        
    
    def _runActivity(self):
        
        self._heartbeat.setState(Heartbeat.States.Active)
        if self._activity != None:
            self._activity.start()

        
    def _stopActivity(self):
        
        self._heartbeat.setState(Heartbeat.States.Waiting)
        if self._activity != None:
            self._activity.stop()        
        
    
    def _toggleActivity(self):
        
        # First at all try to debounce
        utime_sleep_ms(100)
        if Switch().value():
            if self._activity == None or self._activity.isRunning():
                
                self._stopActivity()
                self.finish()
            
            else:
                
                self._runActivity()
    
    
    async def _keepRunning(self):
        '''
        Let execute the activity until end request
        '''
        
        while self._running:
            await ua_sleep_ms(500)
    