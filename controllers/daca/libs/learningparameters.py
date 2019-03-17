from enum import Enum


class LearningParameters:
    COLLISION_THRESHOLD = "collision_threshold"
    LEARNING_RATE = "learning_rate"
    FORGET_RATE = "forget_rate"
    
    def __init__(self, collision_threshold, learning_rate, forget_rate):
        self.collision_threshold = collision_threshold
        self.learning_rate = learning_rate
        self.forget_rate = forget_rate
    
    def setParameter(self, parameter: str, value: float):
        if parameter ==  LearningParameters.COLLISION_THRESHOLD:
            self.collision_threshold = value
        elif parameter == LearningParameters.LEARNING_RATE:
            self.learning_rate = value
        elif parameter == LearningParameters.FORGET_RATE:
            self.forget_rate = value
            pass

