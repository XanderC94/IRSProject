"""phototaxis controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, LED, DistanceSensor
# from controller import *
import sys, os, copy

print(os.getcwd())

import libs.epuck as epuck
from libs.argutils import Options
from libs.motorresponse import wheelVelocity
import libs.utils as utils
from libs.log import logger
from libs.learningparameters import LearningParameters
from libs.parameterchangingstrategies import ParametersChanger, ModelChanger

opt = Options.fromArgv(sys.argv)

logger.info(opt)

if opt.version == 3:
    # import libs.netversions.version3.neuralnetstructure as nns
    import libs.netversions.version3.evolutionlogic as ann
# elif opt['version'] == 4:
#     # import libs.netversions.version4.neuralnetstructure as nns
#     import libs.netversions.version4.evolutionlogic as ann
else:
    # import libs.netversions.version2.neuralnetstructure as nns
    import libs.netversions.version2.evolutionlogic as ann

logger.info(f"Using ANN v{opt.version}")
        
if opt.isTrainingModeActive and len(opt.parameters) > 0:
    ann.setNetworkParameters(opt.parameters)

logger.info(f"params:{ann.getNetworkParams()}")

# Setup ------------------------------------

# See libs.epuck

# ------------------------------------------------------------------------------------------------------

def simulation(opt : Options, model: utils.TrainedModel):

    # initialize simulation
    log = utils.SimulationLog(opt.executionMode, opt.runtime)
    
    nSteps = 0
    maxSteps = int((opt.runtime * 60 * 1000) / epuck.timeStep)

    logger.info(f"TIME:{opt.runtime} min | STEP-TIME:{epuck.timeStep} ms => MAX-STEPS: {maxSteps}")

    for _, m in epuck.motors.items():
        m.device.setPosition(float('+inf'))
        m.device.setVelocity(0.0)

    #-------------------------------------------------

    nTouches = 0

    # Main loop:
    # - perform simulation steps until Webots is stopping the controller
    while epuck.robot.step(epuck.timeStep) != -1 and nSteps != maxSteps:
        
        # ~~~~~~~ Read the sensors: ~~~~~~~~~~~~~

        distances = [s.device.getValue() for _, s in epuck.dss.items()]
        bumps = [s.device.getValue() for _, s in epuck.bumpers.items()]
        
        hasTouched = (1 in bumps)
        
        if hasTouched: nTouches += 1

        # ~~~~~~~~~~~~~~~~~ Process Sensors Data ~~~~~~~~~~~~~~~~~~~~~~~~~
        
        ann.processAnnState(distances, bumps)

        # ~~~~~~~~~~~~~~~~~ UPDATE MOTOR SPEED ~~~~~~~~~~~~~~~~~~~~~~~~~

        lv, rv = ann.calculateMotorSpeed()
        epuck.motors['left'].device.setVelocity(lv)
        epuck.motors['right'].device.setVelocity(rv)

        # ~~~~~~~~~~~~~~~~~~~~~~~~ UPDATE ANN WEIGHT ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        if opt.isTrainingModeActive: ann.updateWeights()

        # ~~~~~~~~~~~~~~~~~~~~~~~~~ LOGGING STUFF ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
        coordinates = epuck.robot.getSelf().getField("translation").getSFVec3f()
        robotPosition = utils.Position.fromTuple(coordinates)

        log.addLogEntry(utils.LogEntry(nSteps, hasTouched, 1 in ann.getLayerOutput(1).values(), robotPosition, nTouches))

        nSteps += 1

        pass


    if opt.isTrainingModeActive:
        model = utils.TrainedModel(opt.version, ann.getNetworkParams(), ann.getConnectivities())
        utils.saveTrainedModel(model, opt.modelPath)

    log.setModel(model)
    log.saveTo(opt.simulationLogPath)
    
    logger.flush()

#-----------------------------------------------------------------------------------------------------

def buildParameterChanger():
    parametersChanger = None
    if opt.isTrainingModeActive:
        parametersChanger = ParametersChanger.fromList(opt.changingInfo, bounded=False)
    else:
        modelFiles = utils.getAllFilesIn(f"./{opt.modelPath}", "json")
        """
        if opt.changingInfo is not None:
            parametersChanger = ParametersChanger.fromList(opt.changingInfo, bounded=False)
            parametersChanger = ParametersChanger(ModelChanger.createFromFilePaths(modelFiles), parametersChanger)
        else:
        """
        parametersChanger = ModelChanger.createFromFilePaths(modelFiles)

    return parametersChanger
    
#----------------------------------------------------------------------------------------------------
model = None

if opt.changingInfo is None and "json" in opt.modelPath:
   
    if not opt.isTrainingModeActive:
        model = utils.loadTrainedModel(opt.modelPath)
        logger.info(model.parameters)
        ann.setNetworkParameters(model.parameters)
        ann.setNetworkConnectivities(model.connectivities)

    simulation(opt, model)

else:

    initialPositionCoordinates = epuck.robot.getSelf().getField("translation").getSFVec3f()
    initialOrientation = epuck.robot.getSelf().getField("rotation").getSFRotation()

    initialConnectivities = copy.deepcopy(ann.getConnectivities())


    parametersChanger = buildParameterChanger()


    while parametersChanger.hasNext():

        if not opt.isTrainingModeActive:
            model = parametersChanger.next()
            ann.setNetworkParameters(model.parameters)
            ann.setNetworkConnectivities(model.connectivities)
        else:
            ann.setNetworkParameters(parametersChanger.next())
            


        simulation(opt, model)

        # Cleanup code and reset robot fields before next simulation.
        epuck.motors['left'].device.setVelocity(0.0)
        epuck.motors['right'].device.setVelocity(0.0)
        
        epuck.robot.simulationResetPhysics()

        epuck.robot.getSelf().getField("translation").setSFVec3f(initialPositionCoordinates)
        epuck.robot.getSelf().getField("rotation").setSFRotation(initialOrientation)

        if opt.isTrainingModeActive:
            ann.setNetworkConnectivities(copy.deepcopy(initialConnectivities))

        pass

# Cleanup code.
epuck.motors['left'].device.setVelocity(0.0)
epuck.motors['right'].device.setVelocity(0.0)

epuck.robot.simulationSetMode(epuck.robot.SIMULATION_MODE_PAUSE)
epuck.robot.simulationReset()

# --------------------------------------------------------------------------------------------------------------------------------------