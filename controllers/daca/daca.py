"""phototaxis controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, LED, DistanceSensor
from controller import *
import sys, os

print(os.getcwd())

from libs.epuck import ID
from libs.argutils import parseArgs
from libs.sensor import sensorArray
from libs.motorresponse import wheelVelocity
import libs.motor as motor
import libs.utils as utils

opt = parseArgs(sys.argv)

print(opt)

version_name = ""

if 'version' in opt:

    if opt['version'] == 3:
        print("Using ANN v3")
        import libs.netversions.version3.neuralnetstructure as nns
        import libs.netversions.version3.evolutionlogic as ann
    else:
        print("Using ANN v2")
        import libs.netversions.version2.neuralnetstructure as nns
        import libs.netversions.version2.evolutionlogic as ann

    version_name = f"Version{opt['version']}"

isTrainingModeActive = False

executionMode=""
if 'mode' in opt:
    executionMode = opt['mode']
    if opt['mode'] == 'train':
        isTrainingModeActive = True
        
runtime = -1 # minutes, -1 -> Infinite
if 'time' in opt:
    runtime = opt['time']

modelPath = ""
if 'modelPath' in opt:
    modelPath = opt['modelPath']

simulatioLogPath = ""
if 'simulatioLogPath' in opt:
    simulatioLogPath = opt['simulatioLogPath']

if not isTrainingModeActive:
    print('Mode: Test')
    loadedModel = utils.loadTrainedModel(modelPath)
    print(loadedModel.parameters)
    ann.setNetworkParameters(loadedModel.parameters)
    ann.setNetworkConnectivities(loadedModel.connectivities)

elif 'parameters' in opt:
    print('Mode: Train')
    print('params:', opt['parameters'])
    ann.setNetworkParameters(opt['parameters'])

# Setup ------------------------------------

log = utils.SimulationLog(f"{version_name}-{executionMode}")
logger = utils.DACLogger(f"{version_name}-{executionMode}")

# create the Robot instance.
# robot = Robot()
# Supervisor extends Robot but has access to all the world info. 
# Useful for automating the simulation.
robot = Supervisor() 

# get the time step (ms) of the current world.
timeStep = int(robot.getBasicTimeStep())
nSteps = 0
maxSteps = int((runtime * 60 * 1000) / timeStep)

print(f"TIME:{runtime} min | STEP-TIME:{timeStep} ms => MAX-STEPS: {maxSteps}")

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

nTouches = 0

# Main loop:
# - perform simulation steps until Webots is stopping the controller
while robot.step(timeStep) != -1 and nSteps != maxSteps:
    
    # ~~~~~~~ Read the sensors: ~~~~~~~~~~~~~

    distances = []
    bumps = []

    for k, s in dss.items(): distances.append(s.device.getValue())
    for k, s in bumpers.items(): bumps.append(s.device.getValue())
    
    hasTouched = (1 in bumps)
    
    if hasTouched: 
        logger.debug("TOUCHING!")
        nTouches += 1

    logger.debug(f"Distances:{distances}")

    # ~~~~~~~~~~~~~~~~~ Process Sensors Data ~~~~~~~~~~~~~~~~~~~~~~~~~
    
    ann.processAnnState(distances, bumps)

    # ~~~~~~~~~~~~~~~~~ UPDATE MOTOR SPEED ~~~~~~~~~~~~~~~~~~~~~~~~~
    lv, rv = ann.calculateMotorSpeed()
    logger.debug(f"Speed:{lv}, {rv}")
    motors['left'].device.setVelocity(lv)
    motors['right'].device.setVelocity(rv)

    # ~~~~~~~~~~~~~~~~~~~~~~~~ UPDATE ANN WEIGHT ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    if isTrainingModeActive:
        ann.updateWeights()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~ LOGGING STUFF ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    logger.debug(f"N° of touches: {nTouches}")
    logger.debug('########################################')

    coordinates = robot.getSelf().getField("translation").getSFVec3f()
    robotPosition = utils.Position.fromTuple(coordinates)

    log.addLogEntry(utils.LogEntry(nSteps, hasTouched, robotPosition, nTouches))

    nSteps += 1

    pass

if isTrainingModeActive:
    parameters = utils.NetParameters.fromDict(ann.getNetworkParams())
    model = utils.TrainedModel(version_name, parameters, nns.connectivities)
    utils.saveTrainedModel(model, modelPath)

log.saveTo(simulatioLogPath)

# Enter here exit cleanup code.
motors['left'].device.setVelocity(0.0)
motors['right'].device.setVelocity(0.0)

robot.simulationSetMode(robot.SIMULATION_MODE_PAUSE)
robot.simulationReset()