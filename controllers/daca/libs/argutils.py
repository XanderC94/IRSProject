from enum import Enum
import json

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
        with open(args['args'], "r") as config:
            opt = json.load(config)

    return opt
            
class Options(Enum):
    MODE = 'mode'
    TIME = 'time'
    VERSION = 'version'
    MODEL_DIR = 'modelPath'
    LOG_DIR = 'simulatioLogPath'
