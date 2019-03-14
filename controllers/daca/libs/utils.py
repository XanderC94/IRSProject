import json

class NetParameters:
    def __init__(self, 
    collision_treshold: float,  
    learning_rate: float,
    forget_rate: float,
    motor_threshold: int,
    reverse_threshold: int):
        self.collision_treshold = collision_treshold
        self.learning_rate = learning_rate
        self.forget_rate = forget_rate
        self.motor_threshold = motor_threshold
        self.reverse_threshold = reverse_threshold
    def __str__(self):
        return (f" collision_treshold: {self.collision_treshold}, learning_rate: {self.learning_rate}, forget_rate: {self.forget_rate}, motor_threshold:  {self.motor_threshold}, reverse_threshold: {self.reverse_threshold}")

class TrainedModel:
    def __init__(self, version_name: str, parameters: NetParameters, connectivities: dict):
        self.version_name = version_name
        self.parameters = parameters
        self.connectivities = connectivities
    def __str__(self):
        return "Model version name: " + self.version_name + ", Parameters: " + str(self.parameters) + ", Connectivities: " + str(self.connectivities)


def saveTrainedModel(model: TrainedModel, directoryPath: str) -> str:
    model_name = directoryPath + model.version_name + ".json"
    with open(model_name, 'w') as outfile:
        json.dump(model.__dict__, outfile, default= lambda x: x.__dict__)
    return model_name



def recursiveExtractDictWithIntKey(json)-> dict:
    connectivities = {}
    for K,V in json.items():
        if isinstance(V, dict):
            connectivities.update({int(K): recursiveExtractDictWithIntKey(V)})
        else:
            connectivities.update({int(K): V})
    return connectivities


def loadTrainedModel(model_file_name: str) -> TrainedModel:
    loaded_json = None
    with open(model_file_name, 'r') as json_data:
        loaded_json = json.load(json_data)
    loaded_parameters = NetParameters(loaded_json["parameters"]["collision_treshold"],
    loaded_json["parameters"]["learning_rate"],
    loaded_json["parameters"]["forget_rate"],
    loaded_json["parameters"]["motor_threshold"],
    loaded_json["parameters"]["reverse_threshold"])
    connectivities = recursiveExtractDictWithIntKey(loaded_json["connectivities"])
    return TrainedModel(loaded_json["version_name"], loaded_parameters, connectivities)



class Position:
    def __init__(self, X, Y):
        self.X = X
        self.Y = Y

class LogEntry:
    def __init__(self, step_number: int, touched: bool, position: Position):
        self.step_number = step_number
        self.touched = touched
        self.position = position

class SimulationLog:
    def __init__(self, model_name: str, log: list = []):
        self.model_name=model_name;
        self.log = log

    def addLogEntry(entry: LogEntry):
        self.log.append(entry)


def saveSimulationLog(log:SimulationLog, directoryPath: str) -> str:
    file_name = f"{directoryPath}SimLog{log.model_name}.json"
    with open(file_name, 'w') as outfile:
        json.dump(log.__dict__, outfile, default= lambda x: x.__dict__)
    return file_name
