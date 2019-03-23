import math, json, sys, copy, os, csv, datetime

import matplotlib.pyplot as plotter
from mpl_toolkits.mplot3d import axes3d
import figure as figure
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

def filterTopStats(df: panda.DataFrame):
    return (df['std(x)'] > 0.2) & (df['std(z)'] > 0.2) & (df['%events'] > 0.8) & (abs(df['%steps'] - df['%events']) < 0.2)

def filterTraps(df: panda.DataFrame):
    return (df['std(x)'] > 0.2) & (df['std(z)'] > 0.2) & (abs(df['%steps'] - df['%events']) < 0.2)

if len(sys.argv) > 1:

    csvDirPath = Path(sys.argv[1])
    savePath = csvDirPath / 'res'

    if not savePath.exists():
        savePath.mkdir()

    if not csvDirPath.is_dir():
        raise Exception('Argument is not a directory.')
    
    # -------------------------------------------------------------------------------------------------- #
    
    df = panda.DataFrame()

    for csvPath in csvDirPath.iterdir():
        if 'csv' in csvPath.suffix:
            _csv = panda.read_csv(csvPath)
            df = df.append(_csv, ignore_index=True)

    df = df.drop(['activation', 'collision'], axis = 1)
    df = df[df['event'] != 'Going By']

    coll = df[filterCollision(df)].sort_values(
            ['mEventSteps', '%events', 'std(x)', 'std(z)'],
            ascending = [True, True, False, False]
        )

    avoid = df[filterAvoidance(df)].sort_values(
            ['mEventSteps', '%events', 'std(x)', 'std(z)'], 
            ascending = [True, False, False, False]
        )

    top_avoid = avoid[filterTopStats(avoid)]
    top_coll = coll[coll['origin'].isin(top_avoid['origin'])]
    
    print(top_coll)
    print(top_avoid)

    avoid.to_csv(savePath / f'res.avoid.all.{__date()}.csv', index = False)
    coll.to_csv(savePath / f'res.coll.all.{__date()}.csv', index = False)

    # ------------------------------------------------------------------

    versions = df['version'].unique()
    modes = df['mode'].unique()

    plot_columns = ['LR','FR','%events', 'CT']
    
    for version in versions:
        for mode in modes:
            
            # ------------------------------------------------------------------

            filtColl = filterModeAndVersion(df, mode, version) & filterCollision(df)
            filtAv = filterModeAndVersion(df, mode, version) & filterAvoidance(df)

            df[filtColl].sort_values(
                ['std(x)', 'std(z)', '%events'],
                ascending = [False, False, True]
            ).to_csv(savePath / f'res.coll.v{version}.{mode}.{__date()}.csv')

            df[filtColl].sort_values(
                ['std(x)', 'std(z)', '%events'],
                ascending = [False, False, True]
            ).to_csv(savePath / f'res.avoid.v{version}.{mode}.{__date()}.csv')

            # -------------------------------------------------------------------------------

            xa, ya, za, ta = df[filtAv & filterTraps(df)][plot_columns].sort_values(['LR', 'FR'], ascending = [True, True]).T.values

            xy = [ (xi, yi) for xi, yi in zip(xa, ya)]

            __x = [float(i / len(xy)) for i in range(0, len(xy))]

            # xc, yc, zc, tc = df[filtColl][plot_columns].T.values
            
            plot = figure.scatterplot(
                [__x], [ta], [za], [xy], 
                limits={'x':[0, 1], 'y':[0.6, 1.0], 'z':[0, 1]},
                labels={'x':'(LR, FR)', 'y': 'Collision Threshold', 'z':'% Avoided'},
                info=figure.tuple_label
            )

            plot.suptitle(f'{mode} Data - Ann v{version} - x:(%s, %s), y: %s, z:%s' % (plot_columns[0], plot_columns[1], plot_columns[3], plot_columns[2]))
            plot.canvas.set_window_title(mode)    

            plotter.subplots_adjust(
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
                [__x], [za], [xyt]
            )

            for xyti in xyt: print(xyti) 

            plot.suptitle(f'{mode} Data - Ann v{version} - x:(%s, %s, %s), y: %s' % (plot_columns[0], plot_columns[1], plot_columns[3], plot_columns[2]))
            plot.canvas.set_window_title(mode)    

            plotter.subplots_adjust(
                left=0.05,
                right=0.97,
                bottom=0.05,
                top=0.91,
                wspace= 0.0,
                hspace=0.0
            )

    # ------------------------------------------------------------------
    plotter.legend(loc='best')
    plotter.grid()
    plotter.show()