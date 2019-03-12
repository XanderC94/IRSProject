import math, operator

def logicSum(booleanValues: list) -> bool:
    result = 0
    for val in booleanValues:
        result = result or val 
    return result


def sparselyConnected(currLayer:list, prevLayer:dict or list, gen: lambda: float = lambda:0.0) -> dict:
    w = {}

    for i in currLayer:
        w.update(neuralConnection(i, prevLayer[i], gen))

    return w

def fullyConnected(currLayer, prevLayer, gen: lambda: float = lambda:0.0) -> dict:
    w = {}

    for i in currLayer:
        w.update(neuralConnection(i, prevLayer, gen))

    return w

def neuralConnection(nId, prevLayer, gen: lambda: float = lambda:0.0):

    row = {}

    for j in prevLayer:
        row.update(pair(j, gen())) 

    return pair(nId, row)

def sparseInputComposition(inputs:list, outputs: list, layerConnectivities: dict, hf: lambda i, o, w: float) -> list:
    h = []
    for _, connToNeuron in layerConnectivities.items():
        nOuts = []
        nIns = []
        weights = []

        for prevNeuron, weight in connToNeuron.items():
            if len(outputs) > prevNeuron: nOuts.append(outputs[prevNeuron])
            if len(inputs) > prevNeuron: nIns.append(inputs[prevNeuron])
            weights.append(weight)

        h.append((inputComposition(nIns, nOuts, weights, hf)))

    return h

def matrix(rn : int, cn : int, gen: lambda: float = lambda: 0.0) -> list:
    return [array(cn, gen) for i in range(0, rn)]

def array(n: int, gen: lambda: float = lambda: 0.0) -> list:
    return [gen() for i in range(0, n)]

def pair(key, value): return {key:value}

def weightedSum(w : list, o : list) -> float:
    return sum([w[j] * o[j] for j in range(0, len(o))])

def mean(v : list) -> float:
    return sum(v)/len(v)

def inputComposition(i, o, w, h: lambda i, o, w: float) -> float:
    return h(i, o, w)

def activationLevel(hi : float, g : lambda h: float) -> float:
    return g(hi)

def neuronOutput(ai : float, f = lambda a: a) -> float:
    return f(ai)

def updateConnectivities(w : list, currLayerOutput : list, prevLayerOutput: list, learnRate : float, forgetRate : float) -> list:
    
        meanCurrOutput = mean(currLayerOutput) # mean output level of the current layer
        m = len(currLayerOutput)
        n = len(prevLayerOutput)

        # | N[j]: prevLayer |-- w[i][j] -->| M[i]: currLayer |
        # i <- neuron of the current layer A, j <- neuron of the previous layer B
        return [
                [
                    w[i][j] + (learnRate * currLayerOutput[i] * prevLayerOutput[j] - forgetRate * meanCurrOutput * w[i][j]) / n
                    for j in range(0, n)
                ]
                for i in range(0, m)
            ]

class ActivationFunction:
    sigmoid = lambda x: 1 / (1 + math.exp(-x))
    exp_inv = lambda x: math.exp(-x)
    binary_threshold = lambda x, threshold: 0 if x < threshold else 1
    linear_threshold = lambda x, threshold: 0 if x < threshold else x
    linear = lambda x: x