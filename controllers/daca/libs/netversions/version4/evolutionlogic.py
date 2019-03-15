import libs.annutils as annutils
from libs.utils import NetParameters
import libs.netversions.version4.neuralnetstructure as nns
from libs.log import logger
from libs.motorresponse import wheelVelocity

def setNetworkParameters(params: dict or NetParameters):

    if isinstance(params, dict): 

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

    elif isinstance(params, NetParameters):

        nns.LEARNING_RATE = params.learning_rate
        nns.FORGET_RATE = params.forget_rate
        nns.COLLISION_THRESHOLD = params.collision_threshold
        nns.MOTOR_THRESHOLD = params.motor_threshold
        nns.REVERSE_THRESHOLD = params.reverse_threshold

def getNetworkParams() -> dict:
    return {
        'learningRate':nns.LEARNING_RATE,
        'forgetRate':nns.FORGET_RATE,
        'collisionThreshold':nns.COLLISION_THRESHOLD,
        'motorThreshold':nns.MOTOR_THRESHOLD,
        'reverseThreshold':nns.REVERSE_THRESHOLD
    }

def setNetworkConnectivities(conn:dict):
    nns.connectivities = conn

def getConnectivities():
    return nns.connectivities

def processProximityLayer(distances: list):
    # DISTANCES_INPUT -> PROXIMITY  ---------------------------- LAYER 0
    
    i = [distances[i] for i in nns.active_ps]
    
    layer = 0 

    hf = nns.compositionFunction[layer]
    g = nns.activationFunction[layer]
    f = nns.outputFunction[layer]

    # summed activations of each neuron in the Proximity Layer 0
    h_proximity = annutils.layerInputComposition(i = i, o = [], w = [], h = hf)
    # activation level of each neuron in the Proximity Layer 0
    a_proximity = annutils.layerActivationLevel(h_proximity, g)
    # output level of each neuron that will be passed to the next layer
    nns.outputs[layer] = annutils.sparseArray(
        list(nns.outputs[layer].keys()),
        annutils.layerOutput(a_proximity, f)
    )

    logger.info(f"Proximity Layer Output {nns.outputs[layer]}")
    
def processCollisionLayer(bumps : list):
    # COLLISIONS_INPUT, PROXIMITY -> COLLISION -------------------------- LAYER 1
    
    i = [bumps[i] for i in nns.active_ts]

    layer = 1 

    w = nns.connectivities[layer]
    # Proximity Layer Output
    o = nns.outputs[layer - 1]
    hf = nns.compositionFunction[layer]
    g = nns.activationFunction[layer]
    f = nns.outputFunction[layer]

    h_collision = annutils.sparseLayerInputComposition(i, o, w, hf)
    a_collision = annutils.layerActivationLevel(h_collision, g)
    nns.outputs[layer] = annutils.sparseArray(
        list(nns.outputs[layer].keys()), 
        annutils.layerOutput(a_collision, f)
    )

    logger.info(f"Collision Layer Composed Input: {h_collision}")
    logger.info(f"Weights Proximity to Collision:")
    for n, conn in w.items(): logger.info(f"{n}->{conn}")
    logger.info(f"Collision Layer Output: {nns.outputs[layer]}")

def processReverseLayer():
    # COLLISION -> REVERSE -----------------------------  LAYER 2
    
    i = []
    
    layer = 2

    w = nns.connectivities[layer]
    # Collision Layer Output
    o = nns.outputs[layer - 1]
    hf = nns.compositionFunction[layer]
    g = nns.activationFunction[layer]
    f = nns.outputFunction[layer]

    h_reverse = annutils.sparseLayerInputComposition(i, o, w, hf)
    a_reverse = annutils.layerActivationLevel(h_reverse, g)
    nns.outputs[layer] = annutils.sparseArray(
        list(nns.outputs[layer].keys()), 
        annutils.layerOutput(a_reverse, f)
    )
    
    logger.info(f"Reverse Layer Composed Input: {h_reverse}")
    logger.info(f"Reverse Layer Output: {nns.outputs[layer]}")

def processMotorLayer():
    # COLLISION -> MOTORS -----------------------------  LAYER 3

    i = []

    layer = 3

    w = nns.connectivities[layer]
    o = nns.outputs[layer - 2] # Collision Layer Output
    hf = nns.compositionFunction[layer]
    g = nns.activationFunction[layer]
    f = nns.outputFunction[layer]

    h_motor = annutils.sparseLayerInputComposition(i, o, w, hf)
    a_motor = annutils.layerActivationLevel(h_motor, g)
    nns.outputs[layer] = annutils.sparseArray(
        list(nns.outputs[layer].keys()),
        annutils.layerOutput(a_motor, f)
    )
    logger.info(f"Motor Layer Composed Input: {h_motor}")
    logger.info(f"Motor Layer Output: {nns.outputs[layer]}")

def processAnnState(distances:list, bumps:list): 
    # ~~~~~~~~~~~~~~~~~ PROCESS ANN STATE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    
    processProximityLayer(distances)
    processCollisionLayer(bumps)
    processReverseLayer()
    processMotorLayer()
    #--------------------------------------------------------------

def updateWeights():
    # Now apply what It has learned
    # Weights Updates
    proxOut = nns.outputs[0]
    collOut = nns.outputs[1]
    
    updatedWeights = annutils.updateSparseConnectivities(nns.connectivities[1], collOut, proxOut, nns.LEARNING_RATE, nns.FORGET_RATE)
    nns.connectivities.update({1: updatedWeights})
    
def calculateMotorSpeed():
    
    reverseLayerOutput = nns.outputs[2]
    motorLayerOutputs = nns.outputs[3]

    lv, rv = wheelVelocity(motorLayerOutputs[0], reverseLayerOutput[0], motorLayerOutputs[1])
    return lv,rv