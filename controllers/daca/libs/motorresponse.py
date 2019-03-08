from libs.epuck import *
from libs.motor import *

decToRad = lambda degrees: degrees * PI / 180


default_veloity=1.0

def advance():
    return differential(0, AXLE_LENGTH)
    
def reverse():
    return differential(PI, AXLE_LENGTH)

def turnLeft9Deg():
    return differential(decToRad(-9), AXLE_LENGTH)

def turnLeft1Deg():
    return differential(decToRad(-1), AXLE_LENGTH)

def turnRight9Deg():
    return differential(decToRad(9), AXLE_LENGTH)

def turnRight1Deg():
    return differential(decToRad(1), AXLE_LENGTH)