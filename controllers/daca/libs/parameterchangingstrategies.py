from libs.learningparameters import *

class ParameterChanger:
    def __init__(self, parameters: LearningParameters, parameterToChange: str, minValue: float, maxValue: float, changeStep: float):
        self.parameters = parameters
        self.parameterToChange =  parameterToChange
        self.minValue =  minValue * 100
        self.maxValue = maxValue * 100
        self.currentValue = self.minValue 
        self.changeStep = changeStep * 100
        self.hasEnded = False
        self.parameters.setParameter(self.parameterToChange, self.currentValue / 100)


    def updateParameter(self):
        if self.currentValue == self.maxValue:
            self.hasEnded = True

        if self.currentValue + self.changeStep < self.maxValue:
            self.currentValue += self.changeStep
        else:
            self.currentValue = self.maxValue 
        self.parameters.setParameter(self.parameterToChange, (self.currentValue / 100).__round__(2))

    
    def hasEnded(self):
        return self.hasEnded

    @staticmethod
    def fromConfig(currentParameters:LearningParameters, changingInfo: dict):
        return ParameterChanger(currentParameters, 
        changingInfo["parameter"], 
        changingInfo["minVal"], 
        changingInfo["maxVal"], 
        changingInfo["changeStep"])