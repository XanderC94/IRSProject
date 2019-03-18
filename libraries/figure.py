import matplotlib.pyplot as plotter
from mpl_toolkits.mplot3d import axes3d
import numpy as np


point_label = lambda x,y,z,c: '(%.2f, %.2f, %.2f), ct=%.2f' % (x, y, float(z).__round__(2), c)

def figure(xs:list, ys:list, zs:list, cts:list, 
    labels = ['avoidance events', 'collision events'], 
    colors = ['green', 'orange']):

    fig = plotter.figure()
    
    ax = fig.add_subplot(1,1,1, projection='3d')
    
    ax.set_xlabel('Learning Rate')
    ax.set_ylabel('Forget Rate')
    ax.set_zlabel('% Avoided Collisions')

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_zlim(0, 1)

    major_ticks = np.arange(0, 1, 0.1)

    ax.set_yticks(major_ticks)
    ax.set_xticks(major_ticks)
    ax.set_zticks(major_ticks)

    ax.grid(which='both', alpha='0.2')

    # -------------------------------------------------------------------------------------------------------
    text = []
    for i in range(0, len(zs)):
        
        x = xs[i]
        y = ys[i]
        z = zs[i]
        t = cts[i]

        color = colors[i]
        label = labels[i]

        # Avoidance events evolution by LearningRate variation
        ax.scatter(
            x, y, z,
            label=label, 
            # linewidth=0.1,
            color=color
        )

        ax.plot(x, y, 0.0, zdir = 'z', linewidth=0.5, color=color)
        ax.plot(x, z, 1.0, zdir = 'y', linewidth=0.5, color=color)
        ax.plot(y, z, 0.0, zdir = 'x', linewidth=0.5, color=color)

        for _x, _y, _z, _c in zip(x, y, z, t):
            info = ax.text(_x, _y, _z, point_label(_x, _y, _z, _c), fontsize='xx-small')
            text.append(info)
            # info.set_visible(False)

    # ---------------------------------------------------------------------------------------------

    # fig.canvas.mpl_connect("motion_notify_event", _hover)
    

    return fig