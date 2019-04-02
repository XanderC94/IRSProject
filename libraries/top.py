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
    saveDir = Path('')
    # -------------------------------------------------------------------------------------------------- #
    
    df = panda.DataFrame() 

    if dataPath.is_dir():

        saveDir = dataPath / 'top'

        for csvPath in dataPath.iterdir():
            if 'csv' in csvPath.suffix:
                _csv = panda.read_csv(csvPath)
                df = df.append(_csv, ignore_index=True)

    elif dataPath.is_file() and 'csv' in dataPath.suffix:
        df = panda.read_csv(dataPath)
        saveDir = dataPath.parent / 'top'

    if not saveDir.exists():
        saveDir.mkdir()

    versions = df['version'].unique()

    for version in versions:
        
        # Align Test models IDs with their trained counterpart
        idx_trains = df[filterModeAndVersion(df, 'train', version)][['index', 'LR', 'FR', 'CT']]
        tests = df[filterModeAndVersion(df, 'test', version)]
                
        if len(idx_trains) > 0 and len(tests) > 0:
            
            df.drop(tests.index, inplace=True)
            tests = idx_trains.merge(tests.iloc[:, 1:], on=['LR', 'FR', 'CT'], how='inner')[['index'] + cols.ordered_columns]
            df = df.append(tests, ignore_index=True, sort=False)

    plot_columns = ['index', 'version', 'mode', 'LR','FR','CT', 'nGoingBySteps', 'mAvoidSteps', '%AvoidSteps', 'std(x)', 'std(z)']

    topstats = df[filterTopStats(df) & (df['mode'] == 'test')][plot_columns]

    __stubdf = panda.DataFrame()

    __stubdf['mean_std'] = (topstats['std(x)'] + topstats['std(z)']) / 2
    __stubdf['std'] = (topstats['std(x)'] - __stubdf['mean_std']) * (topstats['std(x)'] - __stubdf['mean_std']) + (topstats['std(z)'] - __stubdf['mean_std']) * (topstats['std(z)'] - __stubdf['mean_std'])

    __stubdf['std'] = (__stubdf['std'] / 2) ** 0.5

    topstats['rank'] = (__stubdf['mean_std'] * 0.35 - __stubdf['std'] * 0.05 + topstats['%AvoidSteps'] * 0.6) / 1.0
    
    # print(topstats)

    topstats.sort_values(['rank'], ascending=[False]).to_csv(saveDir / f'topstats.all.{getDate()}.csv', index=False)

    # ------------------------------------------------------------------
