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
from libs.utils import *
# import libs.annutils as ann

opt = parseArgs(sys.argv)

print(opt)
version_name=""
if 'version' in opt 
    if opt['version'] == '3':
        # from libs.netversions.version3.neuralnetstructure import *
        print("using ann v3")
        import libs.netversions.version3.evolutionlogic as ann
    else:
        print("using ann v2")
        # from libs.netversions.version2.neuralnetstructure import *
        import libs.netversions.version2.evolutionlogic as ann
    version_name = "Version"opt['version']

isTrainModeActive = False
if 'mode' in opt and opt['mode'] == 'train':
    isTrainModeActive = True

modelDirectory = ""
if 'modelDirectory' in opt:
    modelDirectory=opt['modelDirectory']

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

if !isTrainModeActive:
    loadedModel = loadTrainedModel(modelPath)
    COLLISION_THRESHOLD = loadedModel.parameters.collision_treshold
    LEARNING_RATE = loadedModel.parameters.learning_rate
    FORGET_RATE = loadedModel.parameters.forget_rate
    MOTOR_THRESHOLD = loadedModel.parameters.motor_threshold
    REVERSE_THRESHOLD = loadedModel.parameters.reverse_threshold
    connectivities = loadedModel.connectivities
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
    
    ann.processAnnState(distances, bumps)

    # ~~~~~~~~~~~~~~~~~ UPDATE MOTOR SPEED ~~~~~~~~~~~~~~~~~~~~~~~~~
    lv, rv = ann.calculateMotorSpeed()
    print(f"Speed:{lv}, {rv}")
    motors['left'].device.setVelocity(lv)
    motors['right'].device.setVelocity(rv)

    #~~~~~~~~~~~~~~~~~~~~~~~~ UPDATE ANN WEIGHT ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ann.updateWeights()
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    print()

    pass

if isTrainModeActive:
    parameters = NetParameters(COLLISION_THRESHOLD, LEARNING_RATE, FORGET_RATE, MOTOR_THRESHOLD, REVERSE_THRESHOLD)
    model = TrainedModel(version_name, parameters, connectivities)
    saveTrainedModel(model, modelDirectory)

# Enter here exit cleanup code.
motors['left'].device.setVelocity(0.0)
motors['right'].device.setVelocity(0.0)