from enum import Enum


class LearningParameters:
    LEARNING_RATE = "learningRate"
    FORGET_RATE = "forgetRate"
    COLLISION_THRESHOLD = "collisionThreshold"
    MOTOR_THRESHOLD = "motorThreshold"
    REVERSE_THRESHOLD = "reverseThreshold"

    def __init__(self, learningRate, forgetRate, collisionThreshold, motorThreshold, reverseThreshold):
        self.learningRate = learningRate
        self.forgetRate = forgetRate
        self.collisionThreshold = collisionThreshold
        self.motorThreshold = motorThreshold
        self.reverseThreshold = reverseThreshold
    
    def setParameter(self, parameter: str, value: float):
        if parameter == LearningParameters.LEARNING_RATE:
            self.learningRate = value
        elif parameter == LearningParameters.FORGET_RATE:
            self.forgetRate = value
        elif parameter ==  LearningParameters.COLLISION_THRESHOLD:
            self.collisionThreshold = value
        elif parameter == LearningParameters.MOTOR_THRESHOLD:
            self.motorThreshold = value
        elif parameter == LearningParameters.REVERSE_THRESHOLD:
            self.reverseThreshold = value
            pass

