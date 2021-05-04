'''
Created on 30 mar. 2020

@author: David
'''
from micropython import const
from uasyncio import sleep_ms, sleep
from uvacbot.io.esp8266 import Connection, Esp8266
from uvacbot.ui.bicolor_led_matrix import BiColorLedMatrix, hexStringToInt
from uvacbot.ui.buzzer import Sequencer
from math import radians


class _RemoteConnection(Connection):
    
    async def onReceived(self, message):
        
        cmd = message.strip()
        if cmd != "":
            response = await self._extraObj.dispatchCommand(cmd)
            self.send("{0}\r\n".format(response))
                    

class RemoteControlledActivity(object):
    
    #TODO: 20200725 DPM Reduce memory use, in order to select network mode on run time.
    # Network mode selection doesn't fit within the L476RG-MCU's memory 
    # (128KB, but ~80KB free running Micropython+uasyncio), code shall reduce its memory consumption.
    
    #TODO: 20200624 DPM Get network options from settings
    NETWORK_AP_ENABLED = False
    NETWORK_CLIENT_MODE_ENABLED = True
    
    NETWORK_AP_SSID = "Microvacbot_AP"
    NETWORK_AP_PASSWD = ""
    NETWORK_AP_IP = "192.168.4.1"
    
    NETWORK_CLIENT_MODE_SSID = "Nenukines-Haus"
    NETWORK_CLIENT_MODE_PASSWD = "8V83QGJR773E9767"
    NETWORK_CLIENT_IP = "192.168.1.200"
    NETWORK_CLIENT_GATEWAY = "192.168.1.1"
    
    #TODO: 20200511 DPM Get throttle values from settings
    DRIVE_THROTTLE = const(80)
    SLOW_THROTTLE = const(60)
    ROTATION_THROTTLE = const(60)
    
    STATE_MATRICES = [
        [ 0,0,0,0,0x7c,0x38,0x10,0 ],
        [ 0,0x10,0x38,0x7c,0,0,0,0 ],
        [ 0,0x10,0x30,0x70,0x30,0x10,0,0 ],
        [ 0,0x8,0xc,0xe,0xc,0x8,0,0 ]
    ]
    
    EXPRESSION_DURATION = const(1000) # milliseconds
    
    EXPRESSION_MATRICES = [
        [
            None,
            [ 0,0x66,0x66,0,0x42,0x3c,0,0 ]
        ],
        [
            [ 0,0x66,0x66,0,0x18,0x24,0x18,0 ],
            [ 0,0x66,0x66,0,0,0,0,0 ]
        ],
        [
            [ 0,0,0,0,0x7e,0x18,0x18,0 ],
            [ 0,0x66,0x66,0,0x7e,0,0,0 ]
        ],        
        [
            [ 0xf,0xf,0xf,0xf,0xf0,0xf0,0xf0,0xf0 ],
            [ 0xf0,0xf0,0xf0,0xf0,0xff,0xff,0xff,0xff ]
        ]
    ]
    
    EXPRESSION_SOUNDS = [
        lambda self: self._buzzer.slide(220, 440, 200),
        lambda self: self._buzzer.buzz(110, 200),
        lambda self: self._buzzer.trill(220, 200),
        lambda self: Sequencer(self._buzzer).play("3cdeg.4b3d")
    ]
    
    def __init__(self, motion, esp):
        
        self._motion = motion
        self._motion.setRotation(RemoteControlledActivity.ROTATION_THROTTLE)
        
        self._esp = esp
        self._esp.start()
        assert self._esp.isPresent()
        #TODO: 20200511 DPM Move ESP module initialization to the robot-class
        opmode = 0
        if RemoteControlledActivity.NETWORK_AP_ENABLED:
            opmode = Esp8266.OP_MODE_AP
            
        if RemoteControlledActivity.NETWORK_CLIENT_MODE_ENABLED:
            opmode |= Esp8266.OP_MODE_CLIENT
              
        assert opmode != 0
        self._esp.setOperatingMode(opmode)
        
        #self._esp.setOperatingMode(1) #Esp8266.OP_MODE_CLIENT = 1; Esp8266.OP_MODE_AP = 2
        
        if RemoteControlledActivity.NETWORK_CLIENT_MODE_ENABLED:
         
            #TODO: 20200511 DPM Get IP configuration from settings
            self._esp.setStaIpAddress(RemoteControlledActivity.NETWORK_CLIENT_IP, RemoteControlledActivity.NETWORK_CLIENT_GATEWAY)
            #TODO: 20200916 DPM Get SSID and password from settings
            self._esp.join(RemoteControlledActivity.NETWORK_CLIENT_MODE_SSID, RemoteControlledActivity.NETWORK_CLIENT_MODE_PASSWD)
            
        if RemoteControlledActivity.NETWORK_AP_ENABLED:
              
            if RemoteControlledActivity.NETWORK_AP_PASSWD != None and RemoteControlledActivity.NETWORK_AP_PASSWD != "":
                self._esp.setAccessPointConfig(RemoteControlledActivity.NETWORK_AP_SSID, RemoteControlledActivity.NETWORK_AP_PASSWD, security=Esp8266.SECURITY_WPA_WPA2)
            else:
                self._esp.setAccessPointConfig(RemoteControlledActivity.NETWORK_AP_SSID)
            #TODO 20200725 DPM Get IP Address on AP-mode from settings
            self._esp.setApIpAddress(RemoteControlledActivity.NETWORK_AP_IP, RemoteControlledActivity.NETWORK_AP_IP)
         
        self._isrunning = False
        
        self._ledMatrix = None
        self._buzzer = None
        
            
    async def start(self):
        '''
        Starts the activity
        '''
        
        self._isrunning = True
        self._esp.initServer(_RemoteConnection, self)
    
    
    async def stop(self):
        '''
        Stops the activity
        '''
        
        self._esp.stopServer()
        self._isrunning = False
        
        
    def setDeviceProvider(self, deviceProvider):
        '''
        Sets the object which provides the devices
        
        @param deviceProvider: The device provider
        '''
        
        self._ledMatrix = deviceProvider.getLedMatrix()
        self._buzzer = deviceProvider.getBuzzer()
        
        
    def getIconRows(self):
        '''
        @return: The icon of this activity
        '''
        
        return (None, [ 0,0x3c,0x42,0x18,0x24,0,0x18,0 ])
    
    
    def cleanup(self):
        '''
        Finalizes and releases the used resources
        '''
        
        self._motion.stop()
        
    
    def isRunning(self):
        '''
        Reports the activity is currently running
        @return: True or False depending the activity is running or not
        '''
        
        return self._isrunning
    
    
    async def _dispatchExpression(self, params):
        
        if len(params) > 0:
            
            exprId = int(params[0])
            if exprId < len(RemoteControlledActivity.EXPRESSION_MATRICES):
            
                expressionMatrix = RemoteControlledActivity.EXPRESSION_MATRICES[exprId]
                self._ledMatrix.updateDisplayFromRows(expressionMatrix[0], expressionMatrix[1])
                RemoteControlledActivity.EXPRESSION_SOUNDS[exprId](self)
                await sleep_ms(RemoteControlledActivity.EXPRESSION_DURATION)
                self._ledMatrix.displayOff()
        
    
    def _dispatchLedMatrixCmd(self, params):
        
        if len(params) > 1:
            
            redRows = []
            greenRows = []
            
            red = 0
            green = 0
            
            for row in range(8):
                
                charIndex = row*2
                red = hexStringToInt(params[0][charIndex:charIndex+2]) if len(params[0]) >= charIndex+2 else red
                green = hexStringToInt(params[1][charIndex:charIndex+2]) if len(params[1]) >= charIndex+2 else green
                
                redRows += [red]
                greenRows += [green]
                
            if len(params) > 2:
                
                if params[2] == "1":
                    blinkMode = BiColorLedMatrix.BLINK_1HZ
                elif params[2] == "2":
                    blinkMode = BiColorLedMatrix.BLINK_2HZ
                elif params[2] == "H":
                    blinkMode = BiColorLedMatrix.BLINK_HALF_HZ
                else:
                    blinkMode = BiColorLedMatrix.BLINK_OFF
            else:
                blinkMode = BiColorLedMatrix.BLINK_OFF
                
            self._ledMatrix.updateDisplayFromRows(redRows, greenRows, blinkMode)
        
        else:
            
            self._ledMatrix.displayOff()
            self._ledMatrix.clear()
            
            
    def _dispatchBuzzCmd(self, params):
        
        if len(params) > 1:
            
            freq = int(params[0])
            playtime = int(params[1])
            
            self._buzzer.buzz(freq, playtime)
            

    def _stopAndClear(self):
        
        self._motion.stop()
        self._ledMatrix.displayOff()
        self._ledMatrix.clear()
        

    async def _sleepAndStop(self, params):
        
        if params != None and len(params) != 0:
                    
            delay = int(params[0])
            
            if len(params) > 1 and params[1].lower() == 's':
                
                await sleep(delay)
            
            else:
                
                await sleep_ms(delay)
                
            self._stopAndClear()
        
            
    async def _dispatchForwardsCmd(self, params):
        
        self._motion.setThrottle(RemoteControlledActivity.DRIVE_THROTTLE)
        self._motion.goForwards()
        self._ledMatrix.updateDisplayFromRows(greenRows=RemoteControlledActivity.STATE_MATRICES[0])
        await self._sleepAndStop(params)
        
        
    async def _dispatchBackwardsCmd(self, params):
        
        self._motion.setThrottle(RemoteControlledActivity.SLOW_THROTTLE)
        self._motion.goBackwards()
        self._ledMatrix.updateDisplayFromRows(redRows=RemoteControlledActivity.STATE_MATRICES[1])
        await self._sleepAndStop(params)
        
        
    async def _dispatchTurnLeftCmd(self, params):
    
        self._motion.turnLeft()
        #The led-matrix is placed with its base line to the forward direction, therefore left and right are reversed 
        self._ledMatrix.updateDisplayFromRows(RemoteControlledActivity.STATE_MATRICES[3],RemoteControlledActivity.STATE_MATRICES[3]);
        await self._sleepAndStop(params)
    
    
    async def _dispatchTurnRightCmd(self, params):
        
        self._motion.turnRight()
        self._ledMatrix.updateDisplayFromRows(RemoteControlledActivity.STATE_MATRICES[2],RemoteControlledActivity.STATE_MATRICES[2])
        await self._sleepAndStop(params)
        
        
    async def _dispatchTurnToCmd(self, params):
        
        if params != None and len(params) >= 2:
            
            angle = float(params[0]) if params != "" else 0.0
            unit = params[1].lower()
            
            if unit == "d": #the angle comes as degrees
                angleRad = radians(angle)
            else: #the angle comes as radians
                angleRad = angle
            
            await self._motion.turnTo(angleRad)
            
    
    async def _dispatchTurnCmd(self, params):
        
        if params != None and len(params) >= 2:
            
            angle = float(params[0]) if params != "" else 0.0
            unit = params[1].lower()
            
            if unit == "d": #the angle comes as degrees
                angleRad = radians(angle)
            else: #the angle comes as radians
                angleRad = angle
            
            await self._motion.turn(angleRad)
            
    
    async def _dispatchForwardsToCmd(self, params):
        
        if params != None and len(params) >= 1:
            
            #TODO: 20210305 DPM Only steps are currently implemented
            await self._motion.goForwardsTo(int(params[0]))
    
    
    async def _dispatchBackwardsToCmd(self, params):
        
        if params != None and len(params) >= 1:
            
            #TODO: 20210305 DPM Only steps are currently implemented
            await self._motion.goBackwardsTo(int(params[0]))
        
        
    def _dispatchStopCmd(self, params):
        
        self._stopAndClear()        
                
    
    async def dispatchCommand(self, message):
        
        message = message.strip()
        
        if message != "":
            
            cmdArgs = message.split(':')
            cmdCode = cmdArgs[0].upper()
            cmdParams = cmdArgs[1:]
            
            try:
            
                if cmdCode == "FWD":
                    await self._dispatchForwardsCmd(cmdParams)
                    
                elif cmdCode == "BAK":
                    await self._dispatchBackwardsCmd(cmdParams)
                    
                elif cmdCode == "TLE":
                    await self._dispatchTurnLeftCmd(cmdParams)
                    
                elif cmdCode == "TRI":
                    await self._dispatchTurnRightCmd(cmdParams)
                    
                elif cmdCode == "TRT":
                    await self._dispatchTurnToCmd(cmdParams)
                    
                elif cmdCode == "TRN":
                    await self._dispatchTurnCmd(cmdParams)
                    
                elif cmdCode == "FWT":
                    await self._dispatchForwardsToCmd(cmdParams)
                
                elif cmdCode == "BKT":
                    await self._dispatchBackwardsToCmd(cmdParams)
                    
                elif cmdCode.startswith("STO"):
                    self._dispatchStopCmd(cmdParams)
                    
                elif cmdCode.startswith("EXP"):
                    await self._dispatchExpression(cmdParams)
                    
                elif cmdCode.startswith("LMX"):
                    self._dispatchLedMatrixCmd(cmdParams)
                    
                elif cmdCode.startswith("BUZ"):
                    self._dispatchBuzzCmd(cmdParams)
                    
                else:
                    raise Exception("Unknown command")
                
                response = "{0}:OK".format(cmdCode)
            
            except Exception as ex:
                
                self._stopAndClear()
                response = "{0}:ERROR:{1}".format(cmdCode, str(ex).replace(":",";"))
                
            return response
