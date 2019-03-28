import matplotlib.pyplot as plotter
from mpl_toolkits.mplot3d import axes3d
import matplotlib.cm as cmx
import matplotlib.colors as clrs
import numpy as np

point_label = lambda x,y,z,t: '(%.2f, %.2f, %.2f), %.2f' % (x, y, float(z).__round__(2), t)
tuple_label = lambda x,y,z,t: ','.join(['%g' for _ in range(0, len(t))]) % t

__colors = ['#990c41', 'blue', '#228b22', 'orange', '#222222', '#9f1f19', 'violet', 'purple', 'salmon', '#008080']

def scatterplot(xs:list, ys:list, zs:list, ts:list, 
    legend = ['avoidance events', 'collision events'], 
    colors = ['green', 'orange'],
    labels = {'x':'Learning Rate', 'y':'Forget Rate', 'z':'% Avoided Collisions'},
    limits = {'x':[0.03, 0.07],'y':[0.5, 1],'z':[0, 1]},
    zfilter = 0.9,
    info = point_label):

    plotter.rc('grid', linestyle=":", color='lightgray')
    
    fig = plotter.figure()
    
    ax = fig.add_subplot(1,1,1, projection='3d')
    
    ax.set_xlabel(labels['x'])
    ax.set_ylabel(labels['y'])
    ax.set_zlabel(labels['z'])

    ax.set_xlim(limits['x'][0], limits['x'][1])
    ax.set_ylim(limits['y'][0], limits['y'][1])
    ax.set_zlim(limits['z'][0], limits['z'][1])

    ax.set_zticks(np.arange(limits['z'][0], limits['z'][1], 0.05), minor=True)
        
    # -------------------------------------------------------------------------------------------------------

    for i in range(0, len(xs)):
        
        x = xs[i]
        y = ys[i]
        z = zs[i]
        t = ts[i]

        color = colors[i]
        label = legend[i]

        cm = plotter.get_cmap('jet')
        cNorm = clrs.Normalize(vmin=min(z), vmax=max(z))
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)

        # Avoidance events evolution by LearningRate variation
        ax.scatter(
            x, y, z,
            label=label,
            # color=color,
            # s=1.0,
            depthshade = False,
            c=scalarMap.to_rgba(z),

        )

        for _x, _y, _z, _c in zip(x, y, z, t):
            if (_z > zfilter):
                ax.text(_x, _y, _z, info(_x, _y, _z, _c), fontsize='x-small')

    # ---------------------------------------------------------------------------------------------
    
    
    ax.legend(loc='best', fontsize='x-small')

    return fig

def plot2d(xs:list, ys:list, ts:list, 
    ids:list = [],
    legend = ['avoidance events'], 
    colors = ['green'],
    labels = {'x':'(LR, FR, CT)', 'y':'% Avoided Collisions'},
    limits = {'x':[0.0, 1.1],'y':[0.0, 1.05]},
    yfilter = 0.9,
    info = tuple_label):

    fig = plotter.figure()
    
    ax = fig.add_subplot(1,1,1)
    
    ax.set_xlabel(labels['x'])
    ax.set_ylabel(labels['y'])

    ax.set_xlim(limits['x'][0], limits['x'][1])
    ax.set_ylim(limits['y'][0], limits['y'][1])

    ax.set_yticks(np.arange(limits['y'][0], limits['y'][1], 0.1))
    
    ax.minorticks_on()

    # -------------------------------------------------------------------------------------------------------
    
    for i in range(0, len(xs)):
        
        x = xs[i]
        y = ys[i]
        t = ts[i]
        idx = ids[i] if (len(ids) >= len(xs)) and len(ids[i]) == len(x) else [i for i in range(0, len(x))]

        color = colors[i]
        label = legend[i]
    
        ax.plot(
            x, y,
            # label=label,
            color=color,
            linewidth= 0.5
        )
        
        nextc = 0
        offxy = [[-0.015, 0.005],[0.005, 0.005]]
        nexto = 0

        for _id, _x, _y, _c in zip(idx, x, y, t):
            if (_y > yfilter):
                
                ax.scatter(
                    _x, _y,
                    color=__colors[nextc],
                    s=1.0,
                    label=f'{int(_id)}: {info(0.0,0.0,0.0,_c)}'
                )

                ax.annotate(
                    f'{int(_id)}', 
                    xy=(_x, _y),
                    xytext=(_x + offxy[nexto][0], _y + offxy[nexto][1]),
                    fontsize='x-small',
                    color=__colors[nextc],
                    fontstyle='oblique',
                    va='top',
                    xycoords='data', 
                    textcoords='data'
                )

                nexto = 1 if nexto == 0 else 0

            else:
                ax.scatter(
                    _x, _y,
                    color=__colors[nextc],
                    s=0.75
                )
            
            nextc = (nextc + 1) % len(__colors)

    ax.grid(linestyle="--", which= 'major', color='lightgray')
    ax.grid(linestyle=":", which= 'minor', color='lightgray')
    ax.legend(loc='best', fontsize='x-small')

    # ---------------------------------------------------------------------------------------------
    
    return fig