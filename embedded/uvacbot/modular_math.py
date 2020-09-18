'''
Created on 18-sep-2020

@author: david
'''

def modularDiff(a, b, modulus):
    '''
    Calculates the shortest difference between two numbers according to a modular arithmetic
    
    @param a: First argument
    @param b: Second argument
    @param modulus: Modulus of the arithmetic
    @return: The shortest difference between two numbers according to a modular arithmetic
    '''
        
    diff1 = (a-b)%modulus
    diff2 = (b-a)%modulus
    if diff1 < diff2:
        diff = -diff1
    else:
        diff = diff2
        
    return diff
