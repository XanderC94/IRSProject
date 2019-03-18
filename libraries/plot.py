import math, json, sys, copy, os, csv

import matplotlib.pyplot as plotter
from mpl_toolkits.mplot3d import axes3d
from matplotlib import cm

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

    print(df[filterCollision(df)].sort_values(['version', 'mode', '%events']))
    print(df[filterAvoidance(df)].sort_values(['version', 'mode', '%events'], ascending = False))

    exit(0)

    fig = plotter.figure() 
    axlr = fig.add_subplot(1,1,1, projection='3d')
    
    xlr = df[filterModeAndVersion(df, 'train', 2) & filterAvoidance(df)]['LR'].values
    yfr = df[filterModeAndVersion(df, 'train', 2) & filterAvoidance(df)]['FR'].values

    zAvEvents = df[filterModeAndVersion(df, 'train', 2) & filterAvoidance(df)]['%events'].values
    zCollEvents = df[filterModeAndVersion(df, 'train', 2) & filterCollision(df)]['%events'].values

    xlr, yfr, zAvEvents = np.meshgrid(xlr, yfr, zAvEvents)

    # Avoidance events evolution by LearningRate variation
    axlr.plot_surface(
        xlr,
        yfr, 
        zAvEvents,
        label='avoidance events', 
        linewidth=0.1
    )

    xlr, yfr, zCollEvents = np.meshgrid(xlr, yfr, zAvEvents)

    # Collision events evolution by LearningRate variation
    axlr.plot_surface(
        xlr,
        yfr, 
        zCollEvents,
        label='collision events', 
        linewidth=0.1
    )

    axlr.set_xlim(0, 1.1)
    axlr.set_ylim(0, 1.1)
    axlr.set_zlim(0, 1.1)

    cset = axlr.contourf(xlr, yfr, zAvEvents, zdir='x', offset=0, cmap=cm.coolwarm)
    cset = axlr.contourf(xlr, yfr, zAvEvents, zdir='y', offset=0, cmap=cm.coolwarm)
    cset = axlr.contourf(xlr, yfr, zAvEvents, zdir='z', offset=0, cmap=cm.coolwarm)

    # zAvSteps = df[filterModeAndVersion(df, 'train', 2) & filterAvoidance(df)]['%steps'].values
    # zCollSteps = df[filterModeAndVersion(df, 'train', 2) & filterCollision(df)]['%steps'].values
    
    # # Avoidance step evolution by LearningRate variation
    # axlr.plot_surface(
    #     xlr,
    #     yfr, 
    #     zAvSteps,
    #     label='avoidance steps', 
    #     linewidth=0.1
    # )

    # # Collision steps evolution by LearningRate variation
    # axlr.plot_surface(
    #     xlr,
    #     yfr, 
    #     zCollSteps,
    #     label='collision steps', 
    #     linewidth=0.1
    # )


    plotter.legend()
    plotter.show()