# w = 2*v*sin(theta)/d
import math
from libs.epuck import EPUCK_FRONT_RAD, MAX_V, PI

rsign = lambda theta: 1 if theta > PI / 2 and theta < 3/2 * PI else -1
sign = lambda theta: 1 if theta >= 0 else -1

def differential(theta, d): 
    # either this
    v = abs(EPUCK_FRONT_RAD - theta) * d / 2
    w = 2 * v * math.sin(theta) / d

    # or this
    # w = abs(EPUCK_FRONT_RAD - theta)
    # v = w / math.sin(theta) * d / 2

    vl = v-d/2*w
    vr = v+d/2*w

    return (
        min(vl, MAX_V - 1) + 1, #* -rsign(theta) + 1, 
        min(vr, MAX_V - 1) + 1 #* rsign(theta) + 1
    )

def toDifferentialModel(v, theta, d):
    
    w = theta
    # 7.536
    vl = v+d/2*w #7,45436
    vr = v-d/2*w #
    print(f"w = {w} v={v} d={d}  VL = {vl} Vr = {vr}")
    return (
        min(vl, MAX_V), 
        min(vr, MAX_V) 
    )