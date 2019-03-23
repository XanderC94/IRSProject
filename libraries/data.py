import math, json, sys
from pathlib import Path
import pandas as panda
import columns as cols

def eventMatcher(x) -> str:

    _stub = (x['collision'], x['activation'])

    if _stub == (False, False):
        return "Going By"
    elif _stub == (False, True):
        return "Avoidance"
    elif _stub == (True, True):
        return "Collision"
    else:
        return "Error"

def extractData(path: Path, save = False) -> (Path or None, panda.DataFrame):

    data = {}

    with open(path) as dataFile:
        data = json.load(dataFile)
    
    model = data['model']

    seq = 0
    act = False
    coll = False

    for e in data['log']:
        if act != e['activation'] or coll != e['collision']:
            seq += 1
            act = e['activation']
            coll = e['collision']

        e['nEvent'] = seq

    df = panda.DataFrame(data['log']).rename(columns = {'step_number':'nStep'})

    # NOTE #3:
    # Since many robots that run circularly on themselves have higher chances 
    # during the test phase to achieve great avoidances score 
    # and very low collision scores 
    # there is the need of a mean to sieze such behaviour.
    #
    # The main idea here is that those robots with circular behavior
    # explore less the area, moving around in the same area.
    # Since they move over and over the same positions,
    # the variances and stddev of such values should be lower
    # than the one of the robots with a more 'audace' behaviour.
    #
    # In order to maximize such value and don't be swayed away by negative coordinates
    # every position is translated by a vector of magnidute || max(abs(x)), max(abs(z)) ||

    df['xc'] = df['position'].apply(lambda p: p['X'])
    df['zc'] = df['position'].apply(lambda p: p['Z'])

    maxx = df['xc'].abs().max()
    maxz = df['zc'].abs().max()

    df['xc'] += maxx
    df['zc'] += maxz
    
    df.drop(['position'], axis=1)

    route = df[['xc', 'zc']]

    dx = route['xc'].std(axis=0)
    dz = route['zc'].std(axis=0)
    
    # NOTE #1: 
    # Can we say that continous activations may refere to a single obstacle avoidance/collision?
    # Interval discern avoidance of a new obstacle.

    # Compressed data frame
    cdf = (
        df[['collision', 'activation', 'nStep', 'nEvent']]
            .groupby(['nEvent', 'collision', 'activation'], as_index = False).count()
    )

    # NOTE #2:
    # Groups data by evidencing the following events
    # Collision | Activation -> Event
    # False     | True       -> Obstacle Avoided
    # False     | False      -> Going By # Uninteresting
    # True      | True       -> Collision
    # True      | False      -> Should Never Happen, else we got Design flaws or train flaws
    stats = (
        cdf.groupby(['collision', 'activation'], as_index = False)
        .agg({'nEvent':'count',  'nStep':'sum'})
        .rename(columns = {'nEvent':'nEvents', 'nStep':'nSteps'})
    )
    
    stats[cols.EVENT] = stats[['collision', 'activation']].apply(lambda x: eventMatcher(x), axis = 1)

    stats[cols.VERSION] = model['version']
    stats[cols.MODE] = data['mode']

    # Reodering columns
    stats = stats[[cols.VERSION, cols.MODE, cols.EVENT, cols.ACTIVATION, cols.COLLISION, cols.N_STEPS, cols.N_EVENTS]]
    
    # Data statistics:
    
    # mEventSteps = mean number of steps for each related event.
    # This value display, in the case of collisions and avoidances, 
    # the mean number of steps necessary for the robot to 
    # either end a collision (after colliding) or avoid an obstacle
    stats[cols.MEAN_EVENT_STEPS] = stats[cols.N_STEPS] / stats[cols.N_EVENTS]
    
    # # %OverallSteps = % of steps related to the total number of steps done
    # # This value greatly depends -- indirectly -- on the composition (difficulty and variance) of the environment
    # # Since considere ALL the steps and not only the significative ones (Collisions and Avoidances)
    # stats['%OverallSteps'] = stats['nSteps'] / stats['nSteps'].sum()
    
    # %Steps = % of steps related to the number of positive activations of the neurons in the collision layer 
    # This value exteem the goodness of the learning in relation to the number of SINGLE activations 
    # that is either if they are related to the same obstacle
    stats[cols.P_STEPS] = stats[stats[cols.ACTIVATION] == True][cols.N_STEPS] / stats[cols.N_STEPS][stats[cols.ACTIVATION] == True].sum()
    stats.loc[stats[cols.ACTIVATION] == False, [cols.P_STEPS]] = (
        stats[stats[cols.ACTIVATION] == False][cols.N_STEPS] / stats[stats[cols.ACTIVATION] == False][cols.N_STEPS].sum()
    )
    
    # # %OverallEvents = % of events {'Collision', 'Avoidance', 'Going By'} related to the total number of events
    # # This Value as well depends -- indirectly -- on the composition (difficulty and variance) of the environment
    # # Since considere ALL the events and not only the significative ones (Collisions and Avoidances)
    # stats['%OverallEvents'] = stats['nEvents'] / stats['nEvents'].sum()
    
    # %Events = % of events related to the number of positive activations of the neurons in the collision layer 
    # This value exteem the goodness of the learning in relation to the number of (grouped) SEQUENTIAL (see NOTE #1) activations 
    # that is, sequential activation are seen as single events related to a collision or avoidance of a single obstacle
    stats[cols.P_EVENTS] = stats[stats[cols.ACTIVATION] == True][cols.N_EVENTS] / stats[stats[cols.ACTIVATION] == True][cols.N_EVENTS].sum()
    stats.loc[stats[cols.ACTIVATION] == False, [cols.P_EVENTS]] = (
        stats[cols.N_EVENTS][stats[cols.ACTIVATION] == False] / stats[cols.N_EVENTS][stats[cols.ACTIVATION] == False].sum()
    )
    
    # Dipping some useful data
    stats[cols.STDX] = dx
    stats[cols.STDZ] = dz
    stats[cols.MAXX] = maxx
    stats[cols.MAXZ] = maxz

    stats[cols.LR] = model['parameters']['learningRate']
    stats[cols.FR] = model['parameters']['forgetRate']
    stats[cols.CT] = model['parameters']['collisionThreshold']
    stats[cols.RT] = model['parameters']['reverseThreshold']
    stats[cols.MT] = model['parameters']['motorThreshold']

    stats[cols.ORIGIN] = path.name
    
    print(f'Completed: {path.name}')
    
    savePath = None

    if save:
        if not (path.parent / 'csv').is_dir():
            (path.parent / 'csv').mkdir()

        savePath = (path.parent / 'csv' / path.name).with_suffix('.csv')
  
        stats.to_csv(savePath, index = False)

        print(f'Saved to: {savePath}')

    # print(stats)

    return (savePath, stats)

# ---------------------------------------------------------------------------------------------------------
if __name__== "__main__" and len(sys.argv) > 1:

    dataPath = Path(sys.argv[1])
   
    if dataPath.is_file() and dataPath.suffix == '.json':
        extractData(dataPath, save=True)

    elif dataPath.is_dir():

        for f in dataPath.iterdir():
            if f.is_file() and f.suffix == '.json':
                extractData(f, save=True)