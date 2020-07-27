'''
Created on 30 mar. 2020

@author: David
'''
from micropython import const
from utime import sleep_ms
from uvacbot.io.esp8266 import Connection, Esp8266
from uvacbot.ui.bicolor_led_matrix import BiColorLedMatrix, hexStringToInt


class _RemoteConnection(Connection):
    
    async def onReceived(self, message):
        
        cmd = message.strip()
        if cmd != "":
            self._extraObj.dispatchCommand(cmd)
                    

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
        
        [
            0b00000000,
            0b00000000,
            0b00000000,
            0b00000000,
            0b01111100,
            0b00111000,
            0b00010000,
            0b00000000
        ],
        [
            0b00000000,
            0b00010000,
            0b00111000,
            0b01111100,
            0b00000000,
            0b00000000,
            0b00000000,
            0b00000000
        ],
        [
            0b00000000,
            0b00010000,
            0b00110000,
            0b01110000,
            0b00110000,
            0b00010000,
            0b00000000,
            0b00000000
        ],
        [
            0b00000000,
            0b00001000,
            0b00001100,
            0b00001110,
            0b00001100,
            0b00001000,
            0b00000000,
            0b00000000
        ]
    ]
    
    EXPRESION_MATRICES = [
        [
            None,
            [
                0b00000000,
                0b01100110,
                0b01100110,
                0b00000000,
                0b01000010,
                0b00111100,
                0b00000000,
                0b00000000
            ]
        ],
        [
            [
                0b00000000,
                0b01100110,
                0b01100110,
                0b00000000,
                0b00011000,
                0b00100100,
                0b00011000,
                0b00000000
            ],
            [
                0b00000000,
                0b01100110,
                0b01100110,
                0b00000000,
                0b00000000,
                0b00000000,
                0b00000000,
                0b00000000
            ]
        ],
        [
            [
                0b00000000,
                0b00000000,
                0b00000000,
                0b00000000,
                0b01111110,
                0b00011000,
                0b00011000,
                0b00000000
            ],
            [
                0b00000000,
                0b01100110,
                0b01100110,
                0b00000000,
                0b01111110,
                0b00000000,
                0b00000000,
                0b00000000
            ]
        ],        
        [
            [
                0b00001111,
                0b00001111,
                0b00001111,
                0b00001111,
                0b11110000,
                0b11110000,
                0b11110000,
                0b11110000
            ],
            [
                0b11110000,
                0b11110000,
                0b11110000,
                0b11110000,
                0b11111111,
                0b11111111,
                0b11111111,
                0b11111111
            ]
        ]
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
         
            self._esp.join(RemoteControlledActivity.NETWORK_CLIENT_MODE_SSID, RemoteControlledActivity.NETWORK_CLIENT_MODE_PASSWD)
            #TODO: 20200511 DPM Get IP configuration from settings
            self._esp.setStaIpAddress(RemoteControlledActivity.NETWORK_CLIENT_IP, RemoteControlledActivity.NETWORK_CLIENT_GATEWAY)
            
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
        
        self._isrunning = True
        self._esp.initServer(_RemoteConnection, self)
    
    
    async def stop(self):
        
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
        
        return (None, [            
            0b00000000,
            0b00111100,
            0b01000010,
            0b00011000,
            0b00100100,
            0b00000000,
            0b00011000,
            0b00000000
            ])
    
    
    def cleanup(self):
        
        self._motion.stop()
        
    
    def isRunning(self):
        
        return self._isrunning
    
    
    def _dispatchExpression(self, cmd):
        
        params = cmd.split(':')
        if len(params) == 2:
            
            exprId = int(params[1])
            if exprId < len(RemoteControlledActivity.EXPRESION_MATRICES):
            
                self._ledMatrix.updateDisplayFromRows(RemoteControlledActivity.EXPRESION_MATRICES[exprId][0], RemoteControlledActivity.EXPRESION_MATRICES[exprId][1])
                sleep_ms(1000)
                self._ledMatrix.displayOff()
        
    
    def _dispatchLedMatrixCmd(self, cmd):
        
        params = cmd.split(':')
        
        if len(params) > 2:
            
            redRows = []
            greenRows = []
            
            red = 0
            green = 0
            
            for row in range(8):
                
                charIndex = row*2
                red = hexStringToInt(params[1][charIndex:charIndex+2]) if len(params[1]) >= charIndex+2 else red
                green = hexStringToInt(params[2][charIndex:charIndex+2]) if len(params[2]) >= charIndex+2 else green
                
                redRows += [red]
                greenRows += [green]
                
            if len(params) > 3:
                
                if params[3] == "1":
                    blinkMode = BiColorLedMatrix.BLINK_1HZ
                elif params[3] == "2":
                    blinkMode = BiColorLedMatrix.BLINK_2HZ
                elif params[3] == "H":
                    blinkMode = BiColorLedMatrix.BLINK_HALF_HZ
                else:
                    blinkMode = BiColorLedMatrix.BLINK_OFF
            else:
                blinkMode = BiColorLedMatrix.BLINK_OFF
                
            self._ledMatrix.updateDisplayFromRows(redRows, greenRows, blinkMode)
        
        else:
            
            self._ledMatrix.displayOff()
            self._ledMatrix.clear()
            
            
    def _dispatchBuzzCmd(self, cmd):
        
        params = cmd.split(":")
        if len(params) == 3:
            
            freq = int(params[1])
            playtime = int(params[2])
            
            self._buzzer.buzz(freq, playtime)
    
    
    def dispatchCommand(self, message):
        
        cmd = message.strip()
        
        if cmd != "":
            
            if cmd == "FWD":
                self._motion.setThrottle(RemoteControlledActivity.DRIVE_THROTTLE)
                self._motion.goForwards()
                self._ledMatrix.updateDisplayFromRows(greenRows=RemoteControlledActivity.STATE_MATRICES[0])
            elif cmd == "BAK":
                self._motion.setThrottle(RemoteControlledActivity.SLOW_THROTTLE)
                self._motion.goBackwards()
                self._ledMatrix.updateDisplayFromRows(redRows=RemoteControlledActivity.STATE_MATRICES[1]);
            elif cmd == "TLE":
                self._motion.turnLeft()
                #The led-matrix is placed with its base line to the forward direction, therefore left and right are reversed 
                self._ledMatrix.updateDisplayFromRows(RemoteControlledActivity.STATE_MATRICES[3],RemoteControlledActivity.STATE_MATRICES[3]);
            elif cmd == "TRI":
                self._motion.turnRight()
                self._ledMatrix.updateDisplayFromRows(RemoteControlledActivity.STATE_MATRICES[2],RemoteControlledActivity.STATE_MATRICES[2]);
            elif cmd.startswith("EXP"):
                self._dispatchExpression(cmd)
            elif cmd.startswith("LMX"):
                self._dispatchLedMatrixCmd(cmd)
            elif cmd.startswith("BUZ"):
                self._dispatchBuzzCmd(cmd)
            else:
                self._motion.stop()
                self._ledMatrix.displayOff()
                self._ledMatrix.clear()
