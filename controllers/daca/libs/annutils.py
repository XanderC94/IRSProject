import math, operator

def mapToSensorsOutput(sensorsOutput: list, connections: dict):
    result = []
    mapping = lambda x: list(sensorsOutput[i] for i in x)
    for conn in connections.keys():
        result.append(mapping(connections[conn]))
    return result

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

def neuralConnection(nId, prevLayer:list, gen: lambda: float = lambda:0.0):

    row = {}

    for j in prevLayer:
        row.update(pair(j, gen())) 

    return pair(nId, row)

def sparseInputComposition(nIn: float or int, outputs: list or dict, connectivities: dict, hf: lambda i, o, w: float) -> list:
    nOuts = []
    weights = []
    
    for prevNeuron, weight in connectivities.items():
        
        if len(outputs) > prevNeuron or prevNeuron in outputs: 
            nOuts.append(outputs[prevNeuron])
            weights.append(weight)

    return inputComposition(nIn, nOuts, weights, hf)

def sparseLayerInputComposition(inputs:list, outputs: list or dict, layerConnectivities: dict, hf: lambda i, o, w: float) -> list:
    h = []
        
    for currNeuron, connToNeuron in layerConnectivities.items():
        nIn = inputs[currNeuron] if len(inputs) > 0 else 0.0

        h.append(sparseInputComposition(nIn, outputs, connToNeuron, hf))

    return h

def sparseArray(keys:list, values:list) -> dict:
    return {
        keys[i]:values[i] for i in range(0, len(values))
    }

def matrix(rn : int, cn : int, gen: lambda: float = lambda: 0.0) -> list:
    return [array(cn, gen) for i in range(0, rn)]

def array(n: int, gen: lambda: float = lambda: 0.0) -> list:
    return [gen() for i in range(0, n)]

def pair(key, value): return {key:value}

def weightedSum(w : list, o : list) -> float:
    return sum([w[j] * o[j] for j in range(0, len(o))])

def mean(v : list) -> float:
    return sum(v)/len(v)

def inputComposition(i: float, o: list, w: list, h: lambda i, o, w: float) -> float:
    return h(i, o, w)

def activationLevel(hi : float, g : lambda h: float) -> float:
    return g(hi)

def neuronOutput(ai : float, f = lambda a: a) -> float:
    return f(ai)

def layerInputComposition(i: list, o:list, w: list or dict, h: lambda i, o, w: float) -> list:
    return [inputComposition(i = i[n], o = o, w = w, h = h) for n in range(0, len(i))]

def layerActivationLevel(h:list, g : lambda h: float) -> list:
    return [activationLevel(h[i], g) for i in range(0, len(h))]

def layerOutput(a:list, f = lambda a: a):
    return [neuronOutput(a[i], f) for i in range(0, len(a))]

def updateSparseConnectivities(w : dict, currLayerOutput : list or dict, prevLayerOutput: list or dict, learnRate : float, forgetRate : float) -> dict:
    
    # mean output level of the current layer
    meanCurrOutput = mean(
        currLayerOutput if isinstance(currLayerOutput, list) else list(currLayerOutput.values())
    )

    # m = len(currLayerOutput)
    n = len(prevLayerOutput)

    weights = {}
    for i, oi in currLayerOutput.items():
        conn = {}
        for j, oj in prevLayerOutput.items():
            
            delta = (learnRate * oi * oj - forgetRate * meanCurrOutput * w[i][j]) / n
            conn.update({j:w[i][j] + delta})

        weights.update({i:conn})

    return weights

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