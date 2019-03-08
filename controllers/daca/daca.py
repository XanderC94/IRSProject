"""phototaxis controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, LED, DistanceSensor
from controller import *
import sys, math, operator, random

from libs.epuck import *
from libs.argutils import *
from libs.sensor import *
from libs.motorresponse import *
import libs.motor as motor

import libs.ann as ann

opt = parseArgs(sys.argv)

print(opt)

"""
COLLISION_THRESHOLD = 1.0 #float(opt['coll-ths'])
LEARNING_RATE = 0.5 #float(opt['lrate'])
FORGET_RATE = 0.3 #float(opt['frate'])
"""

#Reference paper value
COLLISION_THRESHOLD = 0.5 #float(opt['coll-ths'])
LEARNING_RATE = 0.1 #float(opt['lrate'])
FORGET_RATE = 0.5 #float(opt['frate'])
RESPONSE_THRESHOLD = 1;
####################################################################################################
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

# NETWORK STRUCTURE - Version 2 => 3 neurons in the motor layer.  ~~~~~~
# From reference paper Distributed adaptive control: The self-organization of structured behavior
nMotorsResponsegNeurons = 5
connectivities = {
    1: ann.matrix(nBumpers, nDistanceSensors, gen = lambda:0.0), # Collision <- Proximity ==> FULLY CONNECTED
    2: [[[5,1.0],[6,1.0]], [[6,1.0], [7,1.0]], [[7,1.0],[0,1.0]], [[0,1.0],[1,1.0]], [[1,1.0],[2,1.0]]] # Output <- Collision, not fully connected but left bumpers connected to left motor and right bumpers to right motor
}

# layer -> output
# results of f(activation[i]) where f is the output function
outputs = {
    0: ann.array(nDistanceSensors), # output: Proximity -> Collision
    1: ann.array(nBumpers), # output: Collison -> Motor
    2: ann.array(nMotorsResponsegNeurons) # output: Motor -> ...
}

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Neuron Functions ############################################

# sensorInput as sIn, previousLayerOutput as plOut, weights[[layer - 1] -> [layer]] as w -> compositionFunction[layer] as h 

compositionFunction = {
    0: lambda sIn, o, w: sIn,
    1: lambda sIn, plOut, wij: sIn + ann.weightedSum(wij, plOut),
    2: lambda i, plOut, wij: ann.weightedSum(wij, plOut) # (?)
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
    0: lambda h: ann.ActivationFunction.logistic(h), # Logistic (?) or Linear (?)
    1: lambda h: ann.ActivationFunction.linear_threshold(h, COLLISION_THRESHOLD),
    2: lambda h: ann.ActivationFunction.linear_threshold(h, RESPONSE_THRESHOLD) # Maybe should be the conversion to motor speed?
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
    2: lambda a: a # Motors output are between [1, and MAX_V]
}
#################################################################



#########################################################################################################

distance_ids = ids(distance_sensor_template, nDistanceSensors)
light_ids = ids(light_sensor_template, nLightSensors)
led_ids = ids(led_template, nLEDs)
motors_ids = {'left':'left wheel motor', 'right':'right wheel motor'}
bumper_ids = ids(bumper_template, nBumpers)

# create the Robot instance.
robot = Robot()

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

# You should insert a getDevice-like function in order to get the
# instance of a device of the robot.

leds = sensorArray(led_ids, timestep, lambda name: robot.getLED(name), enable = False)
motors = sensorArray(motors_ids, timestep, lambda name: robot.getMotor(name), enable = False)

dss = sensorArray(distance_ids, timestep, lambda name: robot.getDistanceSensor(name))
lss = sensorArray(light_ids, timestep, lambda name: robot.getLightSensor(name))
bumpers = sensorArray(bumper_ids, timestep, lambda name: robot.getTouchSensor(name))

for k, m in motors.items():
    m.device.setPosition(float('+inf'))
    m.device.setVelocity(0.0)

# Main loop:
# - perform simulation steps until Webots is stopping the controller
while robot.step(timestep) != -1:
    
    # Read the sensors:    
    distances = []
    bumps = []

    for k, s in dss.items(): distances.append(s.device.getValue())
    for k, s in bumpers.items(): bumps.append(s.device.getValue())
    
    # print(f"distances:{distances}")
    # print(f"bumps:{bumps}")

    if 1 in bumps: print("TOUCHING!")
    
    # Process sensor data here. ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    # INPUT -> PROXIMITY  ##########################
    layer = 0 

    hf = compositionFunction[layer]
    g = activationFunction[layer]
    f = outputFunction[layer]

    h_proximity = [ann.inputComposition(i = distances[n], o = [], w = [],h = hf) for n in range(0, len(distances))] # summed activations of each neuron in the Proximity Layer 0
    a_proximity = [ann.activationLevel(h, g) for h in h_proximity] # activation level of each neuron in the Proximity Layer 0
    outputs[layer] = [ann.neuronOutput(a, f) for a in a_proximity] # output level of each neuron that will be passed to the next layer
    
    #################################################

    # PROXIMITY -> COLLISION ###########################

    layer += 1 
    
    w = connectivities[layer]
    o = outputs[layer - 1] # Proximity Layer Output
    hf = compositionFunction[layer]
    g = activationFunction[layer]
    f = outputFunction[layer]

    h_collision = [ann.inputComposition(bumps[n], o, w[n], hf) for n in range(0, len(bumps))]
    a_collision = [ann.activationLevel(h, g) for h in h_collision]
    outputs[layer] = [ann.neuronOutput(a, f) for a in a_collision]

    ################################################

    # COLLISION -> MOTORS ############################# 
    layer += 1 

    #w = connectivities[layer]
    o = outputs[layer - 1] # Collision Layer Output
    hf = compositionFunction[layer]
    g = activationFunction[layer]
    f = outputFunction[layer]

    """
    #Version 1 => 2 motor neuron
    step = int(len(o)/len(motors))
    
    # since the last layer is not fully connected, get slices of the output from the collision layer by *steps*
    # in this case to each motor is provided half (2 motors) of the outputs array: 
    # 0-3 are those on the right motor side
    # 4-7 are those on the left motor side
    h_motor = [ann.inputComposition([], o[n*step:(n+1)*step], w[n], hf) for n in range(0, len(motors))]
    """

    #Version 2 => 3 motor neuron   
    collisionMotorNeuronsConn = connectivities[layer]
    h_motor = []
    for connToMotorAction in collisionMotorNeuronsConn:
        oConn = []
        weight = []
        for connection in connToMotorAction: 
            oConn.append(o[connection[0]])
            weight.append(connection[1])
        h_motor.append((ann.inputComposition([], oConn, weight, hf)))
            
    a_motor = [ann.activationLevel(h, g) for h in h_motor]
    outputs[layer] = [ann.neuronOutput(a, f) for a in a_motor]

    ##################################################

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    #CALCULATE NEW MOTOR SPEED ~~~~~~~~~~~~~~~~~~~~~~~~~

    """
    # Version 1-> 2 neuron in motor layer
    rv, lv = (outputs[layer][0], outputs[layer][1])
    """

    # Version 2 -> 5 neuron in the motor layer
    #get the extreme motor neuron value and subtract the output of the center motor neuron
    motorLayerOutputs = outputs[2]
    lv, rv = 0,0
    if motorLayerOutputs[2] or (motorLayerOutputs[1] and motorLayerOutputs[3]):
        lv, rv = reverse()
        print("Reverse");
    elif motorLayerOutputs[1]:
        lv, rv = turnRight9Deg()
        print("turnRight9Deg");
    elif motorLayerOutputs[3]:
        lv, rv = turnLeft9Deg()
        print("turnLeft9Deg");
    elif motorLayerOutputs[0]:
        lv, rv = turnRight1Deg()
        print("turnRight1Deg");
    elif motorLayerOutputs[4]:
        lv, rv = turnLeft1Deg()
        print("turnLeft1Deg");
    else:
        lv, rv = advance()
        print("advance");



    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    print(f"Speed:{lv}, {rv}")

    # Enter here functions to send actuator commands:
    motors['left'].device.setVelocity(lv)
    motors['right'].device.setVelocity(rv)

    # Now apply what It has learned
    # Weights Updates
    connectivities.update({1: ann.updateConnectivities(connectivities[1], outputs[1], outputs[0], LEARNING_RATE, FORGET_RATE)})
    
    """
    connectivities.update({2:
        ann.updateConnectivities(connectivities[2], outputs[2][:1], outputs[1][:step], LEARNING_RATE, FORGET_RATE) +
        ann.updateConnectivities(connectivities[2], outputs[2][1:], outputs[1][step:], LEARNING_RATE, FORGET_RATE)
    })
    """


    pass

# Enter here exit cleanup code.
motors['left'].device.setVelocity(0.0)
motors['right'].device.setVelocity(0.0)