import math, json, os, sys, datetime
from pathlib import Path
import pandas as panda
import columns as cols
from data import extractData

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

def synthesis(df: panda.DataFrame) -> panda.DataFrame:

    __df = df.drop([cols.ACTIVATION, cols.COLLISION], axis = 1)
    __df = __df[__df[cols.EVENT] != 'Going By']

    coll = __df[filterCollision(__df)].rename(
        columns= {
            cols.N_STEPS:cols.N_COLLIDE_STEPS,
            cols.N_EVENTS:cols.N_COLLIDE_EVENTS,
            cols.MEAN_EVENT_STEPS:cols.MEAN_COLLIDE_STEPS,
            cols.P_STEPS:cols.P_COLLIDE_STEPS,
            cols.P_EVENTS:cols.P_COLLIDE_EVENTS
        }
    )

    avoid = __df[filterAvoidance(__df)].rename(
        columns= {
            cols.N_STEPS:cols.N_AVOID_STEPS,
            cols.N_EVENTS:cols.N_AVOID_EVENTS,
            cols.MEAN_EVENT_STEPS:cols.MEAN_AVOID_STEPS,
            cols.P_STEPS:cols.P_AVOID_STEPS,
            cols.P_EVENTS:cols.P_AVOID_EVENTS
        }
    )

    avoid = avoid.drop([cols.EVENT], axis=1)
    coll = coll.drop([cols.EVENT], axis=1)

    synth = panda.DataFrame()

    if len(avoid) == 0:
        synth = fillZero(coll, 'Avoid')
        
    elif len(coll) == 0:
        synth = fillZero(avoid, 'Collide')
    else:
        synth = avoid.merge(coll, on=cols.standalone_columns)

    return synth[cols.ordered_columns]

# -------------------------------------------------------------------------

if __name__== "__main__" and len(sys.argv) > 1:

    __date = lambda: f'{datetime.datetime.now():%Y-%m-%dT%H-%M-%S}'

    dataPath = Path(sys.argv[1])
    savePath = ''

    df = panda.DataFrame()

    if dataPath.is_file() and dataPath.suffix == '.json':
        __path, __stats = extractData(dataPath)
        __stats = synthesis(__stats)
        df = df.append(__stats, ignore_index=True)

    elif dataPath.is_dir():

        saveDir = dataPath / 'csv'

        if not saveDir.exists():
            saveDir.mkdir()

        savePath = saveDir / f'res.synthetic.all.{__date()}.csv'

        for f in dataPath.iterdir():
            if f.is_file() and f.suffix == '.json':
                __path, __stats = extractData(f)
                __stats = synthesis(__stats)
                # print(__stats)
                df = df.append(__stats, ignore_index=True)

    df.sort_values(
        [cols.STDX, cols.STDZ, cols.P_AVOID_STEPS],
        ascending=[False, False, False]
    ).to_csv(savePath)