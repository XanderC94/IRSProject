import json, datetime, logging
from  libs.learningparameters  import * 
from pathlib import Path


class TrainedModel:
    def __init__(self, version: int, parameters: LearningParameters, connectivities: dict):
        self.version = version
        self.parameters = parameters
        self.connectivities = connectivities

    def __str__(self):
        return "Model version name: " + str(self.version) + ", Parameters: " + str(self.parameters) + ", Connectivities: " + str(self.connectivities)
    
    @classmethod
    def emptyModel(cls):
        return TrainedModel("", LearningParameters(0,0,0,0,0), {})

def generateFileName(model: TrainedModel):
    return f"Model_AnnV{model.version}-{datetime.datetime.now():%Y-%m-%dT%H-%M-%S}g"

def writeModelOnFile(model: TrainedModel, file_path: str):
    with open(file_path, 'w') as outfile:
        json.dump(model.__dict__, outfile, indent=4, default= lambda x: x.__dict__)

def saveTrainedModel(model: TrainedModel, directoryPath: str):
    file_path = f"{directoryPath}{generateFileName(model)}.json"
    writeModelOnFile(model, file_path)


def recursiveExtractDictWithIntKey(json)-> dict:
    connectivities = {}
    for K,V in json.items():
        if isinstance(V, dict):
            connectivities.update({int(K): recursiveExtractDictWithIntKey(V)})
        else:
            connectivities.update({int(K): V})
    return connectivities


def loadTrainedModel(path: str) -> TrainedModel:
    
    loaded_json = {}

    with open(path, 'r') as json_data:
        loaded_json = json.load(json_data)

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
    
    def __init__(self, version: int, mode:str, time: int, relative_model: TrainedModel = TrainedModel.emptyModel(), log: list = []):
        self.version = version
        self.mode = mode
        self.time = time
        self.log = log
        self.relative_model = relative_model

    def addLogEntry(self, entry: LogEntry):
        self.log.append(entry)

    def setRelativeModel(self, relative_model: TrainedModel):
        self.relative_model = relative_model

    def saveTo(self, directoryPath: str) -> str:

        model_name = Path(self.model).with_suffix('').name
        file_name = f"{directoryPath}SimLog_v{self.version}-{self.mode}-{model_name}-{datetime.datetime.now():%Y-%m-%dT%H-%M-%S}g.json"
        print(file_name)
        with open(file_name, 'w') as outfile:
            json.dump(self.__dict__, outfile, indent=4, default= lambda x: x.__dict__)
        return file_name
