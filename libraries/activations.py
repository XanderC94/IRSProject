import math, json, sys
from collections import OrderedDict
from pathlib import Path
import matplotlib.pyplot as plotter
from mpl_toolkits.mplot3d import axes3d
import pandas as panda
import columns as cols
from utils import Float

neurons = [0, 1, 2, 5, 6, 7]
colors = ['pink', 'cyan', 'green', 'orange', 'red', 'violet']

def activation(path: Path) -> panda.DataFrame:
    
    data = {}

    with open(path) as dataFile:
        data = json.load(dataFile)

    df = panda.DataFrame(data)

    for i in neurons:
        df[f'n{i}'] = df['collision_pattern'].apply(lambda p: p[f'{i}'])
        df[f'd{i}'] = df['distances'].apply(lambda d: d[i])
        df[f'ci{i}'] = df['collision_input'].apply(lambda c: c[neurons.index(i)])

    return df.iloc[:, 2:]

def plot_activation(activations: panda.DataFrame, title:str):

    a = list()
    d = list()
    c = list()

    for n in neurons:
        an, dn, cn = activations[[f'n{n}', f'd{n}', f'ci{n}']].T.values
        a.append(an)
        d.append(dn)
        c.append(cn)

    x = range(len(a[0]))

    fig, ax = plotter.subplots(6,1, figsize=(12,8), dpi=80)
    plotter.xlabel('step')
    
    for n in range(len(a)):

        ax[n].set_ylabel(f'n{neurons[n]}')
        ax[n].set_ylim(-0.1, 1.25)
        ax[n].set_xlim(-10, max(x) + 10)

        ax[n].plot(x, d[n], color='black', linewidth=0.75, label="Proximity")
        # ax[n].plot(x, list(map(lambda x: math.exp(-x), d[n])), color='green', linewidth=0.75, linestyle='-', label="Proximity Output")
        ax[n].plot(x, c[n], color='purple', linewidth=0.75, linestyle='-', label="Collision Input")
        ax[n].plot(x, a[n], color='cyan', linewidth=0.85, linestyle='-', label="Activation")
    
    handles, labels = fig.gca().get_legend_handles_labels()
    by_label = OrderedDict(zip(labels, handles))
    fig.legend(by_label.values(), by_label.keys(), loc='upper right', fontsize='large')

    # fig.legend()
    
    fig.suptitle(title)

    fig.subplots_adjust(
        left=0.05,
        right=0.95,
        bottom=0.05,
        top=0.95,
        wspace= 0.0,
        hspace=0.25
    )

    fig.canvas.set_window_title(f'{title}_activations')

if __name__== "__main__" and len(sys.argv) > 1:

    dataPath = Path(sys.argv[1])
    # route = panda.DataFrame({})

    if dataPath.is_file() and '.log.json' in dataPath.name:
        df = activation(dataPath)
        plot_activation(df, dataPath.with_suffix("").name.replace('.log', ''))

    elif dataPath.is_dir():

        for f in dataPath.iterdir():
            if f.is_file() and '.log.json' in f.name:
                df = activation(f)
                plot_activation(df, f.with_suffix("").name.replace('.log', ''))
    
    plotter.show()