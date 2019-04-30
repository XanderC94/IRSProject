import math, json, sys, statistics
from collections import OrderedDict
from pathlib import Path
import matplotlib.pyplot as plotter
from mpl_toolkits.mplot3d import axes3d
import pandas as panda
import columns as cols
from utils import Float

neurons = [0, 1, 2, 5, 6, 7]
colors = ['pink', 'cyan', 'green', 'orange', 'red', 'violet']

def connectivities(path: Path) -> panda.DataFrame:
    
    data = {}

    with open(path) as dataFile:
        data = json.load(dataFile)

    df = panda.DataFrame(data)

    for i in neurons:
        df[f'meanw_cn{i}'] = df[f'{i}'].apply(lambda w: statistics.mean(list(w.values())))
        df[f'maxw_cn{i}'] = df[f'{i}'].apply(lambda w: max(list(w.values())))
        df[f'minw_cn{i}'] = df[f'{i}'].apply(lambda w: min(list(w.values())))

        for j in neurons:
            df[f'pn{j}->cn{i}'] = df[f'{i}'].apply(lambda w: w[f'{j}'])

    return df.iloc[:, len(neurons):]

def plot_connevol_stats(connectivities: panda.DataFrame, title:str):

    meanw = list()
    maxw = list()
    minw = list()

    # print(connectivities)

    for n in neurons:
        _meanw, _maxw, _minw = connectivities[[f'meanw_cn{n}', f'maxw_cn{n}', f'minw_cn{n}']].T.values
        meanw.append(_meanw)
        maxw.append(_maxw)
        minw.append(_minw)

    x = range(len(meanw[0]))

    fig, ax = plotter.subplots(6,1, figsize=(12,8), dpi=80)
    plotter.xlabel('step')
    
    for n in range(len(neurons)):

        ax[n].set_ylabel(f'n{neurons[n]}')
        # ax[n].set_ylim(-0.1, 1)
        # ax[n].set_xlim(-10, max(x) + 10)

        ax[n].plot(x, minw[n], color='orange', linewidth=0.75, label="Min Connectivity")
        ax[n].plot(x, maxw[n], color='cyan', linewidth=0.75, label="Max Connectivity")
        ax[n].plot(x, meanw[n], color='purple', linewidth=0.75, label="Mean Connectivity")
    
    handles, labels = fig.gca().get_legend_handles_labels()
    by_label = OrderedDict(zip(labels, handles))
    fig.legend(by_label.values(), by_label.keys(), loc='upper right', fontsize='large')
    
    fig.suptitle(title)

    fig.subplots_adjust(
        left=0.05,
        right=0.95,
        bottom=0.05,
        top=0.95,
        wspace= 0.0,
        hspace=0.25
    )

    fig.canvas.set_window_title(f'{title}_evol_stats')

def plot_connevol(connectivities: panda.DataFrame, title:str):

    ns = {}

    for i in neurons:
        
        n = {}

        for j in neurons: 
            w = connectivities[f'pn{j}->cn{i}'].T.values
            
            n.update({j:w})

        ns.update({i:n})

    x = range(len(ns[0][0]))

    fig, ax = plotter.subplots(6,1, figsize=(12,8), dpi=80)
    plotter.xlabel('step')
    
    for i in range(len(neurons)):

        cn = neurons[i]

        ax[i].set_ylabel(f'n{cn}')

        for j in range(len(neurons)):
            pn = neurons[j]
            ax[i].plot(x, ns[cn][pn], color=colors[j], linewidth=0.5, label=f"Weight Pn{pn}")
    
    handles, labels = fig.gca().get_legend_handles_labels()
    by_label = OrderedDict(zip(labels, handles))
    fig.legend(by_label.values(), by_label.keys(), loc='upper right', fontsize='large')
    
    fig.suptitle(title)

    fig.subplots_adjust(
        left=0.05,
        right=0.95,
        bottom=0.05,
        top=0.95,
        wspace= 0.0,
        hspace=0.25
    )

    fig.canvas.set_window_title(f'{title}_evol')

if __name__== "__main__" and len(sys.argv) > 1:

    dataPath = Path(sys.argv[1])
    # route = panda.DataFrame({})

    if dataPath.is_file() and '.conn.json' in dataPath.name:
        df = connectivities(dataPath)

        plot_connevol_stats(df, dataPath.with_suffix("").name.replace('.', '_'))

        plot_connevol(df, dataPath.with_suffix("").name.replace('.', '_'))

    elif dataPath.is_dir():

        for f in dataPath.iterdir():
            if f.is_file() and '.conn.json' in f.name:
                df = connectivities(f)
                plot_connevol_stats(df, f.with_suffix("").name.replace('.', '_'))

                plot_connevol(df, f.with_suffix("").name.replace('.', '_'))
    
    plotter.show()