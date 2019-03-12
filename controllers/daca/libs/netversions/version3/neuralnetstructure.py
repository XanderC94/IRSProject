"""
Network structure VERSION 3
A neuron for each proximity sensors
        |
        '----> 3 Neuron in the Collision layer 
                    |---> 1 Reverse Neuron
                    '---> 2 Motor Neuron


"""
from libs.epuck import nBumpers, nDistanceSensors, nMotors, nLightSensors, MIN_V, PI
import libs.annutils as ann

COLLISION_THRESHOLD = 0.65 #float(opt['coll-ths'])
LEARNING_RATE = 0.08 #float(opt['lrate'])
FORGET_RATE = 0.8 #float(opt['frate'])

#################################################

MOTOR_THRESHOLD = 1;
REVERSE_THRESHOLD = 2;

#~~~~~~~~~~~~~ NETWORK STRUCTURE  ~~~~~~~~~~~~~~~~~~~~~

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