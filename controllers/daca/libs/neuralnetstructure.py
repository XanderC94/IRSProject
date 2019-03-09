from libs.epuck import *
import libs.annutils as ann

"""
COLLISION_THRESHOLD = 1.0 #float(opt['coll-ths'])
LEARNING_RATE = 0.5 #float(opt['lrate'])
FORGET_RATE = 0.3 #float(opt['frate'])
"""

# Reference paper value #########################
COLLISION_THRESHOLD = 0.5 #float(opt['coll-ths'])
LEARNING_RATE = 0.1 #float(opt['lrate'])
FORGET_RATE = 0.5 #float(opt['frate'])

#################################################

RESPONSE_THRESHOLD = 2;

"""
# NETWORK STRUCTURE - Version 1 => 2 neurons in the motor layer ~~~~~~~~~

# Connectivity Matrices
# for each neuron of layer[j] the matrix holds the weights to each neuron of level[i = j - 1]
# in the form of neuron[n] of layer[j] -> [ w[n][0], ..., w[n][m] ] of neuron[0...m] of layer[i]
connectivities = {
    1: ann.matrix(nBumpers, nDistanceSensors), # Collision <- Proximity ==> FULLY CONNECTED
    2: ann.matrix(nMotors, int(nBumpers / 2), gen = lambda:1.0) # Output <- Collision, not fully connected but left bumpers connected to left motor and right bumpers to right motor
}

# layer -> output
# results of f(activation[i]) where f is the output function
outputs = {
    0: ann.array(nDistanceSensors), # output: Proximity -> Collision
    1: ann.array(nBumpers), # output: Collison -> Motor
    2: ann.array(nMotors) # output: Motor -> ...
}

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#~~~~~~~~~~~~~ NETWORK STRUCTURE - Version 2  ~~~~~~~~~~~~~~~~~~~~~

collToMotConnOrder = [5,6,7,0,1,2, 3,4]
collisionToMotorConnections = [
    [[4, 1.0],[5,1.0],[6,1.0],[7,1.0]], 
    [[7,1.0],[0,1.0]], 
    [[0,1.0],[1,1.0],[2,1.0],[3, 1.0]]
] 
    
connectivities = {
    1: ann.matrix(nBumpers, nDistanceSensors, gen = lambda:0.0), # Collision <- Proximity ==> FULLY CONNECTED
    2: collisionToMotorConnections # Motor Command <- Collision, not fully connected 
}

# layer -> output
# results of f(activation[i]) where f is the output function
outputs = {
    0: ann.array(nDistanceSensors), # output: Proximity -> Collision
    1: ann.array(nBumpers), # output: Collison -> Motor
    2: ann.array(len(collisionToMotorConnections)) # output: Motor -> ...
}

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

###################### Neuron Functions ############################################ 
# sensorInput as sIn, previousLayerOutput as plOut, weights[[layer - 1] -> [layer]] as w 
#  '-> compositionFunction[layer]  
#       '-> activationFunction[layer]  
#           '->  outputFunction[layer] as o

# sensorInput as sIn, previousLayerOutput as plOut, weights[[layer - 1] -> [layer]] as w -> compositionFunction[layer] as h 
compositionFunction = {
    0: lambda sIn, o, w: sIn,
    1: lambda sIn, plOut, wij: sIn + ann.weightedSum(wij, plOut),
    2: lambda i, plOut, wij: ann.weightedSum(wij, plOut) # wij is the degree
}

# compositionFunction[layer] as h -> activationLevel[layer] as a = g(h[layer]) 
"""
activationFunction = {
    0: lambda h: ann.ActivationFunction.logistic(h), # Logistic (?) or Linear (?)
    1: lambda h: ann.ActivationFunction.linear_threshold(h, COLLISION_THRESHOLD),
    2: lambda h: ann.ActivationFunction.linear(h) # Maybe should be the conversion to motor speed?
}
"""
activationFunction = {
    0: lambda h: ann.ActivationFunction.sigmoid(h), 
    1: lambda h: ann.ActivationFunction.binary_threshold(h, COLLISION_THRESHOLD),
    2: lambda h: ann.ActivationFunction.linear_threshold(h, RESPONSE_THRESHOLD) 
}

# activationLevel[layer] as a -> output[layer] as o
# the final value that will be propagated to each one of the connected neurons bearing activactionLevel a
"""
outputFunction = {
    0: lambda a: a,
    1: lambda a: a,
    2: lambda a: min(a, MAX_V - 1) + 1 # Motors output are between [1, and MAX_V]
}
"""
outputFunction = {
    0: lambda a: a,
    1: lambda a: a,
    2: lambda a, nPlOutput: a * PI/nPlOutput  
}

#################################################################
