'''
Created on 27 mar. 2020

@author: David
'''
'''
Run this program on the PC
'''

from socket import socket, AF_INET, SOCK_STREAM


def main():
    
    print("Socket client test")
    
    with socket(AF_INET, SOCK_STREAM) as client:
        client.settimeout(5)
        client.connect(("192.168.1.200", 333))
        try:
            print("Send")
            nBytes = client.send(b"HELLO!")
            print("{0} bytes sent.".format(nBytes))
            print("Receiving")
            print(client.recv(128))
            
        except Exception as ex:
            print("Error: {0}".format(ex))
        finally:
            client.close()
            print("Finish")
    


if __name__ == '__main__':
    
    main()