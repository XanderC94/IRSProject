import datetime
from pathlib import Path
import columns as cols
import pandas as panda
import numpy as np

getDate = lambda: f'{datetime.datetime.now():%Y-%m-%dT%H-%M-%S}'

class Events:
    AVOIDANCE = 'Avoidance'
    COLLISION = 'Collision'
    ERROR = 'Error'
    GOINGBY = 'Going By'
 
def filterModeAndVersion(df: panda.DataFrame, mode:str, version:int):
    return (df['version'] == version) & (df['mode'] == mode)

def filterTopStats(df: panda.DataFrame, stdx = 0.2, stdz = 0.2, psteps = 0.8):
    return (df['std(x)'] > stdx) & (df['std(z)'] > stdz) & (df['%AvoidSteps'] > psteps) # & (abs(df['%AvoidSteps'] - df['%AvoidEvents']) < 0.2)

def filterFalsePositives(df: panda.DataFrame, stdx = 0.2, stdz = 0.2):
    return (df['std(x)'] > stdx) & (df['std(z)'] > stdz) # & (abs(df['%AvoidSteps'] - df['%AvoidEvents']) < 0.2)

def fillZero(df:panda.DataFrame, event: str):
    
    df[cols._nSteps(event)] = 0
    df[cols._nEvents(event)] = 0
    df[cols._mEventSteps(event)] = 0.0
    df[cols._pSteps(event)] = 0.0
    df[cols._pEvents(event)] = 0.0

    return df

def filterAvoidance(df: panda.DataFrame):
    return (df['event'] == Events.AVOIDANCE)

def filterCollision(df: panda.DataFrame):
    return (df['event'] == Events.COLLISION)

def filterError(df: panda.DataFrame):
    return (df['event'] == Events.ERROR)

def filterGoingBy(df: panda.DataFrame):
    return (df['event'] == Events.GOINGBY)

class Float(float):
    def __init__(self, value:float):
        self.value = value

    def isBetween(self, a:float, b:float, upperbounded : bool = False, lowerbounded : bool = False):
        
        _b, _a = (a, b) if a > b else (b, a)
        
        if upperbounded and lowerbounded:
            return self.value < _b and self.value > _a
        elif upperbounded:
            return self.value < _b and self.value >= _a
        elif lowerbounded:
            return self.value <= _b and self.value > _a
        else:
            return self.value <= _b and self.value >= _a