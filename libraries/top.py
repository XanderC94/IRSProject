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

    plot_columns = ['index', 'version', 'mode', 'LR','FR','CT', 'nGoingBySteps', 'mAvoidSteps', '%AvoidSteps', 'std(x)', 'std(z)']

    topstats = df[filterTopStats(df, stdx=0.25, stdz=0.25) & (df['mode'] == 'test')][plot_columns].sort_values(['std(x)', 'std(z)', '%AvoidSteps'], ascending=[False, False, False])
    
    # print(topstats)

    topstats.to_csv(saveDir / f'topstats.all.{getDate()}.csv', index=False)

    # ------------------------------------------------------------------
