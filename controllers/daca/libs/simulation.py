# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, LED, DistanceSensor
# from controller import *
import sys, os, copy

import libs.epuck as epuck
from libs.argutils import opt, Options
from libs.utils import LogEntry, Position, TrainedModel
from libs.log import logger
from libs.learningparameters import LearningParameters
from libs.parameterchangingstrategies import ParametersChanger, ModelChanger

if opt.version == 3:
    # import libs.netversions.version3.neuralnetstructure as nns
    import libs.netversions.version3.evolutionlogic as ann
else:
    # import libs.netversions.version2.neuralnetstructure as nns
    import libs.netversions.version2.evolutionlogic as ann

# Setup ------------------------------------

# See libs.epuck

# ------------------------------------------------------------------------

def __step(opt: Options):
    # ~~~~~~~ Read the sensors: ~~~~~~~~~~~~~

    distances = [s.device.getValue() for _, s in epuck.dss.items()]
    bumps = [s.device.getValue() for _, s in epuck.bumpers.items()]

    # ~~~~~~~~~~~~~~~~~ Process Sensors Data ~~~~~~~~~~~~~~~~~~~~~~~~~
    
    ann.processAnnState(distances, bumps)

    # ~~~~~~~~~~~~~~~~~ UPDATE MOTOR SPEED ~~~~~~~~~~~~~~~~~~~~~~~~~

    lv, rv = ann.calculateMotorSpeed()

    epuck.motors['left'].device.setVelocity(lv)
    epuck.motors['right'].device.setVelocity(rv)

    # ~~~~~~~~~~~~~~~~~~~~~~~~ UPDATE ANN WEIGHT ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    if opt.isTrainingModeActive: ann.updateWeights()

    return (1 in bumps)

# ------------------------------------------------------------------------------------------------------

def run(opt : Options, loghook: lambda info: None) -> TrainedModel:
    
    # initialize simulation
    nSteps = 0
    maxSteps = int((opt.runtime * 60 * 1000) / epuck.timeStep)

    logger.info(f"TIME:{opt.runtime} min | STEP-TIME:{epuck.timeStep} ms => MAX-STEPS: {maxSteps}")

    # -------------------------------------------------

    nTouches = 0

    # Main loop:
    # - perform simulation steps until Webots is stopping the controller
    while epuck.robot.step(epuck.timeStep) != -1 and nSteps != maxSteps:
        
        # -------------------- PERFORM SIMULATION STEP ------------------------

        logger.info(f"step:{nSteps}")

        hasTouched = __step(opt)

        if (hasTouched): nTouches += 1

        # ~~~~~~~~~~~~~~~~~~~~~~~~~ LOGGING STUFF ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        coordinates = epuck.robot.getSelf().getField("translation").getSFVec3f()
        robotPosition = Position.fromTuple(coordinates)

        loghook(
            LogEntry(nSteps, hasTouched, 1 in ann.getLayerOutput(1).values(), robotPosition, nTouches)
        )

        nSteps += 1

        pass
    
    return TrainedModel(
        opt.version, 
        ann.getNetworkParams(), 
        ann.getConnectivities()
    )

#----------------------------------------------------------------------------------------------------
    
#----------------------------------------------------------------------------------------------------

def cleanup(opt: Options):

    # Cleanup code.
    epuck.motors['left'].device.setVelocity(0.0)
    epuck.motors['right'].device.setVelocity(0.0)

    epuck.robot.simulationSetMode(epuck.robot.SIMULATION_MODE_PAUSE)

    if opt.onTerminationQuit:
        epuck.robot.simulationQuit(1)
    else:
        epuck.robot.simulationReset()

# --------------------------------------------------------------------------------------------------------------------------------------