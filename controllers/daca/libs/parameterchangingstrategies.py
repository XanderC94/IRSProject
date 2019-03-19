from libs.learningparameters import LearningParameters

def defaultChanging():
    return {
        'parameter':"",
        'minVal': 0.0,
        'maxVal': 0.0,
        'changeStep': 0.0
    }

ROUND_FACTOR = 3
MULT_FACTOR = 100

class Changer:

    def next(self) -> dict:
        return {}
    
    def hasNext(self) -> bool:
        return False
    
    def reset(self):
        pass

class ParameterChanger(Changer):
    

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

    def hasNext(self) -> bool:

        return self.currentValue < (self.maxValue + self.changeStep)

    def next(self) -> {str:float}:

        if self.hasNext():

            __retval = {self.parameterToChange: float(self.currentValue / MULT_FACTOR).__round__(ROUND_FACTOR)}
           
            self.currentValue = min(self.currentValue, self.maxValue) + self.changeStep
            
            return __retval

        else: raise Exception('Parameter Changer limit reached!')
    
    def reset(self):

        self.currentValue = self.minValue
        self.__hasEnded = False

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

class ParametersChanger(Changer):

    def __init__(self,  changer: ParameterChanger, chained: Changer):
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
    def fromList(params: LearningParameters, changers:list):
        
        if len(changers) > 0:
            changer = ParameterChanger.fromConfig(params, changers.pop())
            chained = ParametersChanger.fromList(params, changers)

            return ParametersChanger(changer, chained)
        else: return Changer()