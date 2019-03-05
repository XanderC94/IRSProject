"""phototaxis controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, LED, DistanceSensor
from controller import *
import sys, math, operator, os

from libs.epuck import *
from libs.argutils import *
from libs.sensor import *
import libs.motor as motor

from libs.motorschema import *

#########################################################################################################

distance_ids = ids(distance_sensor_template, nDistanceSensors)
light_ids = ids(light_sensor_template, nLightSensors)
led_ids = ids(led_template, nLEDs)
motors_ids = {'left':'left wheel motor', 'right':'right wheel motor'}
bumper_ids = ids(bumper_template, nBumpers)

# create the Robot instance.
robot = Robot()

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

# You should insert a getDevice-like function in order to get the
# instance of a device of the robot. Something like:
#  led = robot.getLED('ledname')
#  ds = robot.getDistanceSensor('dsname')
#  ds.enable(timestep)

leds = sensorArray(led_ids, timestep, lambda name: robot.getLED(name), enable = False)
motors = sensorArray(motors_ids, timestep, lambda name: robot.getMotor(name), enable = False)

dss = sensorArray(distance_ids, timestep, lambda name: robot.getDistanceSensor(name))
lss = sensorArray(light_ids, timestep, lambda name: robot.getLightSensor(name))
bumpers = sensorArray(bumper_ids, timestep, lambda name: robot.getTouchSensor(name))

for k, m in motors.items():
    m.device.setPosition(float('+inf'))
    m.device.setVelocity(0.0)

# Main loop:
# - perform simulation steps until Webots is stopping the controller
while robot.step(timestep) != -1:
    # Read the sensors:
    
    ds_values = []
    ls_values = []
    bumper_value = bumpers[0].device.getValue()
        
    print(f"Bumper:{bumper_value}")

    if bumper_value == 1.0: break

    for k, s in dss.items(): ds_values.append(s.device.getValue())
    for k, s in lss.items(): ls_values.append(s.device.getValue())
    
    print(f"distance:{ds_values}")
    print(f"light:{ls_values}")
    
    # Process sensor data here.
    magnitudes = []
    radians = []

    res, theta = PerceptionSchema.lightPerceptor(ls_values, lss_rad, compose)
    magnitudes.append(res)
    radians.append(theta)
    print(f"light direction:{theta}, magnitude: {res}")

    res, theta = PerceptionSchema.obstaclePerceptor(ds_values, dss_rad, maximum)
    magnitudes.append(res)
    radians.append(theta)
    print(f"obstacle direction:{theta}, distance:{res}")
    
    if (len(magnitudes) > 1):
        res, theta = PerceptionSchema.mergePerception(magnitudes, radians, maximum)
        print(f"direction:{theta}, magnitude:{res}")

    lv, rv = motor.differential(theta, AXLE_LENGTH)

    print(f"Speed:{lv}, {rv}")
        
    # Enter here functions to send actuator commands:
    
    motors['left'].device.setVelocity(lv)
    motors['right'].device.setVelocity(rv)

    pass

# Enter here exit cleanup code.
motors['left'].device.setVelocity(0.0)
motors['right'].device.setVelocity(0.0)