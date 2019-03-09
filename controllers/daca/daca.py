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

import libs.annutils as ann
from libs.nuralnetstructure import *

opt = parseArgs(sys.argv)

print(opt)

# Setup ------------------------------------

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

#-------------------------------------------------


# Main loop:
# - perform simulation steps until Webots is stopping the controller
while robot.step(timestep) != -1:
    
    # ~~~~~~~ Read the sensors: ~~~~~~~~~~~~~
    distances = []
    bumps = []

    for k, s in dss.items(): distances.append(s.device.getValue())
    for k, s in bumpers.items(): bumps.append(s.device.getValue())
    
    # print(f"distances:{distances}")
    # print(f"bumps:{bumps}")

    if 1 in bumps: print("TOUCHING!")
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


    # ~~~~~~~~~~~~~~~~~ PROCESS CURRENT NETWORKSTATE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    # INPUT -> PROXIMITY  ---------------------------- LAYER 0
    layer = 0 

    hf = compositionFunction[layer]
    g = activationFunction[layer]
    f = outputFunction[layer]

    h_proximity = [ann.inputComposition(i = distances[n], o = [], w = [],h = hf) for n in range(0, len(distances))] # summed activations of each neuron in the Proximity Layer 0
    a_proximity = [ann.activationLevel(h_proximity[i], g) for i in range(0, len(h_proximity))] # activation level of each neuron in the Proximity Layer 0
    outputs[layer] = [ann.neuronOutput(a_proximity[i], f) for i in range(0,len(a_proximity))] # output level of each neuron that will be passed to the next layer
    
    #----------------------------------------------------------

    # PROXIMITY -> COLLISION -------------------------- LAYER 1

    layer += 1 
    
    w = connectivities[layer]
    o = outputs[layer - 1] # Proximity Layer Output
    hf = compositionFunction[layer]
    g = activationFunction[layer]
    f = outputFunction[layer]

    h_collision = [ann.inputComposition(bumps[n], o, w[n], hf) for n in range(0, len(bumps))]
    a_collision = [ann.activationLevel(h_collision[i], g) for i in range(0,len(h_collision))]
    outputs[layer] = [ann.neuronOutput(a_collision[i], f) for i in range(0,len(a_collision))]

    #-----------------------------------------------------------

    # COLLISION -> MOTORS -----------------------------  LAYER 2
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

    print("composed input")        
    print(h_motor)
    a_motor = [ann.activationLevel(h_motor[i], g) for i in range(0,len(h_motor))]

    outputs[layer] = [ann.neuronOutput(a_motor[i], lambda x: f(x, len(collisionMotorNeuronsConn[i]))) for i in range(0,len(a_motor))]

    #--------------------------------------------------------------

    # ~~~~~~~~~~~~~~~~~ END PROCESS CURRENT STATE ~~~~~~~~~~~~~~~~~~~~~~~~
    




    # ~~~~~~~~~~~~~~~~~ CALCULATE NEW MOTOR SPEED ~~~~~~~~~~~~~~~~~~~~~~~~~

    """
    # Version 1-> 2 neuron in motor layer
    rv, lv = (outputs[layer][0], outputs[layer][1])
    """

    # Version 2 -> 5 neuron in the motor layer
    #get the extreme motor neuron value and subtract the output of the center motor neuron
    
    print("Collision neurons output")
    print(outputs[1])
    motorLayerOutputs = outputs[2]
    print("Motor command neurons output")
    print(motorLayerOutputs)

    lv, rv = wheelVelocity(motorLayerOutputs[0], motorLayerOutputs[1], motorLayerOutputs[2])

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


    print(f"Speed:{lv}, {rv}")
    # Enter here functions to send actuator commands:
    motors['left'].device.setVelocity(lv)
    motors['right'].device.setVelocity(rv)


    #~~~~~~~~~~~~~~~~~~~~~~~~ UPDATE WEIGHT ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Now apply what It has learned
    # Weights Updates
    connectivities.update({1: ann.updateConnectivities(connectivities[1], outputs[1], outputs[0], LEARNING_RATE, FORGET_RATE)})
    
    """
    connectivities.update({2:
        ann.updateConnectivities(connectivities[2], outputs[2][:1], outputs[1][:step], LEARNING_RATE, FORGET_RATE) +
        ann.updateConnectivities(connectivities[2], outputs[2][1:], outputs[1][step:], LEARNING_RATE, FORGET_RATE)
    })
    """
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    pass

# Enter here exit cleanup code.
motors['left'].device.setVelocity(0.0)
motors['right'].device.setVelocity(0.0)