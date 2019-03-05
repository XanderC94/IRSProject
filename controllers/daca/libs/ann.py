import math, operator

def matrix(rn, cn, gen = lambda : 0.0) -> list:
    return [array(cn, gen) for _ in range(0, rn)]

def array(n, gen = lambda : 0.0) -> list:
    return [gen() for _ in range(0, n)]

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

def updateConnectivities(N : int, ann : dict, o : dict, lrate : float, frate : float) -> dict:
    
    for layer, w in ann.items():

        om = mean(o[layer]) # mean output level of the current layer
        
        ann[layer] = [
            # i <- neuron of the current layer, j <- neuron of the previous layer
            w[i][j] + (lrate * o[layer][i] * o[layer - 1][j] - frate * om * w[i][j]) / N
                for i in range(0, len(o[layer]))
                for j in range(0, len(o[layer - 1]))
        ]

    return ann

class ActivationFunction:
    logistic = lambda x: 1 / (1 + math.exp(-x))
    linear_threshold = lambda x, t: 0 if x < t else 1
    linear = lambda x: x