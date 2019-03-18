class LearningParameters:
    LEARNING_RATE = "learningRate"
    FORGET_RATE = "forgetRate"
    COLLISION_THRESHOLD = "collisionThreshold"
    MOTOR_THRESHOLD = "motorThreshold"
    REVERSE_THRESHOLD = "reverseThreshold"

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

