import json, datetime, logging

class NetParameters:
    
    def __init__(self, 
    collision_threshold: float,  
    learning_rate: float,
    forget_rate: float,
    motor_threshold: int,
    reverse_threshold: int):
        self.collision_threshold = collision_threshold
        self.learning_rate = learning_rate
        self.forget_rate = forget_rate
        self.motor_threshold = motor_threshold
        self.reverse_threshold = reverse_threshold

    def __str__(self):
        return (f" collision_treshold: {self.collision_threshold}, learning_rate: {self.learning_rate}, forget_rate: {self.forget_rate}, motor_threshold:  {self.motor_threshold}, reverse_threshold: {self.reverse_threshold}")

    @staticmethod
    def fromDict(params: dict):

        return NetParameters(
            learning_rate = params['learningRate'],
            forget_rate = params['forgetRate'],
            collision_threshold = params['collisionThreshold'],
            motor_threshold = params['motorThreshold'],
            reverse_threshold = params['reverseThreshold']
        )

class TrainedModel:
    def __init__(self, version_name: str, parameters: NetParameters, connectivities: dict):
        self.version_name = version_name
        self.parameters = parameters
        self.connectivities = connectivities
    def __str__(self):
        return "Model version name: " + self.version_name + ", Parameters: " + str(self.parameters) + ", Connectivities: " + str(self.connectivities)


def saveTrainedModel(model: TrainedModel, path: str):
   
    with open(path, 'w') as outfile:
        json.dump(model.__dict__, outfile, indent=4, default= lambda x: x.__dict__)


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

    loaded_parameters = NetParameters(loaded_json["parameters"]["collision_treshold"],
    loaded_json["parameters"]["learning_rate"],
    loaded_json["parameters"]["forget_rate"],
    loaded_json["parameters"]["motor_threshold"],
    loaded_json["parameters"]["reverse_threshold"])
    
    connectivities = recursiveExtractDictWithIntKey(loaded_json["connectivities"])
    return TrainedModel(loaded_json["version_name"], loaded_parameters, connectivities)



class Position:

    def __init__(self, X:float, Y:float, Z:float):
        self.X = X
        self.Y = Y
        self.Z = Z

    @staticmethod
    def fromTuple(coordinates: list or (float, float, float)):
        return Position(coordinates[0], coordinates[1], coordinates[2])

class LogEntry:

    def __init__(self, step_number: int, touched: bool, position: Position, nTouches: int):

        self.step_number = step_number
        self.touched = touched
        self.position = position
        self.nTouches = nTouches


class DACLogger:

    def __init__(self, name : str, path: str = ""):

        self.logger = logging.getLogger(name)

        formatter = logging.Formatter('%(message)s')

        if len(path) > 0:
            fh = logging.FileHandler(path)
            fh.setLevel(logging.INFO)
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)
    
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)

class SimulationLog:
    
    def __init__(self, model_name: str, log: list = []):
        self.model_name=model_name
        self.log = log

    def addLogEntry(self, entry: LogEntry):
        self.log.append(entry)

    def saveTo(self, directoryPath: str) -> str:
        file_name = f"{directoryPath}SimLog{self.model_name}-{datetime.datetime.now():%Y-%m-%dT%H-%M-%S}g.json"
        with open(file_name, 'w') as outfile:
            json.dump(self.__dict__, outfile, indent=4, default= lambda x: x.__dict__)
        return file_name
