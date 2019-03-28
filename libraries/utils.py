import datetime
from pathlib import Path
import columns as cols
import pandas as panda
import numpy as np

def filterModeAndVersion(df: panda.DataFrame, mode:str, version:int):
    return (df['version'] == version) & (df['mode'] == mode)

def filterTopStats(df: panda.DataFrame, stdx = 0.2, stdz = 0.2, psteps = 0.8):
    return (df['std(x)'] > stdx) & (df['std(z)'] > stdz) & (df['%AvoidSteps'] > psteps) # & (abs(df['%AvoidSteps'] - df['%AvoidEvents']) < 0.2)

def filterFalsePositives(df: panda.DataFrame, stdx = 0.2, stdz = 0.2):
    return (df['std(x)'] > stdx) & (df['std(z)'] > stdz) # & (abs(df['%AvoidSteps'] - df['%AvoidEvents']) < 0.2)

getDate = lambda: f'{datetime.datetime.now():%Y-%m-%dT%H-%M-%S}'

def fillZero(df:panda.DataFrame, event: str):
    
    df[cols._nSteps(event)] = 0
    df[cols._nEvents(event)] = 0
    df[cols._mEventSteps(event)] = 0.0
    df[cols._pSteps(event)] = 0.0
    df[cols._pEvents(event)] = 0.0

    return df

def filterAvoidance(df: panda.DataFrame):
    return (df['event'] == 'Avoidance')

def filterCollision(df: panda.DataFrame):
    return (df['event'] == 'Collision')

def filterError(df: panda.DataFrame):
    return (df['event'] == 'Error')