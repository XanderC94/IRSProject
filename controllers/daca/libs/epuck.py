import math, operator
from libs.sensor import ids

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

MIN_V = PI /  (nBumpers / 4)

lss_rad = [1.27, 0.77, 0.0, 5.21, 4.21, 3.14159, 2.37, 1.87, 1.58784]
dss_rad = [1.27, 0.77, 0.0, 5.21, 4.21, 3.14159, 2.37, 1.87]
motors_rad = [0.0, 3.14159]
bumpers_rad = [1.27, 0.77, 0.0, 5.21, 4.21, 3.14159, 2.37, 1.87]

distance_sensor_template = 'ps{id}'
light_sensor_template = 'ls{id}'
led_template = 'led{id}'
bumper_template = 'bs{id}'

class ID:
    distances = ids(distance_sensor_template, nDistanceSensors)
    lights = ids(light_sensor_template, nLightSensors)
    leds = ids(led_template, nLEDs)
    motors = {'left':'left wheel motor', 'right':'right wheel motor'}
    bumpers = ids(bumper_template, nBumpers)