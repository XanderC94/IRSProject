"""phototaxis controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, LED, DistanceSensor
from controller import *
import sys, math, operator, random

from libs.epuck import ID
from libs.argutils import parseArgs
from libs.sensor import sensorArray
from libs.motorresponse import wheelVelocity
import libs.motor as motor

import libs.annutils as ann
from libs.neuralnetstructure import *




opt = parseArgs(sys.argv)

print(opt)

# Setup ------------------------------------

# create the Robot instance.
robot = Robot()

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

# You should insert a getDevice-like function in order to get the
# instance of a device of the robot.

leds = sensorArray(ID.leds, timestep, lambda name: robot.getLED(name), enable = False)
motors = sensorArray(ID.motors, timestep, lambda name: robot.getMotor(name), enable = False)

dss = sensorArray(ID.distances, timestep, lambda name: robot.getDistanceSensor(name))
lss = sensorArray(ID.lights, timestep, lambda name: robot.getLightSensor(name))
bumpers = sensorArray(ID.bumpers, timestep, lambda name: robot.getTouchSensor(name))

for k, m in motors.items():
    m.device.setPosition(float('+inf'))
    m.device.setVelocity(0.0)

#-------------------------------------------------

# Main loop:
# - perform simulation steps until Webots is stopping the controller
while robot.step(timestep) != -1:
    
    # ~~~~~~~ Read the sensors: ~~~~~~~~~~~~~
    distances = []
    bumps = []

    for k, s in dss.items(): distances.append(s.device.getValue())
    for k, s in bumpers.items(): bumps.append(s.device.getValue())
    
    if 1 in bumps: print("TOUCHING!")
    print(f"Distances:{distances}")

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # ~~~~~~~~~~~~~~~~~ PROCESS ANN STATE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    # DISTANCES_INPUT -> PROXIMITY  ---------------------------- LAYER 0

    layer = 0 

    hf = compositionFunction[layer]
    g = activationFunction[layer]
    f = outputFunction[layer]

    h_proximity = [ann.inputComposition(i = distances[n], o = [], w = [],h = hf) for n in range(0, len(distances))] # summed activations of each neuron in the Proximity Layer 0
    a_proximity = [ann.activationLevel(h_proximity[i], g) for i in range(0, len(h_proximity))] # activation level of each neuron in the Proximity Layer 0
    outputs[layer] = [ann.neuronOutput(a_proximity[i], f) for i in range(0, len(a_proximity))] # output level of each neuron that will be passed to the next layer
    
    #----------------------------------------------------------

    # COLLISIONS_INPUT, PROXIMITY -> COLLISION -------------------------- LAYER 1

    layer = 1 
    
    w = connectivities[layer]
    o = outputs[layer - 1] # Proximity Layer Output
    hf = compositionFunction[layer]
    g = activationFunction[layer]
    f = outputFunction[layer]

    #h_collision = [ann.inputComposition(bumps[n], o, w[n], hf) for n in range(0, len(bumps))]
    bumperOutputByConnection = ann.mapToSensorsOutput(bumps, bumpersConnections)
    h_collision = [ann.inputComposition(bumperOutputByConnection[n], o, w[n], hf) for n in range(0, nCollisionNodes)]
    
    a_collision = [ann.activationLevel(h_collision[i], g) for i in range(0, len(h_collision))]
    outputs[layer] = [ann.neuronOutput(a_collision[i], f) for i in range(0, len(a_collision))]

    print(f"Proximity Layer Output {o}")
    print(f"Weights Proximity to Collision:")
    for i in range(0, len(w)): print(w[i])
    print(f"Collision Layer Composed Input {h_collision}")

    #-----------------------------------------------------------

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

    # COLLISION -> MOTORS -----------------------------  LAYER 3

    layer = 3 

    #w = connectivities[layer]
    o = outputs[layer - 2] # Collision Layer Output
    r = outputs[layer - 1] # Reverse Layer Output
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

    #Version 2 => 2 motor neuron
    h_motor = ann.sparseInputComposition([], o, connectivities[layer], hf)

    print(f"motor layer composed input: {h_motor}")

    a_motor = [ann.activationLevel(h_motor[i], g) for i in range(0,len(h_motor))]

    outputs[layer] = [ann.neuronOutput(a_motor[i], f) for i in range(0,len(a_motor))]

    #--------------------------------------------------------------

    # ~~~~~~~~~~~~~~~~~ END PROCESS ANN STATE ~~~~~~~~~~~~~~~~~~~~~~~~

    # ~~~~~~~~~~~~~~~~~ CALCULATE MOTOR SPEED ~~~~~~~~~~~~~~~~~~~~~~~~~

    """
    # Version 1-> 2 neuron in motor layer
    rv, lv = (outputs[layer][0], outputs[layer][1])
    """

    # Version 2 -> 5 neuron in the motor layer
    #get the extreme motor neuron value and subtract the output of the center motor neuron
    
    print(f"Collision Layer output {outputs[1]}")
    reverseLayerOutput = outputs[2]
    motorLayerOutputs = outputs[3]
    print(f"Command Layer [Reverse] output {reverseLayerOutput}")
    print(f"Command Layer [Motor] output {motorLayerOutputs}")

    lv, rv = wheelVelocity(motorLayerOutputs[0], reverseLayerOutput[0], motorLayerOutputs[1])

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    print(f"Speed:{lv}, {rv}")
    # Enter here functions to send actuator commands:
    motors['left'].device.setVelocity(lv)
    motors['right'].device.setVelocity(rv)

    #~~~~~~~~~~~~~~~~~~~~~~~~ UPDATE ANN WEIGHT ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Now apply what It has learned
    # Weights Updates
    updatedWeights = ann.updateConnectivities(connectivities[1], outputs[1], outputs[0], LEARNING_RATE, FORGET_RATE)
    connectivities.update({1: updatedWeights})
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    print()

    pass

# Enter here exit cleanup code.
motors['left'].device.setVelocity(0.0)
motors['right'].device.setVelocity(0.0)