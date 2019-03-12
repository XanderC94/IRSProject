from libs.epuck import nBumpers, nDistanceSensors, nMotors, nLightSensors, MIN_V, PI
import libs.annutils as ann

"""
COLLISION_THRESHOLD = 1.0 #float(opt['coll-ths'])
LEARNING_RATE = 0.5 #float(opt['lrate'])
FORGET_RATE = 0.3 #float(opt['frate'])
"""

# Reference paper value #########################
COLLISION_THRESHOLD = 0.65 #float(opt['coll-ths'])
LEARNING_RATE = 0.05 #float(opt['lrate'])
FORGET_RATE = 0.8 #float(opt['frate'])

#################################################

MOTOR_THRESHOLD = 1;
REVERSE_THRESHOLD = 2;

"""
# NETWORK STRUCTURE - Version 1 => 2 neurons in the motor layer ~~~~~~~~~


connectivities = {
    1: ann.matrix(nBumpers, nDistanceSensors), # Collision <- Proximity ==> FULLY CONNECTED
    2: ann.matrix(nMotors, int(nBumpers / 2), gen = lambda:1.0) # Output <- Collision, not fully connected but left bumpers connected to left motor and right bumpers to right motor
}

outputs = {
    0: ann.array(nDistanceSensors), # output: Proximity -> Collision
    1: ann.array(nBumpers), # output: Collison -> Motor
    2: ann.array(nMotors) # output: Motor -> ...
}

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
"""
#~~~~~~~~~~~~~ NETWORK STRUCTURE - Version 2  ~~~~~~~~~~~~~~~~~~~~~

collToMotConnOrder = {
    'left': [4, 5, 6, 7],
    'right': [0, 1, 2, 3], 
    'front': [0, 7],
    'rear': [3, 4]
}

proximityToCollisionConnections = ann.matrix(nBumpers, nDistanceSensors)

collisionToReverseConnections = ann.sparselyConnected([0], [[7, 0]], gen = lambda:1.0)
    
collisionToMotorConnections = ann.sparselyConnected(range(0, nMotors), [[4, 5, 6, 7], [0, 1, 2, 3]], gen = lambda:1.0)

# collisionToMotorConnections = [
#     [[4, 1.0],[5, 1.0],[6, 1.0],[7, 1.0]],  
#     [[0, 1.0],[1, 1.0],[2, 1.0],[3, 1.0]]
# ]


# Connectivity Matrices
# for each neuron of layer[j] the matrix holds the weights to each neuron of level[i = j - 1]
# in the form of neuron[n] of layer[j] -> [ w[n][0], ..., w[n][m] ] of neuron[0...m] of layer[i]
connectivities = {
    1: proximityToCollisionConnections, # Collision <- Proximity ==> FULLY CONNECTED
    2: collisionToReverseConnections,  # Reverse Command <- Collision, not fully connected 
    3: collisionToMotorConnections # Motor Command <- Collision, not fully connected 
}

# layer -> output
# results of f(activation[i]) where f is the output function
outputs = {
    0: ann.array(nDistanceSensors), # output: Proximity -> Collision
    1: ann.array(nBumpers), # output: Collison -> Motor, Reverse
    2: ann.array(len(collisionToReverseConnections)), # output: Reverse -> ...
    3: ann.array(len(collisionToMotorConnections)) # output: Motor -> ...
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
    1: lambda sIn, plOut, w: sIn + ann.weightedSum(w, plOut),
    2: lambda sIn, plOut, w: ann.weightedSum(w, plOut),
    3: lambda sIn, plOut, w: ann.weightedSum(w, plOut)
}

# compositionFunction[layer] as h -> activationLevel[layer] as a = g(h[layer])
activationFunction = {
    0: lambda h: ann.ActivationFunction.exp_inv(h), 
    1: lambda h: ann.ActivationFunction.binary_threshold(h, COLLISION_THRESHOLD),
    2: lambda h: ann.ActivationFunction.binary_threshold(h, REVERSE_THRESHOLD),
    3: lambda h: ann.ActivationFunction.linear_threshold(h, MOTOR_THRESHOLD) 
}

# activationLevel[layer] as a -> output[layer] as o
# the final value that will be propagated to each one of the connected neurons bearing activactionLevel a

outputFunction = {
    0: lambda a: a,
    1: lambda a: a,
    2: lambda a: a,
    3: lambda a: a * MIN_V # Motor output bounded between [0, MIN_V * || w[i] ||]
}

"""

#~~~~~~~~~~~~~ NETWORK STRUCTURE - Version 3  ~~~~~~~~~~~~~~~~~~~~~

nCollisionNodes = 3
bumpersConnections = ann.sparselyConnected(range(0, nCollisionNodes), [[5, 6, 7], [3, 4], [0, 1, 2]], gen = lambda:1.0)

proximityToCollisionConnections = ann.matrix(nCollisionNodes, nDistanceSensors)

collisionToReverseConnections = ann.sparselyConnected([0], [[0, 2]], gen = lambda:1.0)
collisionToMotorConnections = ann.sparselyConnected(range(0, nMotors), [[0], [2]], gen = lambda:1.0)


connectivities = {
    1: proximityToCollisionConnections, # Collision <- Proximity ==> FULLY CONNECTED
    2: collisionToReverseConnections,  # Reverse Command <- Collision, not fully connected 
    3: collisionToMotorConnections # Motor Command <- Collision, not fully connected 
}

# layer -> output
# results of f(activation[i]) where f is the output function
outputs = {
    0: ann.array(nDistanceSensors), # output: Proximity -> Collision
    1: ann.array(nCollisionNodes), # output: Collison -> Motor, Reverse
    2: ann.array(len(collisionToReverseConnections)), # output: Reverse -> ...
    3: ann.array(len(collisionToMotorConnections)) # output: Motor -> ...
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
    1: lambda bumpers, plOut, wij: ann.logicSum(bumpers) + ann.weightedSum(wij, plOut),
    2: lambda i, plOut, wij: ann.weightedSum(wij, plOut), # wij is the degree
    3: lambda i, plOut, wij: ann.weightedSum(wij, plOut) # wij is the degree
}

# compositionFunction[layer] as h -> activationLevel[layer] as a = g(h[layer]) 

activationFunction = {
    0: lambda h: ann.ActivationFunction.exp_inv(h), 
    1: lambda h: ann.ActivationFunction.binary_threshold(h, COLLISION_THRESHOLD),
    2: lambda h: ann.ActivationFunction.binary_threshold(h, REVERSE_THRESHOLD), 
    3: lambda h: ann.ActivationFunction.linear_threshold(h, MOTOR_THRESHOLD) 
}

# activationLevel[layer] as a -> output[layer] as o
# the final value that will be propagated to each one of the connected neurons bearing activactionLevel a

outputFunction = {
    0: lambda a: a,
    1: lambda a: a,
    2: lambda a: a,
    3: lambda a: a * PI / len(collisionToMotorConnections[0])  
}


#################################################################
