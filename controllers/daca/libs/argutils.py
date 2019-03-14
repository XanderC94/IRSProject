from enum import Enum

def parseArgs(argv):
    opt = {}
    for arg in argv:
        if (arg.startswith("--")): 
            v = arg.split("=")
            key = v[0].replace("--", "")
            value = convertValue(v[1])
            opt.update({key:value})
    return opt

def convertValue(value):

    if value.lower == 'true' or value.lower == 'false':
        return bool(value)
    else:
        try:
            return int(value)    
        except ValueError:
            try:
                return float(value)    
            except ValueError:
                return value
            
class Options(Enum):
    MODE = 'mode'
    TIME = 'time'
    VERSION = 'version'
    MODEL_DIR = 'modelDirectory'
