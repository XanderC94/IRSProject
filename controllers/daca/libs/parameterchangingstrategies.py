from libs.learningparameters import *

class ParameterChanger:
    def __init__(self, parameters: LearningParameters, parameterToChange: str, minValue: float, maxValue: float, changeStep: float):
        self.parameters = parameters
        self.parameterToChange =  parameterToChange
        self.minValue =  minValue
        self.maxValue = maxValue
        self.currentValue = minValue
        self.changeStep = changeStep
        self.hasEnded = False


    def updateParameter(self):
        if self.currentValue + self.changeStep <= self.maxValue:
            self.currentValue += self.changeStep
        else:
            self.currentValue = self.maxValue 
            self.hasEnded = True
        self.parameters.setParameter(self.parameterToChange, self.currentValue)

    
    def hasEnded(self):
        return self.hasEnded

    @staticmethod
    def fromConfig(currentParameters:LearningParameters, changingInfo: dict):
        return ParameterChanger(currentParameters, 
        changingInfo["parameter"], 
        changingInfo["minVal"], 
        changingInfo["maxVal"], 
        changingInfo["changeStep"])