import json
import datetime

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


def saveTrainedModel(model: TrainedModel, path: str) -> str:
    model_name = path + model.version_name + str(datetime.datetime.now()) + ".json"
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
    