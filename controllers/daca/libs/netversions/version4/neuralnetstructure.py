from libs.epuck import nBumpers, nDistanceSensors, nMotors, nLightSensors, MIN_V
import libs.annutils as annutils
from libs.learningparameters import *

# Learning Parameters #########################

learningParameters = LearningParameters(0.05, 0.8, 0.65, 1, 2)

#~~~~~~~~~~~~~ NETWORK STRUCTURE - Version 4  ~~~~~~~~~~~~~~~~~~~~~
# Rear bumpers and distance sensors are disconnected

# active_ps = [0, 1, 2, 3, 4, 5, 6, 7] # v2
# active_ts = [0, 1, 2, 3, 4, 5, 6, 7] # v2
active_ps = [0, 1, 2, 5, 6, 7] # v4
active_ts = [0, 1, 2, 5, 6, 7] # v4

# motor_config = [[4, 5, 6, 7], [0, 1, 2, 3]] # v2
motor_config = [[5, 6, 7], [0, 1, 2]] # v4

_proximityToCollisionConnections = annutils.fullyConnected(active_ts, active_ps)

_collisionToReverseConnections = annutils.sparselyConnected([0], [[0, 7]], gen = lambda:1.0)
    
_collisionToMotorConnections = annutils.sparselyConnected(range(0, nMotors), motor_config, gen = lambda:1.0)

# Connectivity Matrices
# for each neuron of layer[j] the matrix holds the weights to each neuron of level[i = j - 1]
# in the form of neuron[n] of layer[j] -> [ w[n][0], ..., w[n][m] ] of neuron[0...m] of layer[i]
connectivities = {
    1: _proximityToCollisionConnections, # Collision <- Proximity ==> FULLY CONNECTED
    2: _collisionToReverseConnections,  # Reverse Command <- Collision, not fully connected 
    3: _collisionToMotorConnections # Motor Command <- Collision, not fully connected 
}

# layer -> output
# results of f(activation[i]) where f is the output function
outputs = {
    0: annutils.sparseArray(active_ps, [0.0 for _ in active_ps]), # output: Proximity -> Collision
    1: annutils.sparseArray(active_ts, [0.0 for _ in active_ts]), # output: Collison -> Motor, Reverse
    2: annutils.sparseArray(
        list(connectivities[2].keys()), 
        [0.0 for _ in connectivities[2].keys()]
    ), # output: Reverse -> ...
    3: annutils.sparseArray(
        list(connectivities[3].keys()), 
        [0.0 for _ in connectivities[3].keys()]
    ) # output: Motor -> ...
}

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

###################### Neuron Functions ############################################ 
# sensorInput as sIn, previousLayerOutput as plOut, weights[[layer - 1] -> [layer]] as w 
#  '-> compositionFunction[layer]  
#       '-> activationFunction[layer]  
#           '->  outputFunction[layer] as o

# sensorInput as sIn, previousLayerOutput as plOut, weights[[layer - 1] -> [layer]] as w -> compositionFunction[layer] as h 
compositionFunction = {
    0: lambda sIn, plOut, w: sIn,
    1: lambda sIn, plOut, w: sIn + annutils.weightedSum(w, plOut),
    2: lambda sIn, plOut, w: annutils.weightedSum(w, plOut),
    3: lambda sIn, plOut, w: annutils.weightedSum(w, plOut)
}

# compositionFunction[layer] as h -> activationLevel[layer] as a = g(h[layer])
activationFunction = {
    0: lambda h: annutils.ActivationFunction.exp_inv(h), 
    1: lambda h: annutils.ActivationFunction.binary_threshold(h, learningParameters.collisionThreshold),
    2: lambda h: annutils.ActivationFunction.binary_threshold(h, learningParameters.reverseThreshold),
    3: lambda h: annutils.ActivationFunction.linear_threshold(h, learningParameters.motorThreshold) 
}

# activationLevel[layer] as a -> output[layer] as o
# the final value that will be propagated to each one of the connected neurons bearing activactionLevel a

outputFunction = {
    0: lambda a: a,
    1: lambda a: a,
    2: lambda a: a,
    3: lambda a: a * MIN_V # Motor output bounded between [0, MIN_V * || w[i] ||]
}

#################################################################