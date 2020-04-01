#!/usr/bin/python3

'''
Created on 28 nov. 2019

@author: david
'''

import argparse
import sys
import os 
 
sys.path.append(os.path.dirname(os.path.realpath(__file__))+"/..")

from mpu6050_def import DMP_MEMORY, MPU6050_DMP_CODE_SIZE

CHUNK_SIZE = 16

def dumpBytes(path, buffer, length):
    
    with open(path, "wb") as f:
        
        i = 0
        j = CHUNK_SIZE
        
        while i !=j :
            f.write(buffer[i:j])
            i = j
            j = j + CHUNK_SIZE if j<length else length 
        


def main():
    
    parser = argparse.ArgumentParser(description="Dumps the memory for the DMP mode of the MPU6050 sensor onto a binary file.")
    parser.add_argument("path", metavar="TARGET_PATH", nargs="?", help="target path (i.e. path/dmp_mem.bin)")
    args = parser.parse_args()
    
    if args.path:
        dumpBytes(args.path, DMP_MEMORY, MPU6050_DMP_CODE_SIZE)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
