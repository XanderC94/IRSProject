"""phototaxis controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, LED, DistanceSensor
from controller import *
import math
import operator

WHEEL_RADIUS = 0.02
AXLE_LENGTH = 0.052
RANGE = float(1024 / 2)
EPUCK_FRONT_RAD = math.pi / 2
PI = math.pi
W_WHEEL = 2 * PI
MAX_VL = 7.536
MAX_VR = 7.536

####################################################################################################

class Sensor:

    def __init__(self, device, position):
        self.device = device
        self.position = position

def ids(template, n):
    names = {}
    for i in range(0, n):
        names.update({i:template.format(id = i)})
    
    return names

def sensorArray(ids, timestep, getter, pos = [0.0], enable = True): 
    ss = {}
    i = 0
    
    for k, name in ids.items():
        
        s = getter(name)
        
        if (enable) : s.enable(timestep)
        
        ss.update({k:Sensor(s, pos[i])})

        if len(pos) > i+1 : i += 1
        
    return ss

def maximum(magnitudes, radians):
    m = max(magnitudes)
    theta = radians[magnitudes.index(m)]
    return (m, theta)

def compose(magnitudes, radians):
    v = [0.0, 0.0]

    for i in range(0, len(magnitudes)):
        v[0] += magnitudes[i]*math.cos(radians[i])
        v[1] += magnitudes[i]*math.sin(radians[i])
    
    m = math.sqrt(v[0]*v[0]+v[1]*v[1])
    theta = math.atan2(v[1], v[0])

    return (m, betweenZeroPi(theta))

def lightPerceptor(magnitudes, radians, strat = lambda magnitudes, radians: (float, float)):
   return strat(magnitudes, radians)

def obstaclePerceptor(magnitudes, radians, strat = lambda magnitudes, radians: (float, float)):
    res, theta = strat(magnitudes, radians)

    return (0, EPUCK_FRONT_RAD) if res < 0.5 else (res, theta + PI)

def mergePerception(magnitudes, radians, strat = lambda magnitudes, radians: (float, float)):
    return strat(magnitudes, radians)

def betweenZeroPi(rad):
    if (rad < 0):
        return 2 * PI + rad 
    else:
        return rad
# w = 2*v*sin(theta)/d
def differential(theta, d): 
    v = abs(EPUCK_FRONT_RAD - theta)  
    w = 2 * v * math.sin(theta) / d
    vl = v+d/2*w
    vr = v-d/2*w

    return (
        min(vl, MAX_VL - 1) * -rsign(theta) + 1, 
        min(vr, MAX_VR - 1) * rsign(theta) + 1
    )

rsign = lambda theta: 1 if theta > PI / 2 and theta < 3/2 * PI else -1

#########################################################################################################

led_n = 10
ds_n = 8
ls_n = 9
motor_n = 2
pos_n = 2
bumper_n = 8

ls_rad = [1.27, 0.77, 0.0, 5.21, 4.21, 3.14159, 2.37, 1.87, 1.58784]
ds_rad = [1.27, 0.77, 0.0, 5.21, 4.21, 3.14159, 2.37, 1.87]
motor_rad = [0.0, 3.14159]
bumper_rad = [0.0]

distance_sensor_template = 'ps{id}'
light_sensor_template = 'ls{id}'
led_template = 'led{id}'
bumper_template = 'bs{id}'

distance_ids = ids(distance_sensor_template, ds_n)
light_ids = ids(light_sensor_template, ls_n)
led_ids = ids(led_template, led_n)
motors_ids = {'left':'left wheel motor', 'right':'right wheel motor'}
bumper_ids = ids(bumper_template, bumper_n)

# create the Robot instance.
robot = Robot()

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

# You should insert a getDevice-like function in order to get the
# instance of a device of the robot. Something like:
#  led = robot.getLED('ledname')
#  ds = robot.getDistanceSensor('dsname')
#  ds.enable(timestep)

led = sensorArray(led_ids, timestep, lambda name: robot.getLED(name), enable = False)
motor = sensorArray(motors_ids, timestep, lambda name: robot.getMotor(name), enable = False)

ds = sensorArray(distance_ids, timestep, lambda name: robot.getDistanceSensor(name))
ls = sensorArray(light_ids, timestep, lambda name: robot.getLightSensor(name))
bumper = sensorArray(bumper_ids, timestep, lambda name: robot.getTouchSensor(name))

for k, m in motor.items():
    m.device.setPosition(float('+inf'))
    m.device.setVelocity(0.0)

# Main loop:
# - perform simulation steps until Webots is stopping the controller
while robot.step(timestep) != -1:
    # Read the sensors:
    
    ds_values = []
    ls_values = []
    bumper_value = bumper[0].device.getValue()
        
    print(f"Bumper:{bumper_value}")

    # if bumper_value == 1.0: break

    for k, s in ds.items(): ds_values.append(s.device.getValue())
    for k, s in ls.items(): ls_values.append(s.device.getValue())
    
    print(f"distance:{ds_values}")
    print(f"light:{ls_values}")
    
    # Process sensor data here.
    magnitudes = []
    radians = []

    # res, theta = lightPerceptor(ls_values, ls_rad, compose)
    # magnitudes.append(res)
    # radians.append(theta)
    # print(f"light direction:{theta}, magnitude: {res}")

    res, theta = obstaclePerceptor(ds_values, ds_rad, maximum)
    magnitudes.append(res)
    radians.append(theta)
    print(f"obstacle direction:{theta}, distance:{res}")
    
    if (len(magnitudes) > 1):
        res, theta = mergePerception(magnitudes, radians, maximum)
        print(f"direction:{theta}, magnitude:{res}")

    lv, rv = differential(theta, AXLE_LENGTH)

    print(f"Speed:{lv}, {rv}")
        
    # Enter here functions to send actuator commands:
    
    motor['left'].device.setVelocity(lv)
    motor['right'].device.setVelocity(rv)

    pass

# Enter here exit cleanup code.
motor['left'].device.setVelocity(0.0)
motor['right'].device.setVelocity(0.0)