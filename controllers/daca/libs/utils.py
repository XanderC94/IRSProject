import json, datetime, logging, pathlib
from  libs.learningparameters  import LearningParameters 
from pathlib import Path
from glob import glob


class TrainedModel:

    def __init__(self, version: int, parameters: LearningParameters, connectivities: dict):
        self.version = version
        self.parameters = parameters
        self.connectivities = connectivities

    def __str__(self):
        return f"ANN Version: {self.version}, Parameters: {self.parameters}, Connectivities: {self.connectivities}"
    
    @staticmethod
    def emptyModel():
        return TrainedModel(0, LearningParameters(0,0,0,0,0), {})

def generateFileName(mode: str, model: TrainedModel):
    p = model.parameters
    pstr = f'lr{p.learningRate}.fr{p.forgetRate}.ct{p.collisionThreshold}'
    date = f'{datetime.datetime.now():%Y-%m-%dT%H-%M-%S}'
    return f"annv{model.version}.{mode}.{pstr}.{date}"

def writeJsonOnFile(json: dict, file_path: str):
    with open(file_path, 'w') as outfile:
        json.dump(json, outfile)

def writeModelOnFile(model: TrainedModel, file_path: str):
    with open(file_path, 'w') as outfile:
        json.dump(model.__dict__, outfile, indent=4, default= lambda x: x.__dict__)

def saveTrainedModel(model: TrainedModel, directoryPath: str):
    file_path = f"{directoryPath}model.{generateFileName('train',model)}.json"
    writeModelOnFile(model, file_path)

def recursiveExtractDictWithIntKey(json)-> dict:
    connectivities = {}
    for K,V in json.items():
        if isinstance(V, dict):
            connectivities.update({int(K): recursiveExtractDictWithIntKey(V)})
        else:
            connectivities.update({int(K): V})
    return connectivities

def loadJsonFile(path: str) -> dict:
    loaded_json = {}

    with open(path, 'r') as json_data:
        loaded_json = json.load(json_data)

    return loaded_json

def loadTrainedModel(path: str) -> TrainedModel:
    
    loaded_json = loadJsonFile(path)

    loaded_parameters = LearningParameters(loaded_json["parameters"]["learningRate"],
    loaded_json["parameters"]["forgetRate"],
    loaded_json["parameters"]["collisionThreshold"],
    loaded_json["parameters"]["motorThreshold"],
    loaded_json["parameters"]["reverseThreshold"])
    
    connectivities = recursiveExtractDictWithIntKey(loaded_json["connectivities"])
    return TrainedModel(loaded_json["version"], loaded_parameters, connectivities)

class Position:

    def __init__(self, X:float, Y:float, Z:float):
        self.X = X
        self.Y = Y
        self.Z = Z

    @staticmethod
    def fromTuple(coordinates: list or (float, float, float)):
        return Position(coordinates[0], coordinates[1], coordinates[2])

class LogEntry:

    def __init__(self, 
    step_number: int, 
    collision: bool,
    activation : bool, 
    position: Position, 
    nTouches: int):

        self.step_number = step_number
        self.collision = collision
        self.position = position
        self.nTouches = nTouches
        self.activation = activation

class SimulationLog:
    
    def __init__(self, mode:str, time: int, model: TrainedModel = TrainedModel.emptyModel(), log: list = []):
        
        self.mode = mode
        self.time = time
        self.model = model
        self.log = log

    def addLogEntry(self, entry: LogEntry):
        self.log.append(entry)

    def setModel(self, model: TrainedModel):
        self.model = model

    def saveTo(self, directoryPath: str) -> str:

        file_name = Path(directoryPath) / f"simlog.{generateFileName(self.mode, self.model)}.json"
        
        with open(file_name, 'w') as outfile:
            json.dump(self.__dict__, outfile, indent=4, default= lambda x: x.__dict__)

        self.log.clear()
        
        return file_name
    
    def clear(self):
        self.log.clear()

def getAllFilesIn(target:str or Path, extension:str) -> list:

    path = target if isinstance(target, Path) else Path(target)

    return filter(
        lambda f: extension in f.suffix,
        [item for item in path.iterdir()] if path.is_dir() else [path]
    )
    # return (glob(f"{target}*.{extension}"))
