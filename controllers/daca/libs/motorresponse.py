from libs.epuck import *
from libs.motor import *

degToRad = lambda degrees: degrees * PI / 180

def deltaFromFront(radiant):
    translatedRad = radiant + EPUCK_FRONT_RAD
    return translatedRad if translatedRad < PI else 2*PI - translatedRad

def advance(velocity):
    return toDifferentialModel(velocity, 0, AXLE_LENGTH)
    
def reverse(velocity):
    return toDifferentialModel(velocity, -PI, AXLE_LENGTH)

def turnLeft9Deg(velocity):
    return toDifferentialModel(velocity, degToRad(-9), AXLE_LENGTH)

def turnLeft1Deg(velocity):
    return toDifferentialModel(velocity, degToRad(-1), AXLE_LENGTH)

def turnRight9Deg(velocity):
    return toDifferentialModel(velocity, degToRad(9), AXLE_LENGTH)

def turnRight1Deg(velocity):
    return toDifferentialModel(velocity, degToRad(1), AXLE_LENGTH)