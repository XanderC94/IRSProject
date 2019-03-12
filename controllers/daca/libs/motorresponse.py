from libs.epuck import PI, AXLE_LENGTH, MIN_V
from libs.motor import toDifferentialModel, sign

degToRad = lambda degrees: degrees * PI / 180

def _stub_movement(velocity, theta):
    lv,rv = toDifferentialModel(velocity, theta, AXLE_LENGTH)
    return lv * sign(theta), rv * sign(theta)

def advance(velocity):
    return toDifferentialModel(velocity, 0, AXLE_LENGTH)
    
def reverse(velRight, velLeft):
    return -velRight, velLeft

def turnLeft(velocity):
    return _stub_movement(velocity, -PI/12)

def turnRight(velocity):
    return _stub_movement(velocity, PI/12)


def wheelVelocity(oLeftNeuron, reverseNeuron, oRightNeuron, defaultVelocity = MIN_V):

    areBothZero = (oLeftNeuron == 0 and oRightNeuron == 0)
    
    lv,rv = (defaultVelocity, defaultVelocity) if areBothZero else (oLeftNeuron, oRightNeuron)

    if reverseNeuron != 0:
        if oLeftNeuron < oRightNeuron:
            lv = -lv
        else:
            rv = -rv   
    elif lv == 0.0:
        lv = defaultVelocity
    elif rv == 0.0:
        rv = defaultVelocity
    
    return lv,rv