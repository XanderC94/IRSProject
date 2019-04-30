import math, json, sys
from pathlib import Path
import matplotlib.pyplot as plotter
from mpl_toolkits.mplot3d import axes3d
import pandas as panda
import columns as cols
from utils import Float
from collections import OrderedDict

def dist(p1:(float, float), p2:(float, float)) -> float:

    return math.sqrt( ((p1[0] - p2[0])**2) + ((p1[1] - p2[1])**2) )

class Obstacle():

    def __init__(self, position: (float, float), w:float, d:float):
        self.position = {'x':position[0], 'z':position[1]}
        self.depth = d
        self.width = w

obstacles = [
    Obstacle((-0.48, 0.51), 0.25, 0.25),
    Obstacle((0.5, 1.70003e-16), 0.25, 0.25),
    # Obstacle((0.25, 0.25), 0.25, 0.25),
    Obstacle((-0.48, -0.51), 0.25, 0.25),
    Obstacle((0.0, -1.0), 2.0, 0.01),
    Obstacle((-1.0, 0.0), 0.01, 2.0),
    Obstacle((0.0, 1.0), 2.0, 0.01),
    Obstacle((1.0, 0.0), 0.01, 2.0)
]

def paths(path: Path) -> panda.DataFrame:

    data = {}

    with open(path) as dataFile:
        data = json.load(dataFile)
    
    fdata = list(filter(lambda d: d['activation'], data['log']))

    prev = fdata[0]
    prev['nEvent'] = 0

    for e in fdata[1:]:

        p1 = prev['position']
        p2 = e['position']

        distance = dist((p1['X'], p1['Z']), (p2['X'], p2['Z']))

        if distance < 0.1:
            e['nEvent'] = prev['nEvent']
        else:
            e['nEvent'] = prev['nEvent'] + 1

        prev = e

    df = panda.DataFrame(fdata).rename(columns = {'step_number':'nStep'})

    df['xc'] = df['position'].apply(lambda p: p['X'])
    df['zc'] = df['position'].apply(lambda p: p['Z'])

    return df[df['activation'] == True][['nEvent','xc', 'zc', 'collision', 'nStep']]

def plot_paths(trajectory: panda.DataFrame, title: str):
    
    # print(trajectory)

    s = trajectory['nEvent'].unique()

    fig = plotter.figure()
    ax = fig.add_subplot(1,1,1)

    ax.set_xlabel('z')
    ax.set_ylabel('x')

    last_ann = None

    for seq in s:

        x, z = trajectory[trajectory['nEvent'] == seq][['xc', 'zc']].T.values

        count = list(trajectory[trajectory['nEvent'] == seq].groupby(['collision']).agg({'nEvent':'count'})['nEvent'].T.values)

        r = count[1] / sum(count) if len(count) > 1 else 0

        # step = trajectory[trajectory['nEvent'] == seq]['nStep'].T.values[0]

        ax.scatter(z[0], x[0], linewidth=2, color="g", label="Start")

        if last_ann is None or dist(last_ann.xy, (z[0], x[0])) > 0.35:
            
            last_ann = ax.annotate(
                f'{seq}', 
                xy= (z[0], x[0]),
                xytext= (z[0], x[0]),
                va='top',
                xycoords='data', 
                textcoords='data'
            )

        ax.plot(z, x, color=('blue' if r == 0 else 'purple'))
        ax.plot([], [], color='blue', label='Avoidance')
        ax.plot([], [], color='purple', label='Collision')

        ax.scatter(z[len(z)-1], x[len(x)-1], linewidth=2, color="r", label = "Stop")
        

    for obstacle in obstacles:
     
        ox = [
            obstacle.position['x'] + obstacle.width / 2,
            obstacle.position['x'] - obstacle.width / 2,
            obstacle.position['x'] - obstacle.width / 2,
            obstacle.position['x'] + obstacle.width / 2
        ]

        oz = [
            obstacle.position['z'] + obstacle.depth / 2,
            obstacle.position['z'] + obstacle.depth / 2,
            obstacle.position['z'] - obstacle.depth / 2,
            obstacle.position['z'] - obstacle.depth / 2
        ]

        ax.fill(oz, ox, color='k', fill=True)

    handles, labels = fig.gca().get_legend_handles_labels()
    by_label = OrderedDict(zip(labels, handles))
    fig.legend(by_label.values(), by_label.keys(), loc='upper right', fontsize='large')

    fig.suptitle(title)

    fig.canvas.set_window_title(f'{title}_trajectory')

    fig.subplots_adjust(
        left=0.05,
        right=0.95,
        bottom=0.05,
        top=0.95,
        wspace= 0.0,
        hspace=0.0
    )

# ---------------------------------------------------------------------------------------------------------
if __name__== "__main__" and len(sys.argv) > 1:

    dataPath = Path(sys.argv[1])
    # route = panda.DataFrame({})

    if dataPath.is_file() and not ('.log' in dataPath.name) and  dataPath.suffix == '.json':
        r = paths(dataPath)
        plot_paths(r, dataPath.with_suffix("").name)

    elif dataPath.is_dir():

        for f in dataPath.iterdir():
            if f.is_file() and not ('.log' in f.name) and f.suffix == '.json':
                r = paths(f)
                plot_paths(r, f.with_suffix("").name)
    
    plotter.show()