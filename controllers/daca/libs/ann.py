import math, operator

def matrix(rn : int, cn : int, gen: lambda: float = lambda: 0.0) -> list:
    return [array(cn, gen) for i in range(0, rn)]

def array(n: int, gen: lambda: float = lambda: 0.0) -> list:
    return [float(gen()) for i in range(0, n)]

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

def updateConnectivities(w : list, oc : list, op: list, lrate : float, frate : float) -> list:
    
        om = mean(oc) # mean output level of the current layer
        M = len(oc)
        N = len(op)

        # i <- neuron of the current layer, j <- neuron of the previous layer
        return [
                [
                    w[i][j] + (lrate * oc[i] * op[j] - frate * om * w[i][j]) / N
                    for j in range(0, N)
                ]
                for i in range(0, M)
            ]

class ActivationFunction:
    logistic = lambda x: 1 / (1 + math.exp(-x))
    linear_threshold = lambda x, threshold: 0 if x < threshold else 1
    linear = lambda x: x