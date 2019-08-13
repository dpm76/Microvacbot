import pyb
import uasyncio

from uvacbot.ui.heartbeat import Heartbeat

async def killer(timespan):
    await uasyncio.sleep(timespan)


class SystemObjects(object):

    _instance = None
    
    @staticmethod
    def getInstance():
    
        if SystemObjects._instance == None:
            SystemObjects._instance = SystemObjects()
            
        return SystemObjects._instance
        
    def setHeartbeat(self, heartbeat):
    
        self._heartbeat = heartbeat
        
        return self
        
        
    def getHeartbeat(self):
   
        return self._heartbeat
            

def nextSystemState():
    
    heartbeat = SystemObjects.getInstance().getHeartbeat()
    state = heartbeat.getState()
    newState = Heartbeat.States.Active if state == Heartbeat.States.Waiting else Heartbeat.States.Waiting
    heartbeat.setState(newState)
    

def main():

    SystemObjects.getInstance().setHeartbeat(Heartbeat(pyb.LED(1)))
    s = pyb.Switch()
    s.callback(nextSystemState)
    loop = uasyncio.get_event_loop()
    loop.create_task(SystemObjects.getInstance().getHeartbeat().run())
    loop.run_until_complete(killer(10))
    loop.close()
    s.callback(None)
    
if __name__ == '__main__':
    main()
    