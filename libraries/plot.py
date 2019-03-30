import math, json, sys, copy, os, csv, datetime

import matplotlib.pyplot as plotter
from mpl_toolkits.mplot3d import axes3d
import figure as figure

from pathlib import Path

from utils import *

import pandas as panda
import numpy as np

# ------------------------------------------------------------------------------------------------------ #

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

    plot_columns = ['index','LR','FR','CT', '%AvoidSteps', 'mAvoidSteps']

    # ------------------------------------------------------------------

    versions = df['version'].unique()
    modes = df['mode'].unique()

    for version in versions:
        
        # Align Test models IDs with their trained counterpart
        idx_trains = df[filterModeAndVersion(df, 'train', version)][['index', 'LR', 'FR', 'CT']]
        tests = df[filterModeAndVersion(df, 'test', version)]
                
        if len(idx_trains) > 0 and len(tests) > 0:
            
            df.drop(tests.index, inplace=True)
            tests = idx_trains.merge(tests.iloc[:, 1:], on=['LR', 'FR', 'CT'], how='inner')[['index'] + cols.ordered_columns]
            df = df.append(tests, ignore_index=True, sort=False)

        for mode in modes:
            
            # ------------------------------------------------------------------

            filt = filterModeAndVersion(df, mode, version) & filterFalsePositives(df)

            # -------------------------------------------------------------------------------

            data = df[filt][plot_columns].sort_values(['LR', 'FR', 'CT'], ascending = [True, True, True])

            if len(data) > 0:

                idx, lr, fr, ct, hs, ms = data.T.values

                ts = [(xi, yi, ti) for xi, yi, ti in zip(lr, fr, ct)]

                wmax = max(ms) * 1.1
                ws = [5*(1.0 - float(wi / wmax)) for wi in ms]

                xs = [(i + w) * 1.2 for i, w in zip(idx, np.cumsum(ws))]

                plot = figure.stackedbars2d(
                    xs, hs, ws, ts, idx,
                    limits={'x':[min(xs), max(xs) * 1.1],'y':[0, 1.05]},
                    hfilter=0.8
                )

                plot.suptitle(
                    f'{mode} Data - Ann v{version} - x:(%s, %s, %s), y: %s' % (
                        plot_columns[1], plot_columns[2], plot_columns[3], plot_columns[4]
                    )
                )

                plot.canvas.set_window_title(f'{mode}.annv{version}.2d')    

                plot.subplots_adjust(
                    left=0.03,
                    right=0.99,
                    bottom=0.09,
                    top=0.96,
                    wspace= 0.0,
                    hspace=0.0
                )

                if not (mode == 'test'):
                    xy = [ (xi, yi) for xi, yi in zip(lr, fr)]

                    x = [float(i / len(xy)) for i in range(0, len(xy))]

                    plot = figure.scatterplot(
                        [x], [ct], [hs], [xy],
                        legend=['controller model'],
                        limits={'x':[0, 1], 'y':[0.6, 1.0], 'z':[0, 1]},
                        labels={'x':'(LR, FR)', 'y': 'Collision Threshold', 'z':'% Avoided Collisions'},
                        info=figure.tuple_label
                    )

                    plot.suptitle(
                        f'{mode} Data - Ann v{version} - x:(%s, %s), y: %s, z:%s' % (
                            plot_columns[1], plot_columns[2], plot_columns[3], plot_columns[4]
                        )
                    )

                    plot.canvas.set_window_title(f'{mode}.annv{version}.3d')

                    plot.subplots_adjust(
                        left=0.0,
                        right=1.0,
                        bottom=0.0,
                        top=1.0,
                        wspace= 0.0,
                        hspace=0.0
                    )

        df.drop(df[(df['version'] == version)].index, inplace=True)
    # ------------------------------------------------------------------
    
    plotter.show()