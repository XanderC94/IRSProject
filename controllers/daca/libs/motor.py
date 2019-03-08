# w = 2*v*sin(theta)/d
import math
from libs.epuck import EPUCK_FRONT_RAD, MAX_V, PI

rsign = lambda theta: 1 if theta > PI / 2 and theta < 3/2 * PI else -1

def differential(theta, d): 
    v = abs(EPUCK_FRONT_RAD - theta) * d/2
    w = 2 * v * math.sin(theta) / d
    vl = v+d/2*w
    vr = v-d/2*w

    return (
        min(vl, MAX_V - 1) * -rsign(theta) + 1, 
        min(vr, MAX_V - 1) * rsign(theta) + 1
    )