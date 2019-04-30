import math, json, sys
from pathlib import Path
import matplotlib.pyplot as plotter
from mpl_toolkits.mplot3d import axes3d
import pandas as panda
import columns as cols
from utils import Float

class Obstacle():

    def __init__(self, position: (float, float), w:float, d:float):
        self.position = {'x':position[0], 'z':position[1]}
        self.depth = d
        self.width = w

obstacles = [
    Obstacle((-0.48, 0.51), 0.25, 0.25),
    Obstacle((0.5, 1.70003e-16), 0.25, 0.25),
    Obstacle((0.25, 0.25), 0.25, 0.25),
    Obstacle((-0.48, -0.51), 0.25, 0.25),
    Obstacle((0.0, -1.0), 2.0, 0.01),
    Obstacle((-1.0, 0.0), 0.01, 2.0),
    Obstacle((0.0, 1.0), 2.0, 0.01),
    Obstacle((1.0, 0.0), 0.01, 2.0)
]

def trajectory(path: Path) -> panda.DataFrame:

    data = {}

    with open(path) as dataFile:
        data = json.load(dataFile)
    
    df = panda.DataFrame(data['log'])

    df['xc'] = df['position'].apply(lambda p: p['X'])
    df['zc'] = df['position'].apply(lambda p: p['Z'])

    return df[['xc', 'zc']]

def plot_trajectory(trajectory: panda.DataFrame, title: str):
   
    x, z = trajectory.T.values

    fig = plotter.figure()
    ax = fig.add_subplot(1,1,1)

    ax.set_xlabel('z')
    ax.set_ylabel('x')

    maxx = max(x) 
    minx = min(x)
    maxz = max(z)
    minz = min(z)

    ax.set_ylim(minx - 0.25, maxx + 0.25)
    ax.set_xlim(minz - 0.25, maxz + 0.25)

    ax.scatter(z[0], x[0], linewidth=2, color="g")
    ax.annotate(
        f'Start', 
        xy= (z[0], x[0]),
        xytext= (z[0], x[0]),
        va='top',
        xycoords='data', 
        textcoords='data'
    )

    ax.plot(z, x, color='blue', label="Trajectory")
    ax.plot([], [], color='r', linestyle='--', label="Expectation")

    ax.scatter(z[len(z)-1], x[len(x)-1], linewidth=2, color="r")
    ax.annotate(
        f'Stop', 
        xy=(z[len(z)-1], x[len(x)-1]),
        xytext= (z[len(z)-1], x[len(x)-1]),
        va='top',
        xycoords='data', 
        textcoords='data'
    )

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

    ax.legend(loc='upper right', fontsize='small')

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
        r = trajectory(dataPath)
        plot_trajectory(r, dataPath.with_suffix("").name)

    elif dataPath.is_dir():

        for f in dataPath.iterdir():
            if f.is_file() and not ('.log' in f.name) and f.suffix == '.json':
                r = trajectory(f)
                plot_trajectory(r, f.with_suffix("").name)
    
    plotter.show()