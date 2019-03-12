"""phototaxis controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, LED, DistanceSensor
from controller import *
import sys, math, operator, random

from libs.epuck import ID
from libs.argutils import parseArgs
from libs.sensor import sensorArray
from libs.motorresponse import wheelVelocity
import libs.motor as motor

import libs.annutils as ann
from libs.netversions.version3.neuralnetstructure import *
from libs.netversions.version3.evolutionlogic import *




opt = parseArgs(sys.argv)

print(opt)

# Setup ------------------------------------

# create the Robot instance.
robot = Robot()

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

# You should insert a getDevice-like function in order to get the
# instance of a device of the robot.

leds = sensorArray(ID.leds, timestep, lambda name: robot.getLED(name), enable = False)
motors = sensorArray(ID.motors, timestep, lambda name: robot.getMotor(name), enable = False)

dss = sensorArray(ID.distances, timestep, lambda name: robot.getDistanceSensor(name))
lss = sensorArray(ID.lights, timestep, lambda name: robot.getLightSensor(name))
bumpers = sensorArray(ID.bumpers, timestep, lambda name: robot.getTouchSensor(name))

for k, m in motors.items():
    m.device.setPosition(float('+inf'))
    m.device.setVelocity(0.0)

#-------------------------------------------------

# Main loop:
# - perform simulation steps until Webots is stopping the controller
while robot.step(timestep) != -1:
    
    # ~~~~~~~ Read the sensors: ~~~~~~~~~~~~~
    distances = []
    bumps = []

    for k, s in dss.items(): distances.append(s.device.getValue())
    for k, s in bumpers.items(): bumps.append(s.device.getValue())
    
    if 1 in bumps: print("TOUCHING!")
    print(f"Distances:{distances}")

    processAnnState(distances, bumps)

    # ~~~~~~~~~~~~~~~~~ UPDATE MOTOR SPEED ~~~~~~~~~~~~~~~~~~~~~~~~~
    lv, rv = calculateMotorSpeed()
    print(f"Speed:{lv}, {rv}")
    motors['left'].device.setVelocity(lv)
    motors['right'].device.setVelocity(rv)

    #~~~~~~~~~~~~~~~~~~~~~~~~ UPDATE ANN WEIGHT ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    updateWeight()
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    print()

    pass

# Enter here exit cleanup code.
motors['left'].device.setVelocity(0.0)
motors['right'].device.setVelocity(0.0)