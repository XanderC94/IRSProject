"""
Network structure - "dacv3"

Summary:

----------- E-PUCK: ----------------
|
|          -  7-0  -
|    6  /             \  1            
|      |      [^]      |
|    5 |               | 2
|      |               | 
|       \             /
|          -  4-3  -
|
|     [^]  = Front direction
|     numbers -> sensor index  
|
-------------------------------------

PROXIMITY LAYER --composed of--: A neuron for each proximity sensor 
        |
[Fully connected to]
        |
        |
        '----> COLLISION LAYER --composed of--: 3 neurons where: 
                    |                           - the first is associated to the bumper sensors bs0,bs1 and bs2
                    |                           - the second is associated to the bumper sensors bs3 and bs4
                    |                           - the third is associated to the bumper sensors bs5, bs6 and bs7
                    |
                    |-[collision neurons associated to bs7 and bs0 are connected to]--> 1 REVERSE Neuron
                    |
                    '---> MOTOR LAYER -- composed of --: 2 Motor Neurons where: 
                                                          - one of them is associated to the left motor wheel 
                                                            and is connected to the collision layer neuron 
                                                            associated with bumper sensors (bs5, bs6, bs7)
                                                          - the other neuron is associated to the right motor wheel 
                                                            and is connected to the collision layer neuron
                                                            associated with bumper sensors (bs0, bs1, bs2)

"""

from libs.epuck import nBumpers, nDistanceSensors, nMotors, nLightSensors, MIN_V, PI
import libs.annutils as annutils
from libs.learningparameters import *


learningParameters = LearningParameters(0.08, 0.8, 0.65, 1, 2)

#~~~~~~~~~~~~~ NETWORK STRUCTURE ~~~~~~~~~~~~~~~~~~~~~

active_ps = [0, 1, 2, 3, 4, 5, 6, 7]

motor_config = [[0], [2]]

nCollisionNodes = 3
collisionNode = range(0, nCollisionNodes)
bumpersConnections = annutils.sparselyConnected(collisionNode, [[5, 6, 7], [3, 4], [0, 1, 2]], gen = lambda:1.0)

_proximityToCollisionConnections = annutils.fullyConnected(collisionNode, active_ps)

_collisionToReverseConnections = annutils.sparselyConnected([0], [[0, 2]], gen = lambda:1.0)
_collisionToMotorConnections = annutils.sparselyConnected(range(0, nMotors), motor_config, gen = lambda:1.0)


connectivities = {
    1: _proximityToCollisionConnections, # Collision <- Proximity ==> FULLY CONNECTED
    2: _collisionToReverseConnections,  # Reverse Command <- Collision, not fully connected 
    3: _collisionToMotorConnections # Motor Command <- Collision, not fully connected 
}

# layer -> output
# results of f(activation[i]) where f is the output function
outputs = {
    0: annutils.sparseArray(active_ps, [0.0 for _ in active_ps]), # output: Proximity -> Collision
    1: annutils.sparseArray(collisionNode, [0.0 for _ in collisionNode]),
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
#  '-> compositionFunction[layer] as h
#       '-> activationFunction[layer] as a 
#           '->  outputFunction[layer] as o

# sensorInput as sIn, previousLayerOutput as plOut, weights[[layer - 1] -> [layer]] as w -> compositionFunction[layer] as h 
compositionFunction = {
    0: lambda sIn, o, w: sIn,
    1: lambda bumpers, plOut, wij: annutils.logicSum(bumpers) + annutils.weightedSum(wij, plOut),
    2: lambda i, plOut, wij: annutils.weightedSum(wij, plOut), # wij is the degree
    3: lambda i, plOut, wij: annutils.weightedSum(wij, plOut) # wij is the degree
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
    3: lambda a: a * PI / len(_collisionToMotorConnections[0])  
}


#################################################################