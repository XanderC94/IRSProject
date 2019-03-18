import sys, math, operator
from libs.sensor import ids
from libs.argutils import parseArgs
from controller import *
from libs.sensor import sensorArray

WHEEL_RADIUS = 0.02 #m
AXLE_LENGTH = 0.052 #m

RANGE = float(1024 / 2)

PI = math.pi
EPUCK_FRONT_RAD = PI / 2
EPUCK_FRONT_DEG = EPUCK_FRONT_RAD * 180 / PI
W_WHEEL = 2 * PI
MAX_V = 7.536 #1200 step al secondo

nLEDs = 10
nDistanceSensors = 8
nLightSensors = 9
nMotors = 2
nBumpers = 8

_opt = parseArgs(sys.argv)

MIN_V = PI / (nBumpers / 2)

if 'version' in _opt and _opt['version'] == 3:
    MIN_V = 2 * PI / (nBumpers / 2)

lss_rad = [1.27, 0.77, 0.0, 5.21, 4.21, 3.14159, 2.37, 1.87, 1.58784]
dss_rad = [1.27, 0.77, 0.0, 5.21, 4.21, 3.14159, 2.37, 1.87]
motors_rad = [0.0, 3.14159]
bumpers_rad = [1.27, 0.77, 0.0, 5.21, 4.21, 3.14159, 2.37, 1.87]

distance_sensor_template = 'ps{id}'
light_sensor_template = 'ls{id}'
led_template = 'led{id}'
bumper_template = 'bs{id}'

# -------------------------------------------------------------------------------------------

class ID:
    distances = ids(distance_sensor_template, nDistanceSensors)
    lights = ids(light_sensor_template, nLightSensors)
    leds = ids(led_template, nLEDs)
    motors = {'left':'left wheel motor', 'right':'right wheel motor'}
    positions = {'left': 'left wheel sensor', 'right':'right wheel sensor'}
    bumpers = ids(bumper_template, nBumpers)

# create the Robot instance.
# robot = Robot()

# Supervisor extends Robot but has access to all the world info. 
# Useful for automating the simulation.
robot = Supervisor() 

# get the time step (ms) of the current world.
timeStep = int(robot.getBasicTimeStep())

#Retrieve device references
leds = sensorArray(ID.leds, timeStep, lambda name: robot.getLED(name), enable = False)
motors = sensorArray(ID.motors, timeStep, lambda name: robot.getMotor(name), enable = False)

dss = sensorArray(ID.distances, timeStep, lambda name: robot.getDistanceSensor(name))
lss = sensorArray(ID.lights, timeStep, lambda name: robot.getLightSensor(name))
bumpers = sensorArray(ID.bumpers, timeStep, lambda name: robot.getTouchSensor(name))