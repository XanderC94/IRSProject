import math, operator

WHEEL_RADIUS = 0.02
AXLE_LENGTH = 0.052

RANGE = float(1024 / 2)

EPUCK_FRONT_RAD = math.pi / 2
PI = math.pi
W_WHEEL = 2 * PI
MAX_V = 7.536

nLEDs = 10
nDistanceSensors = 8
nLightSensors = 9
nMotors = 2
nBumpers = 8

lss_rad = [1.27, 0.77, 0.0, 5.21, 4.21, 3.14159, 2.37, 1.87, 1.58784]
dss_rad = [1.27, 0.77, 0.0, 5.21, 4.21, 3.14159, 2.37, 1.87]
motors_rad = [0.0, 3.14159]
bumpers_rad = [1.27, 0.77, 0.0, 5.21, 4.21, 3.14159, 2.37, 1.87]

distance_sensor_template = 'ps{id}'
light_sensor_template = 'ls{id}'
led_template = 'led{id}'
bumper_template = 'bs{id}'