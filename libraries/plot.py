import math, json, sys, copy, os, csv, datetime

import matplotlib.pyplot as plotter
from mpl_toolkits.mplot3d import axes3d
import figure as figure
from data import extractData

from pathlib import Path

import pandas as panda
import numpy as np

# ------------------------------------------------------------------------------------------------------ #

def filterModeAndVersion(df: panda.DataFrame, mode:str, version:int):
    return (df['version'] == version) & (df['mode'] == mode)

def filterTopStats(df: panda.DataFrame):
    return (df['std(x)'] > 0.2) & (df['std(z)'] > 0.2) & (df['%AvoidSteps'] > 0.8) # & (abs(df['%AvoidSteps'] - df['%AvoidEvents']) < 0.2)

def filterFalsePositives(df: panda.DataFrame):
    return (df['std(x)'] > 0.2) & (df['std(z)'] > 0.2) # & (abs(df['%AvoidSteps'] - df['%AvoidEvents']) < 0.2)

if len(sys.argv) > 1:

    dataPath = Path(sys.argv[1])
    
    # -------------------------------------------------------------------------------------------------- #
    
    df = panda.DataFrame() 

    if dataPath.is_dir():
        for csvPath in dataPath.iterdir():
            if 'csv' in csvPath.suffix:
                _csv = panda.read_csv(csvPath)
                df = df.append(_csv, ignore_index=True)

    elif dataPath.is_file() and 'csv' in dataPath.suffix:
        df = panda.read_csv(dataPath)

    # top = df[filterTopStats(df)].iloc[:, 2:12]
    
    # print(top)

    # ------------------------------------------------------------------

    versions = df['version'].unique()
    modes = df['mode'].unique()

    plot_columns = ['index','LR','FR','%AvoidSteps', 'CT']
    
    for version in versions:
        for mode in modes:
            
            # ------------------------------------------------------------------

            filt = filterModeAndVersion(df, mode, version) & filterFalsePositives(df)

            # -------------------------------------------------------------------------------

            data = df[filt][plot_columns].sort_values(['LR', 'FR', 'CT'], ascending = [True, True, True])

            idx, xa, ya, za, ta = data.T.values

            xy = [ (xi, yi) for xi, yi in zip(xa, ya)]

            __x = [float(i / len(xy)) for i in range(0, len(xy))]
            
            plot = figure.scatterplot(
                [__x], [ta], [za], [xy], 
                limits={'x':[0, 1], 'y':[0.6, 1.0], 'z':[0, 1]},
                labels={'x':'(LR, FR)', 'y': 'Collision Threshold', 'z':'% Avoided Collisions'},
                info=figure.tuple_label
            )

            plot.suptitle(
                f'{mode} Data - Ann v{version} - x:(%s, %s), y: %s, z:%s' % (
                    plot_columns[0], plot_columns[1], plot_columns[3], plot_columns[2]
                )
            )

            plot.canvas.set_window_title(mode)    

            plot.subplots_adjust(
                left=0.0,
                right=1.0,
                bottom=0.0,
                top=1.0,
                wspace= 0.0,
                hspace=0.0
            )

            xyt = [ (xi, yi, ti) for xi, yi, ti in zip(xa, ya, ta)]

            __x = [float(i / len(xyt)) for i in range(0, len(xyt))]

            plot = figure.plot2d(
                [__x], [za], [xyt],
                ids=[idx],
                yfilter=0.8
            )

            plot.suptitle(
                f'{mode} Data - Ann v{version} - x:(%s, %s, %s), y: %s' % (
                    plot_columns[0], plot_columns[1], plot_columns[3], plot_columns[2]
                )
            )

            plot.canvas.set_window_title(mode)    

            plot.subplots_adjust(
                left=0.05,
                right=0.99,
                bottom=0.05,
                top=0.96,
                wspace= 0.0,
                hspace=0.0
            )

    # ------------------------------------------------------------------
    
    plotter.show()