import math, json, os, sys, datetime
from pathlib import Path
import pandas as panda
import columns as cols
from data import extractData

from utils import *

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

def __getSynthData(path, getModel) -> (panda.DataFrame, dict):

    __path, __stats, __model = extractData(path, getModel=getModel)
    __stats = synthesis(__stats)

    if len(__model) > 0 and len(__stats[(__stats['mode'] == 'train') & filterTopStats(__stats)]) > 0:
        print(f'Added model for: {path.name}')
        return (__stats, __model)
    else:
        return (__stats, {})
    

if __name__== "__main__" and len(sys.argv) > 1:

    dataPath = Path(sys.argv[1])
    getModel = True if len(sys.argv) > 2 and '-model' in sys.argv[2] else False
    saveDir = Path('')

    print(f'path:{dataPath}, save-model:{getModel}')

    df = panda.DataFrame()
    models = []

    if dataPath.is_file() and dataPath.suffix == '.json':
        
        saveDir = dataPath.parent / 'csv'

        stats, model = __getSynthData(dataPath, getModel)
        df = df.append(stats, ignore_index=True)
        if len(model) > 0: models.append(model)

    elif dataPath.is_dir():

        saveDir = dataPath / 'csv'

        for f in dataPath.iterdir():
            if f.is_file() and f.suffix == '.json':
                stats, model = __getSynthData(f, getModel)
                df = df.append(stats, ignore_index=True)
                if len(model) > 0: models.append(model)

    # --------------------------------------------------------------------------

    if not saveDir.exists():
        saveDir.mkdir()

    modelsDir = saveDir / 'models'

    if not modelsDir.exists():
        modelsDir.mkdir()

    # ---------------------------------------------------------------------------

    df.index.name = 'index'

    plot_columns = ['index', 'LR', 'FR', '%AvoidSteps', 'CT']

    savePath = saveDir / f'res.synthetic.all.{getDate()}.csv'

    df.sort_values(
        [cols.STDX, cols.STDZ, cols.P_AVOID_STEPS],
        ascending=[False, False, False]
    ).to_csv(savePath)

    # ---------------------------------------------------------------------------

    for model in models:
        if len(model) > 0:
            lr = model['parameters']['learningRate']
            fr = model['parameters']['forgetRate']
            ct = model['parameters']['collisionThreshold']

            savePath = modelsDir / f'model.to.test.lr{lr}.fr{fr}.ct{ct}.{getDate()}.json'
            with open(savePath, mode='w') as savefile:
                json.dump(model,savefile, indent=4)
            
            print(f'Saved model to {savePath}')