import matplotlib.pyplot as plotter
from mpl_toolkits.mplot3d import axes3d
import numpy as np

point_label = lambda x,y,z,t: '(%.2f, %.2f, %.2f), %.2f' % (x, y, float(z).__round__(2), t)
tuple_label = lambda x,y,z,t: ','.join(['%g' for _ in range(0, len(t))]) % t

def scatterplot(xs:list, ys:list, zs:list, ts:list, 
    legend = ['avoidance events', 'collision events'], 
    colors = ['green', 'orange'],
    labels = {'x':'Learning Rate', 'y':'Forget Rate', 'z':'% Avoided Collisions'},
    limits = {'x':[0.03, 0.07],'y':[0.5, 1],'z':[0, 1]},
    info = point_label):

    fig = plotter.figure()
    
    ax = fig.add_subplot(1,1,1, projection='3d')
    
    ax.set_xlabel(labels['x'])
    ax.set_ylabel(labels['y'])
    ax.set_zlabel(labels['z'])

    ax.set_xlim(limits['x'][0], limits['x'][1])
    ax.set_ylim(limits['y'][0], limits['y'][1])
    ax.set_zlim(limits['z'][0], limits['z'][1])

    # -------------------------------------------------------------------------------------------------------
    
    for i in range(0, len(xs)):
        
        x = xs[i]
        y = ys[i]
        z = zs[i]
        t = ts[i]

        color = colors[i]
        label = legend[i]

        # Avoidance events evolution by LearningRate variation
        ax.scatter(
            x, y, z,
            label=label,
            color=color,
            depthshade = False
        )
        
        for _x, _y, _z, _c in zip(x, y, z, t):
            if (_z > 0.8):
                ax.text(_x, _y, _z, info(_x, _y, _z, _c), fontsize='xx-small')

    # ---------------------------------------------------------------------------------------------

    return fig

def plot2d(xs:list, ys:list, ts:list, 
    legend = ['avoidance events'], 
    colors = ['green'],
    labels = {'x':'(LR, FR, CT)', 'y':'% Avoided Collisions'},
    limits = {'x':[-0.2, 1.2],'y':[-0.2, 1.2]},
    info = tuple_label):

    fig = plotter.figure()
    
    ax = fig.add_subplot(1,1,1)
    
    ax.set_xlabel(labels['x'])
    ax.set_ylabel(labels['y'])

    ax.set_xlim(limits['x'][0], limits['x'][1])
    ax.set_ylim(limits['y'][0], limits['y'][1])

    # ax.set_xticks(np.arange(limits['x'][0], limits['x'][1], 0.05))
    ax.set_yticks(np.arange(limits['y'][0], limits['y'][1], 0.1))

    # -------------------------------------------------------------------------------------------------------
    
    for i in range(0, len(xs)):
        
        x = xs[i]
        y = ys[i]
        t = ts[i]

        color = colors[i]
        label = legend[i]

        plotter.rc('grid', linestyle="--", color='lightgray')
    
        ax.plot(
            x, y,
            # label=label,
            color=color,
            linewidth= 0.5
        )

        ax.scatter(
            x, y,
            color='k'
        )
        
        basey = 1.0
        offy = 0.025
        offystep = 0.075

        offx = -0.2
        offxstep = 0.0115

        for _x, _y, _c in zip(x, y, t):
            if (_y > 0.8):
                text = ax.annotate(
                    info(0.0, 0.0, 0.0, _c), 
                    xy=(_x, _y),
                    xytext=(_x + offx, basey + offy),
                    fontsize='xx-small', 
                    va='top',
                    xycoords='data', 
                    textcoords='data',
                    arrowprops=dict(
                        arrowstyle="->",
                        color="0.75"
                    )
                )
                offy = offy + offystep if basey + offy < limits['y'][1] else 0.025
                offx = offx + offxstep
    # ---------------------------------------------------------------------------------------------
    
    return fig