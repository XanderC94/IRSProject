"""phototaxis controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, LED, DistanceSensor
from controller import *
import math
import operator

WHEEL_RADIUS = 0.02
AXLE_LENGTH = 0.052
RANGE = float(1024 / 2)

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

def useMax(lvs, rads):
    res = max(lvs)
    a = rads[lvs.index(res)]
    return (res, a)

def compose(lvs, rads):
    v = [0.0, 0.0]

    for i in range(0, len(lvs)):
        v[0] += lvs[i]*math.cos(rads[i])
        v[1] += lvs[i]*math.sin(rads[i])
    
    m = v[0]*v[0]+v[1]*v[1]
    theta = math.atan2(v[1], v[0]) if v[1] > 0 else 0.0

    return (m, theta)

def lightPerceptor(lvs, rads, strat = lambda lvs, rads: (float, float)): 
    return strat(lvs, rads)

differential = lambda v, w, d: (v+d/2*w, v-d/2*w)

sign = lambda theta: 1 if theta > math.pi / 2 and theta < 3/2 * math.pi else -1

#########################################################################################################

led_n = 10
ds_n = 8
ls_n = 9
motor_n = 2
pos_n = 2
bumper_n = 1

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

braitenberg_coefficients = [
    [0.942, -0.22], 
    [0.63, -0.1], 
    [0.5, -0.06],
    [-0.06, -0.06],
    [-0.06, -0.06], 
    [-0.06, 0.5], 
    [-0.19, 0.63], 
    [-0.13, 0.942]
]

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
    
    speed = [0.0, 0.0] # 0 = sx, 1 = dx

    ds_values = []
    ls_values = []
    bumper_value = bumper[0].device.getValue()
    
    for k, s in ds.items(): ds_values.append(s.device.getValue())
    for k, s in ls.items(): ls_values.append(s.device.getValue())
    
    print(ds_values)
    print(ls_values)
    
    # Process sensor data here.

    res, theta = lightPerceptor(ls_values, ls_rad, compose)

    print(f"light direction:{theta}")

    # if a >= math.pi / 2 - 0.05 and a <= math.pi / 2 + 0.05:
    #     for i in range(0, motor_n):
    #         for j in range(0, ds_n):
    #             speed[i] += braitenberg_coefficients[j][i] * (1.0 - ds_values[j] / RANGE)
    # else:
    arc = AXLE_LENGTH / 2 * abs(math.pi / 2 - theta)
    lv, rv = differential(arc, 2*math.pi, AXLE_LENGTH)
    # speed[0] = arc * -sign(a) * 50
    # speed[1] = arc * sign(a) * 50
    
    speed[0] = lv * -sign(theta) * 10
    speed[1] = rv * sign(theta) * 10
    
    print(speed)
    
    print(bumper_value)
    
    # Enter here functions to send actuator commands:
    
    motor['left'].device.setVelocity(speed[0])
    motor['right'].device.setVelocity(speed[1])

    pass

# Enter here exit cleanup code.
