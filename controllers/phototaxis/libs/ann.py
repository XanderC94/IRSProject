import math, operator

def matrix(rn, cn):
    return [array(cn) for _ in range(0, rn)]

def array(n):
    return [0.0 for _ in range(0, n)]

def weightedSum(nidx, w, o):
    return sum([w[nidx][j] * o[j] for j in range(0, len(o))])

def mean(v : []):
    return sum(v)/len(v)

def activationLevel(hi, g = lambda h: float):
    return g(hi)

def neuronOutput(ai, f = lambda a: float):
    return f(ai)

def updateConnectivities(N, ann, o, lrate, frate):
    
    for layer, w in ann.items():
        
        ann[layer] = [
            w[i][j] + (lrate * o[layer + 1][i] * o[layer][j] - frate * mean(o[layer + 1]) * w[i][j]) / N
                for i in range(0, len(o[layer+1]))
                for j in range(0, len(o[layer]))
        ]

    return ann

class ActivationFunction:
    logistic = lambda x: 1 / (1 + math.exp(-x))
    linear_threshold = lambda x, t: 0 if x < t else 1
    linear = lambda x: x