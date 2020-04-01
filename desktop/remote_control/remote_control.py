'''
Created on 06/07/2017

@author: david
'''
from controller import Controller
import argparse
import logging

def main():
    '''
    Executes the process logic
    '''
    APP_VERSION = "0.0.1"
    
    DEFAULT_IP = "192.168.1.200"
    DEFAULT_PORT = 333
    
    logging.basicConfig(level=logging.DEBUG)
    
    parser = argparse.ArgumentParser(prog="remote_control", description="Microvacbot basic controller.")
    parser.add_argument("srvAddr", metavar="ADDRESS", nargs="?", default=DEFAULT_IP,
                    help=   """Robot's server address (default: {0}:{1}). \
                                Port is not required and it will used the default one if not present.\
                            """.format(DEFAULT_IP, DEFAULT_PORT))
    parser.add_argument("--testing", "-t", action="store_true",                   
                    help="Use testing mode")
    parser.add_argument("--local", "-l", action="store_true",                   
                    help="Runs locally (IP value will be ignored)")

    parser.add_argument("--version", action="version", version="%(prog)s v{0}".format(APP_VERSION))

    args = parser.parse_args()    
    
    
    controller = Controller()    
    
    try:
        address = args.srvAddr.split(":",1)
        controller.start(address[0], address[1] if len(address)>1 else DEFAULT_PORT, args.testing, args.local)
    except Exception as e:        
        print(e)
    finally:
        controller.stop()
        

if __name__ == '__main__':
    main()
