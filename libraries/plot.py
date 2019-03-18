import matplotlib.pyplot as plotter
from data import extractData
import math, json, sys, copy, os, csv
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

    print(df)

    # fig, ax = plotter.subplots(1,1)
    
    # ax.plot(
    #     df['step_number'].values, 
    #     df['touched'].values, 
    #     label='results', 
    #     linewidth=0.5)

    # plotter.legend()
    # plotter.show()