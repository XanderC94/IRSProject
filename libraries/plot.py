import math, json, sys, copy, os, csv

import matplotlib.pyplot as plotter
from mpl_toolkits.mplot3d import axes3d
from figure import figure
from data import extractData

from pathlib import Path

import pandas as panda
import numpy as np

# ------------------------------------------------------------------------------------------------------ #

csvPaths = { }

def extractAndStore(path: Path):
    csvPath, mode, version = extractData(path)

    if not version in csvPaths:
        csvPaths.update({version:{}})

    if mode in csvPaths[version]:
        csvPaths[version][mode].append(csvPath)
    else:
        csvPaths[version].update({mode:[csvPath]})

def filterModeAndVersion(df: panda.DataFrame, mode:str, version:int):
    return (df['version'] == version) & (df['mode'] == mode)

def filterAvoidance(df: panda.DataFrame):
    return (df['event'] == 'Avoidance')

def filterCollision(df: panda.DataFrame):
    return (df['event'] == 'Collision')

if len(sys.argv) > 1:

    dataPath = Path(sys.argv[1])

    if dataPath.is_file() and dataPath.suffix == '.json':
        extractAndStore(dataPath)

    elif dataPath.is_dir():

        for f in dataPath.iterdir():
            if f.is_file() and f.suffix == '.json':
                extractAndStore(f)

    # -------------------------------------------------------------------------------------------------- #
    
    df = panda.DataFrame()

    for version, modes in csvPaths.items():
        for mode, csvPathList in modes.items():
            for csvPath in csvPathList:
                _df = panda.read_csv(csvPath)
                _df['version'] = version
                _df['mode'] = mode
                df = df.append(_df, ignore_index=True)

    df = df.drop(['activation', 'collision'], axis = 1)
    df = df[df['event'] != 'Going By']

    print(df[filterCollision(df)].sort_values(
            ['version', 'mode', 'std(x)', 'std(z)', '%events'],
            ascending = [True, True, False, False, True]
        )
        
    )

    print(df[filterAvoidance(df)].sort_values(
            ['version', 'mode', 'std(x)', 'std(z)', '%events'], 
            ascending = [True, True, False, False, False]
        )
    )

    # ------------------------------------------------------------------

    versions = df['version'].unique()
    modes = df['mode'].unique()

    print(modes, versions)

    plot_columns = ['LR','FR', 'CT','%events']
    
    for version in versions:
        for mode in modes:

            xlra, yfra, cta, zea = (
                df[filterModeAndVersion(df, mode, version) & filterAvoidance(df)][plot_columns].T.values
            )

            xlrc, yfrc, ctc, zec = (
                df[filterModeAndVersion(df, mode, version) & filterCollision(df)][plot_columns].T.values
            )
            
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