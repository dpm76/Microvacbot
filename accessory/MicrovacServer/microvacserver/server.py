#!/usr/bin/env python3
from time import sleep
from datetime import datetime

from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple

from jsonrpc import JSONRPCResponseManager, dispatcher
import socket
import sys
import random
    
FEEDBACK_BUFFER_LENGTH = 128
SOCKET_TIMEOUT = 600
DEFAULT_ROBOT_PORT = 333
DEFAULT_SERVER_IP = "localhost"
DEFAULT_SERVER_PORT = 4000

_fake = False

def _sendCommand(data, fakeDelay=0, fakeResponse=None):

    global soc
    global _fake
    
    if len(data) == 0:
        return
    
    msg = ""
    for item in data:
        msg += ":" + item
        
    print(msg[1:])
    
    if not _fake:
        soc.sendall(bytes(msg[1:], 'ascii'))
        feedback = soc.recv(FEEDBACK_BUFFER_LENGTH).decode('ascii').strip().split(':')
        
        assert feedback[0] == data[0], f"Received answer for command '{feedback[0]}' but expecting for command '{data[0]}'."
        assert feedback[1] == "OK", feedback[2] if len(feedback) > 2 else "Unknown error"
        
        response = {"success": "OK"}
        if len(feedback) > 2:
            response["data"] = feedback[2]
        
    else:
        
        response = {"success": "OK"}
        if fakeResponse != None:
        	response["data"] = fakeResponse
        	
        if fakeDelay != 0:
        	sleep(fakeDelay)
        
    return response
    

def _sendMotionCommand(command, time = 0, unit = "s"):

    if time > 0:
        response = _sendCommand([command, str(time), unit])
    else:
        response = _sendCommand([command])
        
    return response
    
    
@dispatcher.add_method
def forwards(time = 0, unit = "s"):
    
    return _sendMotionCommand("FWD", time, unit)
    

@dispatcher.add_method
def backwards(time = 0, unit = "s"):
    
    return _sendMotionCommand("BAK", time, unit)
    

@dispatcher.add_method
def turnLeft(time = 0, unit = "s"):
    
    return _sendMotionCommand("TLE", time, unit)
    
    
@dispatcher.add_method
def turnRight(time = 0, unit = "s"):
    
    return _sendMotionCommand("TRI", time, unit)


@dispatcher.add_method
def stop():
    
    return _sendCommand(["STO"])


@dispatcher.add_method
def displayExpression(idExp):

    return _sendCommand(["EXP", str(idExp)])
    
    
@dispatcher.add_method
def beep(freq, millisec):

    return _sendCommand(["BUZ", str(freq), str(millisec)], fakeDelay=millisec/1000.0)
    
    
@dispatcher.add_method
def turnTo(angle, isDegrees):

    return _sendCommand(["TRT", str(angle), "d" if isDegrees else "r"])
    
    
@dispatcher.add_method
def turn(angle, isDegrees):

    return _sendCommand(["TRN", str(angle), "d" if isDegrees else "r"])
    
    
@dispatcher.add_method
def forwardsTo(length):

    return _sendCommand(["FWT", str(length)])


@dispatcher.add_method
def backwardsTo(length):

    return _sendCommand(["BKT", str(length)])


@dispatcher.add_method
def wait(seconds):

    sleep(seconds)
    return { "success": "OK" }    
    
    
@dispatcher.add_method
def getDistance():

    return _sendCommand(["DST"], fakeResponse=random.randrange(0,400))


@Request.application
def application(request):
    
    if request.environ['REQUEST_METHOD'] == "POST":
    
        print(datetime.now().strftime("%Y%m%d-%H%M%S\t") + str(request.data))
        result = JSONRPCResponseManager.handle(request.data, dispatcher)
        print(datetime.now().strftime("%Y%m%d-%H%M%S\t") + result.json)
        response = Response(result.json, mimetype='application/json')
        sleep(0.15) # Wait between commands
        
    else:
        
        #An OPTIONS verb may come to validate the CORS request
        response = Response("null", mimetype='application/json')
    
    response.headers["Access-Control-Allow-Origin"] = "*" #"http://localhost:8000"
    response.headers["Access-Control-Allow-Headers"] = "content-type"

    return response
    
    
def main():

    global soc
    global _fake
    
    if len(sys.argv) < 2 or sys.argv[1] == "--help":
    
        print("Usage:")
        print("\tserver IP [PORT]")
        print("Where")
        print("\tIP: the IP address of the robot")
        print("\tPORT (optional, default=333): the port of the robot")
        print("or")
        print("\tserver --fake")
        print("\tThe messages won't be actually sent but they will be shown on the output")
        print("or")
        print("\tserver --help")
        print("for this message")
        
        sys.exit(1)
        
    if sys.argv[1] == "--fake":
    
        _fake = True
    
    try:
        
        if not _fake:
        
            ip = sys.argv[1]
            port = int(sys.argv[2]) if len(sys.argv) >= 3 else DEFAULT_ROBOT_PORT
        
            soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            soc.settimeout(SOCKET_TIMEOUT)
            print(f"Connecting to {ip}:{port}")
            soc.connect((ip, port))
            print("Connected")
            
        else:
            print("Fake mode: Just echo!")
        
        
        run_simple(DEFAULT_SERVER_IP, DEFAULT_SERVER_PORT, application)
    except KeyboardInterrupt:
        stop()        
    except socket.timeout:
        print("ERROR: Robot not responding. Is it turned on and the remote-controlled activity running?")
    finally:
        if not _fake:
            soc.close()
        print("Server closed")
        

if __name__ == '__main__':

    main()
 
