"""daca controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, LED, DistanceSensor
# from controller import *
import sys, os, copy

print(os.getcwd())

import libs.epuck as epuck
from libs.argutils import opt, Options
import libs.utils as utils
from libs.log import logger
import libs.simulation as simulation

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

# Setup ------------------------------------

# See libs.epuck

#-------------------------------------------

if not opt.isTrainingModeActive:

    if opt.modelPath.is_dir():
        raise Exception('Test model is not a file!')
    elif not ('json' in opt.modelPath.suffix):
        raise Exception('Test model is not a JSON file!')

    model = utils.loadTrainedModel(opt.modelPath)
    ann.setNetworkParameters(model.parameters)
    ann.setNetworkConnectivities(model.connectivities)

elif len(opt.parameters) > 0:
    ann.setNetworkParameters(opt.parameters)
    
logger.info(f"params:{ann.getNetworkParams()}")

print(ann.getNetworkParams())

log = utils.SimulationLog(opt.executionMode, opt.runtime)

model = simulation.run(opt, loghook = lambda e: log.addLogEntry(e))

if opt.isTrainingModeActive:
    utils.saveTrainedModel(model, opt.modelPath)

log.setModel(model)
log.saveTo(opt.simulationLogPath)

logger.flush()

# Cleanup code.

simulation.cleanup(opt)

# --------------------------------------------------------------------------------------------------------------------------------------