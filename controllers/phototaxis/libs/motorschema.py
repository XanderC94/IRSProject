
import math, operator
from libs.epuck import EPUCK_FRONT_RAD, PI

def maximum(magnitudes, radians):
    m = max(magnitudes)
    theta = radians[magnitudes.index(m)]
    return (m, theta)


def betweenZeroPi(rad):
    if (rad < 0):
        return 2 * PI + rad 
    else:
        return rad

def compose(magnitudes, radians):
    v = [0.0, 0.0]

    for i in range(0, len(magnitudes)):
        v[0] += magnitudes[i]*math.cos(radians[i])
        v[1] += magnitudes[i]*math.sin(radians[i])
    
    m = math.sqrt(v[0]*v[0]+v[1]*v[1])
    theta = math.atan2(v[1], v[0])

    return (m, betweenZeroPi(theta))

class PerceptionSchema:
    
    @staticmethod
    def lightPerceptor(magnitudes, radians, strat = lambda magnitudes, radians: (float, float)):
        return strat(magnitudes, radians)

    @staticmethod
    def obstaclePerceptor(magnitudes, radians, strat = lambda magnitudes, radians: (float, float)):
        res, theta = strat(magnitudes, radians)

        return (0, EPUCK_FRONT_RAD) if res < 0.5 else (res, theta + PI)
    
    @staticmethod
    def mergePerception(magnitudes, radians, strat = lambda magnitudes, radians: (float, float)):
        return strat(magnitudes, radians)