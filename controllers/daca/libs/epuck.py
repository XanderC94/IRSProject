import math, operator

WHEEL_RADIUS = 0.02
AXLE_LENGTH = 0.052

RANGE = float(1024 / 2)

EPUCK_FRONT_RAD = math.pi / 2
PI = math.pi
W_WHEEL = 2 * PI
MAX_VL = 7.536
MAX_VR = 7.536

led_n = 10
ds_n = 8
ls_n = 9
motor_n = 2
pos_n = 2
bumper_n = 8

ls_rad = [1.27, 0.77, 0.0, 5.21, 4.21, 3.14159, 2.37, 1.87, 1.58784]
ds_rad = [1.27, 0.77, 0.0, 5.21, 4.21, 3.14159, 2.37, 1.87]
motor_rad = [0.0, 3.14159]
bumper_rad = [1.27, 0.77, 0.0, 5.21, 4.21, 3.14159, 2.37, 1.87]

distance_sensor_template = 'ps{id}'
light_sensor_template = 'ls{id}'
led_template = 'led{id}'
bumper_template = 'bs{id}'