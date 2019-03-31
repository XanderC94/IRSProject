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