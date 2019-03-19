import math, json, sys, copy, os, csv, datetime

import matplotlib.pyplot as plotter
from mpl_toolkits.mplot3d import axes3d
from figure import figure
from data import extractData

from pathlib import Path

import pandas as panda
import numpy as np

# ------------------------------------------------------------------------------------------------------ #

csvPaths = []

__date = lambda: f'{datetime.datetime.now():%Y-%m-%dT%H-%M-%S}'

def filterModeAndVersion(df: panda.DataFrame, mode:str, version:int):
    return (df['version'] == version) & (df['mode'] == mode)

def filterAvoidance(df: panda.DataFrame):
    return (df['event'] == 'Avoidance')

def filterCollision(df: panda.DataFrame):
    return (df['event'] == 'Collision')

if len(sys.argv) > 1:

    dataPath = Path(sys.argv[1])
    savePath = ''

    if dataPath.is_file() and dataPath.suffix == '.json':
        csvPaths.append(extractData(dataPath))
        savePath = dataPath.parent / 'csv'

    elif dataPath.is_dir():

        savePath = dataPath / 'csv'

        for f in dataPath.iterdir():
            if f.is_file() and f.suffix == '.json':
                csvPaths.append(extractData(f))
        
    # -------------------------------------------------------------------------------------------------- #
    
    df = panda.DataFrame()

    for csvPath in csvPaths:
        _csv = panda.read_csv(csvPath)
        df = df.append(_csv, ignore_index=True)

    df = df.drop(['activation', 'collision'], axis = 1)
    df = df[df['event'] != 'Going By']

    coll = df[filterCollision(df)].sort_values(
            ['std(x)', 'std(z)', '%events'],
            ascending = [False, False, True]
        )

    avoid = df[filterAvoidance(df)].sort_values(
            ['std(x)', 'std(z)', '%events'], 
            ascending = [False, False, False]
        )

    print(coll)
    print(avoid)

    avoid.to_csv(savePath / f'avoid.all.{__date()}.csv', index = False)
    coll.to_csv(savePath / f'coll.all.{__date()}.csv', index = False)

    # ------------------------------------------------------------------

    versions = df['version'].unique()
    modes = df['mode'].unique()

    plot_columns = ['LR','FR', 'CT','%events']
    
    for version in versions:
        for mode in modes:
            
            # ------------------------------------------------------------------

            filtColl = filterModeAndVersion(df, mode, version) & filterCollision(df)
            filtAv = filterModeAndVersion(df, mode, version) & filterAvoidance(df)

            df[filtColl].sort_values(
                ['std(x)', 'std(z)', '%events'],
                ascending = [False, False, True]
            ).to_csv(savePath / f'coll.v{version}.{mode}.{__date()}.csv')

            df[filtColl].sort_values(
                ['std(x)', 'std(z)', '%events'],
                ascending = [False, False, True]
            ).to_csv(savePath / f'avoid.v{version}.{mode}.{__date()}.csv')

            # -------------------------------------------------------------------------------

            xlra, yfra, cta, zea = df[filtAv][plot_columns].T.values

            xlrc, yfrc, ctc, zec = df[filtColl][plot_columns].T.values
            
            trainPlot = figure([xlra, xlrc], [yfra, yfrc], [zea, zec], [cta, ctc])
            trainPlot.suptitle(f'{mode} Data - Ann v{version} - (LR,FR,Score), CT')
            trainPlot.canvas.set_window_title(mode)    

            plotter.subplots_adjust(
                left=0.0,
                right=1.0,
                bottom=0.0,
                top=1.0,
                wspace= 0.0,
                hspace=0.0
            )

    # ------------------------------------------------------------------

    plotter.legend()
    plotter.show()