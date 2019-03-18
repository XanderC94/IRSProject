class LearningParameters:
    LEARNING_RATE_STR = "learningRate"
    FORGET_RATE_STR = "forgetRate"
    COLLISION_THRESHOLD_STR = "collisionThreshold"
    MOTOR_THRESHOLD_STR = "motorThreshold"
    REVERSE_THRESHOLD_STR = "reverseThreshold"

    def __init__(self, 
    learningRate: float,
    forgetRate: float,
    collisionThreshold: float,  
    motorThreshold: int,
    reverseThreshold: int):
        self.learningRate = learningRate
        self.forgetRate = forgetRate
        self.collisionThreshold = collisionThreshold
        self.motorThreshold = motorThreshold
        self.reverseThreshold = reverseThreshold

    def __str__(self):
        return (f"learningRate: {self.learningRate}, forgetRate: {self.forgetRate}, collisionThreshold: {self.collisionThreshold}, motorThreshold:  {self.motorThreshold}, reverseThreshold: {self.reverseThreshold}")

    @staticmethod
    def fromDict(params: dict):

        return LearningParameters(
            learningRate = params['learningRate'],
            forgetRate = params['forgetRate'],
            collisionThreshold = params['collisionThreshold'],
            motorThreshold = params['motorThreshold'],
            reverseThreshold = params['reverseThreshold']
        )

    def setParameter(self, parameter: str, value: float):
        if parameter == LearningParameters.LEARNING_RATE_STR:
            self.learningRate = value
        elif parameter == LearningParameters.FORGET_RATE_STR:
            self.forgetRate = value
        elif parameter ==  LearningParameters.COLLISION_THRESHOLD_STR:
            self.collisionThreshold = value
        elif parameter == LearningParameters.MOTOR_THRESHOLD_STR:
            self.motorThreshold = value
        elif parameter == LearningParameters.REVERSE_THRESHOLD_STR:
            self.reverseThreshold = value
            pass

    def toDict(self):
        return {
        LearningParameters.LEARNING_RATE_STR:self.learningRate,
        LearningParameters.FORGET_RATE_STR:self.forgetRate,
        LearningParameters.COLLISION_THRESHOLD_STR:self.collisionThreshold,
        LearningParameters.MOTOR_THRESHOLD_STR:self.motorThreshold,
        LearningParameters.REVERSE_THRESHOLD_STR:self.reverseThreshold
    }