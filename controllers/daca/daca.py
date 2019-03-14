"""phototaxis controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, LED, DistanceSensor
from controller import *
import sys, os

from libs.epuck import ID
from libs.argutils import parseArgs
from libs.sensor import sensorArray
from libs.motorresponse import wheelVelocity
import libs.motor as motor
from libs.utils import loadTrainedModel, saveTrainedModel, TrainedModel, NetParameters

print(os.getcwd())

opt = parseArgs(sys.argv)

print(opt)
version_name = ""

if 'version' in opt:

    if opt['version'] == 3:
        import libs.netversions.version3.neuralnetstructure as nns
        print("using ann v3")
        import libs.netversions.version3.evolutionlogic as ann
    else:
        print("using ann v2")
        import libs.netversions.version2.neuralnetstructure as nns
        import libs.netversions.version2.evolutionlogic as ann

    version_name = f"Version{opt['version']}"

isTrainingModeActive = False
trainTime = -1 # minutes, -1 -> Infinite
modelPath = ""

if 'mode' in opt and opt['mode'] == 'train':
    isTrainingModeActive = True
    if 'time' in opt:
        trainTime = opt['time']

if 'modelPath' in opt:
    modelPath = opt['modelPath']

if not isTrainingModeActive:
    loadedModel = loadTrainedModel(modelPath)

    ann.setNetworkParameters(loadedModel.parameters)

    ann.setNetworkConnectivities(loadedModel.connectivities)
elif 'parameters' in opt:
    ann.setNetworkParameters(opt['parameters'])

# Setup ------------------------------------

# create the Robot instance.
# robot = Robot()
robot = Supervisor()

# get the time step (ms) of the current world.
timeStep = int(robot.getBasicTimeStep())
nSteps = 0
maxSteps = int((trainTime * 60 * 1000) / timeStep)

print(f"TIME:{trainTime}min | STEP-TIME:{timeStep}ms => MAX-STEPS: {maxSteps}")

# You should insert a getDevice-like function in order to get the
# instance of a device of the robot.

leds = sensorArray(ID.leds, timeStep, lambda name: robot.getLED(name), enable = False)
motors = sensorArray(ID.motors, timeStep, lambda name: robot.getMotor(name), enable = False)

dss = sensorArray(ID.distances, timeStep, lambda name: robot.getDistanceSensor(name))
lss = sensorArray(ID.lights, timeStep, lambda name: robot.getLightSensor(name))
bumpers = sensorArray(ID.bumpers, timeStep, lambda name: robot.getTouchSensor(name))

for k, m in motors.items():
    m.device.setPosition(float('+inf'))
    m.device.setVelocity(0.0)

#-------------------------------------------------

n_touches = 0

# Main loop:
# - perform simulation steps until Webots is stopping the controller
while robot.step(timeStep) != -1 and nSteps != maxSteps:
    
    # ~~~~~~~ Read the sensors: ~~~~~~~~~~~~~
    distances = []
    bumps = []

    for k, s in dss.items(): distances.append(s.device.getValue())
    for k, s in bumpers.items(): bumps.append(s.device.getValue())
    
    if 1 in bumps: 
        print("TOUCHING!")
        n_touches += 1

    print(f"Distances:{distances}")
    
    ann.processAnnState(distances, bumps)

    # ~~~~~~~~~~~~~~~~~ UPDATE MOTOR SPEED ~~~~~~~~~~~~~~~~~~~~~~~~~
    lv, rv = ann.calculateMotorSpeed()
    print(f"Speed:{lv}, {rv}")
    motors['left'].device.setVelocity(lv)
    motors['right'].device.setVelocity(rv)

    if isTrainingModeActive:
        #~~~~~~~~~~~~~~~~~~~~~~~~ UPDATE ANN WEIGHT ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        ann.updateWeights()
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    print(f"N° of touches: {n_touches}")
    print()

    nSteps += 1

    pass

if isTrainingModeActive:
    parameters = NetParameters(nns.COLLISION_THRESHOLD, nns.LEARNING_RATE, nns.FORGET_RATE, nns.MOTOR_THRESHOLD, nns.REVERSE_THRESHOLD)
    model = TrainedModel(version_name, parameters, nns.connectivities)
    saveTrainedModel(model, modelPath)

# Enter here exit cleanup code.
motors['left'].device.setVelocity(0.0)
motors['right'].device.setVelocity(0.0)

robot.simulationSetMode(robot.SIMULATION_MODE_PAUSE)
robot.simulationReset()