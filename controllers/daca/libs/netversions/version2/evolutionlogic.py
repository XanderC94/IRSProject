import libs.annutils as ann
from libs.netversions.version2.neuralnetstructure import outputs
from libs.netversions.version2.neuralnetstructure import outputFunction
from libs.netversions.version2.neuralnetstructure import activationFunction
from libs.netversions.version2.neuralnetstructure import compositionFunction
from libs.netversions.version2.neuralnetstructure import connectivities
from libs.netversions.version2.neuralnetstructure import LEARNING_RATE, FORGET_RATE, COLLISION_THRESHOLD, MOTOR_THRESHOLD, REVERSE_THRESHOLD

from libs.motorresponse import wheelVelocity

def setNetworkParams(learningRate, forgetRate, collisionThreshold, motorThreshold, reverseThreshold):
    LEARNING_RATE = learningRate
    FORGET_RATE = forgetRate
    COLLISION_THRESHOLD = collisionThreshold
    MOTOR_THRESHOLD = motorThreshold
    REVERSE_THRESHOLD = reverseThreshold

def processProxymityLayer(distances):
    # DISTANCES_INPUT -> PROXIMITY  ---------------------------- LAYER 0

    layer = 0 

    hf = compositionFunction[layer]
    g = activationFunction[layer]
    f = outputFunction[layer]

    h_proximity = [ann.inputComposition(i = distances[n], o = [], w = [],h = hf) for n in range(0, len(distances))] # summed activations of each neuron in the Proximity Layer 0
    a_proximity = [ann.activationLevel(h_proximity[i], g) for i in range(0, len(h_proximity))] # activation level of each neuron in the Proximity Layer 0
    outputs[layer] = [ann.neuronOutput(a_proximity[i], f) for i in range(0, len(a_proximity))] # output level of each neuron that will be passed to the next layer
    
def processCollisionLayer(bumps):
    # COLLISIONS_INPUT, PROXIMITY -> COLLISION -------------------------- LAYER 1

    layer = 1 
    
    w = connectivities[layer]
    o = outputs[layer - 1] # Proximity Layer Output
    hf = compositionFunction[layer]
    g = activationFunction[layer]
    f = outputFunction[layer]

    h_collision = [ann.inputComposition(bumps[n], o, w[n], hf) for n in range(0, len(bumps))]
    a_collision = [ann.activationLevel(h_collision[i], g) for i in range(0, len(h_collision))]
    outputs[layer] = [ann.neuronOutput(a_collision[i], f) for i in range(0, len(a_collision))]

    print(f"Proximity Layer Output {o}")
    print(f"Weights Proximity to Collision:")
    for i in range(0, len(w)): print(w[i])
    print(f"Collision Layer Composed Input {h_collision}")

def processReverseLayer():
    # COLLISION -> REVERSE -----------------------------  LAYER 2

    layer = 2 

    #w = connectivities[layer]
    o = outputs[layer - 1] # Collision Layer Output
    hf = compositionFunction[layer]
    g = activationFunction[layer]
    f = outputFunction[layer]

    h_reverse = ann.sparseInputComposition([], o, connectivities[layer], hf)

    print(f"reverse layer composed input: {h_reverse}")

    a_reverse = [ann.activationLevel(h_reverse[i], g) for i in range(0,len(h_reverse))]

    outputs[layer] = [ann.neuronOutput(a_reverse[i], f) for i in range(0, len(a_reverse))]

def processMotorLayer():
   # COLLISION -> MOTORS -----------------------------  LAYER 3

    layer = 3

    #w = connectivities[layer]
    o = outputs[layer - 2] # Collision Layer Output
    r = outputs[layer - 1] # Reverse Layer Output
    hf = compositionFunction[layer]
    g = activationFunction[layer]
    f = outputFunction[layer]

    #Version 2 => 2 motor neuron
    h_motor = ann.sparseInputComposition([], o, connectivities[layer], hf)

    print(f"motor layer composed input: {h_motor}")

    a_motor = [ann.activationLevel(h_motor[i], g) for i in range(0,len(h_motor))]

    outputs[layer] = [ann.neuronOutput(a_motor[i], f) for i in range(0,len(a_motor))]

def processAnnState(distances:list, bumps:list): 
    # ~~~~~~~~~~~~~~~~~ PROCESS ANN STATE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    
    processProxymityLayer(distances)
    processCollisionLayer(bumps)
    processReverseLayer()
    processMotorLayer()
    #--------------------------------------------------------------

def updateWeights():
    # Now apply what It has learned
    # Weights Updates
    updatedWeights = ann.updateConnectivities(connectivities[1], outputs[1], outputs[0], LEARNING_RATE, FORGET_RATE)
    connectivities.update({1: updatedWeights})
    
def calculateMotorSpeed():
    print(f"Collision Layer output {outputs[1]}")
    reverseLayerOutput = outputs[2]
    motorLayerOutputs = outputs[3]
    print(f"Command Layer [Reverse] output {reverseLayerOutput}")
    print(f"Command Layer [Motor] output {motorLayerOutputs}")

    lv, rv = wheelVelocity(motorLayerOutputs[0], reverseLayerOutput[0], motorLayerOutputs[1])
    return lv,rv