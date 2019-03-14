import libs.annutils as annutils
from libs.utils import NetParameters
import libs.netversions.version2.neuralnetstructure as nns

from libs.motorresponse import wheelVelocity

def setNetworkParameters(params: dict or NetParameters):

    if params is dict: 

        if 'learningRate' in params:
            nns.LEARNING_RATE = params['learningRate']
        if 'forgetRate' in params:
            nns.FORGET_RATE = params['forgetRate']
        if 'collisionThreshold' in params:
            nns.COLLISION_THRESHOLD = params['collisionThreshold']
        if 'motorThreshold' in params:
            nns.MOTOR_THRESHOLD = params['motorThreshold']
        if 'reverseThreshold' in params:
            nns.REVERSE_THRESHOLD = params['reverseThreshold']

    elif params is NetParameters:

        nns.LEARNING_RATE = params.learning_rate
        nns.FORGET_RATE = params.forget_rate
        nns.COLLISION_THRESHOLD = params.collision_threshold
        nns.MOTOR_THRESHOLD = params.motor_threshold
        nns.REVERSE_THRESHOLD = params.reverse_threshold

def setNetworkConnectivities(conn:dict):
    nns.connectivities = conn

def processProxymityLayer(distances):
    # DISTANCES_INPUT -> PROXIMITY  ---------------------------- LAYER 0

    layer = 0 

    hf = nns.compositionFunction[layer]
    g = nns.activationFunction[layer]
    f = nns.outputFunction[layer]

    h_proximity = [annutils.inputComposition(i = distances[n], o = [], w = [],h = hf) for n in range(0, len(distances))] # summed activations of each neuron in the Proximity Layer 0
    a_proximity = [annutils.activationLevel(h_proximity[i], g) for i in range(0, len(h_proximity))] # activation level of each neuron in the Proximity Layer 0
    nns.outputs[layer] = [annutils.neuronOutput(a_proximity[i], f) for i in range(0, len(a_proximity))] # output level of each neuron that will be passed to the next layer
    
def processCollisionLayer(bumps):
    # COLLISIONS_INPUT, PROXIMITY -> COLLISION -------------------------- LAYER 1

    layer = 1 
    
    w = nns.connectivities[layer]
    o = nns.outputs[layer - 1] # Proximity Layer Output
    hf = nns.compositionFunction[layer]
    g = nns.activationFunction[layer]
    f = nns.outputFunction[layer]

    h_collision = [annutils.inputComposition(bumps[n], o, w[n], hf) for n in range(0, len(bumps))]
    a_collision = [annutils.activationLevel(h_collision[i], g) for i in range(0, len(h_collision))]
    nns.outputs[layer] = [annutils.neuronOutput(a_collision[i], f) for i in range(0, len(a_collision))]

    print(f"Proximity Layer Output {o}")
    print(f"Weights Proximity to Collision:")
    for i in range(0, len(w)): print(w[i])
    print(f"Collision Layer Composed Input {h_collision}")

def processReverseLayer():
    # COLLISION -> REVERSE -----------------------------  LAYER 2

    layer = 2 

    #w = connectivities[layer]
    o = nns.outputs[layer - 1] # Collision Layer Output
    hf = nns.compositionFunction[layer]
    g = nns.activationFunction[layer]
    f = nns.outputFunction[layer]

    h_reverse = annutils.sparseInputComposition([], o, nns.connectivities[layer], hf)

    print(f"reverse layer composed input: {h_reverse}")

    a_reverse = [annutils.activationLevel(h_reverse[i], g) for i in range(0,len(h_reverse))]

    nns.outputs[layer] = [annutils.neuronOutput(a_reverse[i], f) for i in range(0, len(a_reverse))]

def processMotorLayer():
   # COLLISION -> MOTORS -----------------------------  LAYER 3

    layer = 3

    #w = connectivities[layer]
    o = nns.outputs[layer - 2] # Collision Layer Output
    r = nns.outputs[layer - 1] # Reverse Layer Output
    hf = nns.compositionFunction[layer]
    g = nns.activationFunction[layer]
    f = nns.outputFunction[layer]

    #Version 2 => 2 motor neuron
    h_motor = annutils.sparseInputComposition([], o, nns.connectivities[layer], hf)

    print(f"motor layer composed input: {h_motor}")

    a_motor = [annutils.activationLevel(h_motor[i], g) for i in range(0,len(h_motor))]

    nns.outputs[layer] = [annutils.neuronOutput(a_motor[i], f) for i in range(0,len(a_motor))]

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
    updatedWeights = annutils.updateConnectivities(nns.connectivities[1], nns.outputs[1], nns.outputs[0], nns.LEARNING_RATE, nns.FORGET_RATE)
    nns.connectivities.update({1: updatedWeights})
    
def calculateMotorSpeed():
    print(f"Collision Layer output {nns.outputs[1]}")
    reverseLayerOutput = nns.outputs[2]
    motorLayerOutputs = nns.outputs[3]
    print(f"Command Layer [Reverse] output {reverseLayerOutput}")
    print(f"Command Layer [Motor] output {motorLayerOutputs}")

    lv, rv = wheelVelocity(motorLayerOutputs[0], reverseLayerOutput[0], motorLayerOutputs[1])
    return lv,rv