from libs.learningparameters import LearningParameters
from libs.utils import TrainedModel, loadTrainedModel

def defaultChanging():
    return {
        'parameter':"",
        'minVal': 0.0,
        'maxVal': 0.0,
        'changeStep': 0.0
    }

ROUND_FACTOR = 3
MULT_FACTOR = 100


class ParameterChanger:
    
    def __init__(self, parameters: LearningParameters, parameterToChange: str, minValue: float, maxValue: float, changeStep: float):
        
        self.parameters = parameters
        self.parameterToChange =  parameterToChange
        
        self.changeStep = changeStep * MULT_FACTOR
        self.minValue =  minValue * MULT_FACTOR
        self.maxValue = maxValue * MULT_FACTOR
        self.currentValue = self.minValue 
        
        self.__hasEnded = False
        self.parameters.setParameter(self.parameterToChange, self.currentValue / MULT_FACTOR)

    def updateParameter(self):

        if self.currentValue == self.maxValue:
            self.__hasEnded = True

        if self.currentValue + self.changeStep < self.maxValue:
            self.currentValue += self.changeStep
        else:
            self.currentValue = self.maxValue

        self.parameters.setParameter(self.parameterToChange, (self.currentValue / MULT_FACTOR).__round__(ROUND_FACTOR))

    def hasEnded(self):

        return self.__hasEnded

    @staticmethod
    def fromConfig(currentParameters:LearningParameters, changingInfo: dict):

        return ParameterChanger(currentParameters, 
            changingInfo["parameter"], 
            changingInfo["minVal"], 
            changingInfo["maxVal"], 
            changingInfo["changeStep"]
        )

# -------------------------------------------------------------------------------------------------------------------------------

class Changer:

    def next(self) -> dict:
        return {}
    
    def hasNext(self) -> bool:
        return False
    
    def reset(self):
        pass

class ModelChanger(Changer):
    def __init__(self, trainedModels:list):
        self._trainedModels = trainedModels
        self._elementPointer = 0

    def hasNext(self) -> bool:
        return self._elementPointer < len(self._trainedModels)

    def next(self) -> {TrainedModel}:

        if self.hasNext():

            __retval = self._trainedModels[self._elementPointer]
            
            self._elementPointer += 1
            
            return {__retval}

        else: raise Exception('Parameter Changer limit reached!')

    def reset(self):
        self._elementPointer = 0

    @staticmethod
    def createFromFilePaths(files: list):
        return ModelChanger(list(loadTrainedModel(f) for f in files))


class ChangeStrategy(Changer):

    def __init__(self, parameter: str, minValue: float, maxValue: float, step: float, bounded = True):
        
        self.parameter =  parameter
        
        self.bounded = bounded

        self.step = step * MULT_FACTOR
        self.minValue =  minValue * MULT_FACTOR
        self.maxValue = maxValue * MULT_FACTOR
        
        self.currentValue = self.minValue 

    def __max(self) -> float:
        return self.maxValue if self.bounded else (self.maxValue + self.step)

    def __eval(self) -> float:
        return min(self.currentValue, self.maxValue) / MULT_FACTOR

    def hasNext(self) -> bool:
        return self.currentValue < self.__max()
    
    def next(self) -> {str:float}:

        if self.hasNext():

            __retval = self.__eval().__round__(ROUND_FACTOR)
            
            self.currentValue += self.step
            
            return {self.parameter:__retval}

        else: raise Exception('Parameter Changer limit reached!')
    
    def reset(self):
        self.currentValue = self.minValue

    @staticmethod
    def fromConfig(changingInfo: dict, bounded = True):

        return ChangeStrategy( 
            changingInfo["parameter"], 
            changingInfo["minVal"], 
            changingInfo["maxVal"], 
            changingInfo["changeStep"],
            bounded = bounded
        )

class ParametersChanger(Changer):

    def __init__(self,  changer: Changer, chained: Changer = Changer()):
        self.changer = changer
        self.chained = chained
        self.__next = {} if not chained.hasNext() else changer.next()
        
    def next(self) -> dict:
                
        if self.hasNext():
                            
            if not self.chained.hasNext():
                self.chained.reset()
                self.__next = self.changer.next()
            
            self.__next.update(self.chained.next())

            return self.__next
        else:
            raise Exception('Parameter Changer limit reached!')
    
    def hasNext(self) -> bool:
        return self.changer.hasNext() or self.chained.hasNext()

    def reset(self):
        self.changer.reset()
        
    @staticmethod
    def fromList(changers:list, bounded = True):
        
        if len(changers) > 0:
            changer = ChangeStrategy.fromConfig(changers.pop(), bounded = bounded)
            chained = ParametersChanger.fromList(changers, bounded = bounded)

            return ParametersChanger(changer, chained)
        else: return Changer()