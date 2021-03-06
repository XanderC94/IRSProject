import json, sys, json
from pathlib import Path
from libs.log import logger
import libs.utils as utils

class Options:

    def __init__(self, opt:dict):
        
        self.version = 2

        if 'version' in opt:
            self.version = opt['version']
        
        self.versionList = [2]
        if 'versionList' in opt:
            self.versionList = opt['versionList']

        self.runtime = -1 # minutes, -1 -> Infinite
        if 'time' in opt:
            self.runtime = opt['time']

        self.modelPath = Path('')
        if 'modelPath' in opt:
            self.modelPath = Path(opt['modelPath'])
        
        self.isTrainingModeActive = True

        self.executionMode = "train"
        self.trainedModel = None
        if 'mode' in opt:
            self.executionMode = opt['mode']
            if 'test' in opt['mode'].lower():
                self.isTrainingModeActive = False

                if not self.modelPath.is_dir():
                    self.trainedModel = utils.loadTrainedModel(self.modelPath)
                    self.version = self.trainedModel.version

        self.simulationLogPath = ""
        if 'simulationLogPath' in opt:
            self.simulationLogPath = opt['simulationLogPath']
        
        if 'logging' in opt:
            logger.suppress(not opt['logging'])

        self.changingInfo = None
        if 'changingInfo' in opt:
            self.changingInfo = opt['changingInfo']

        self.parameters = {}
        if 'parameters' in opt:
            self.parameters = opt['parameters']

        self.webotsExecutablePath = ""
        if 'webotsExecutablePath' in opt:
            self.webotsExecutablePath = Path(opt['webotsExecutablePath'])
        
        self.onTerminationQuit = True
        if 'onTerminationQuit' in opt:
            self.onTerminationQuit = opt['onTerminationQuit']

        self.worldTrainPath = ""
        if 'worldTrainPath' in opt:
            self.worldTrainPath = opt['worldTrainPath']

        self.worldTestPath = ""
        if 'worldTestPath' in opt:
            self.worldTestPath = opt['worldTestPath']

    @staticmethod
    def fromArgv(argv:list):
        return Options(parseArgs(argv))

    def __str__(self):
        return f'{self.__dict__}'

def parseArgs(argv):
    args = {}
    for arg in argv:
        if (arg.startswith("--")): 
            v = arg.split("=")
            key = v[0].replace("--", "")
            value = v[1]
            args.update({key:value})

    opt = {}

    if 'args' in args:
        with open(Path(args['args']), "r") as config:
            opt = json.load(config)

    return opt

opt = Options.fromArgv(sys.argv)
