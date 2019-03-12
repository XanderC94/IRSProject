# w = 2*v*sin(theta)/d
import math
from libs.epuck import EPUCK_FRONT_RAD, MAX_V, PI

rsign = lambda theta: 1 if theta > PI / 2 and theta < 3/2 * PI else -1

sign = lambda theta: 1 if theta >= 0 else -1

def toDifferentialModel(v, theta, d):
    
    w = theta

    vl = v+d/2*w 
    vr = v-d/2*w 
    
    return (
        min(vl, MAX_V), 
        min(vr, MAX_V) 
    )