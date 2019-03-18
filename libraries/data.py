import math, json, os
from pathlib import Path
import pandas as panda

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

def extractData(path: Path):

    data = {}
    model = {}

    with open(path) as dataFile:
        data = json.load(dataFile)
    
    with open(data['model']) as modelFile:
        model = json.load(modelFile)

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
    # df['yc'] += df['yc'].max()
    df['zc'] += maxz
    
    # print(f'MAX(x):{maxx}, MAX(z):{maxz}')

    df.drop(['position'], axis=1)

    route = df[['xc', 'zc']]

    dx = route['xc'].std(axis=0)
    # dy = route['yc'].std(axis=0)
    dz = route['zc'].std(axis=0)
    
    # cxz = route.cov()

    # print(f'STD(x):{dx}, STD(z):{dz}')
    # print(f'COV(x, z):{cxz}')

    # NOTE #1: 
    # Can we say that continous activations may refere to a single obstacle avoidance/collision?
    # Interval discern avoidance of a new obstacle.

    # Compressed data frame
    cdf = (
        df[['collision', 'activation', 'nStep', 'nEvent']]
            .groupby(['nEvent', 'collision', 'activation'], as_index = False).count()
    )

    # print(cdf)

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
    
    stats['event'] = stats[['collision', 'activation']].apply(lambda x: eventMatcher(x), axis = 1)
    
    # Reodering columns
    stats = stats[['event', 'collision', 'activation', 'nSteps', 'nEvents']]
    
    # Data statistics:
    
    # mEventSteps = mean number of steps for each related event.
    # This value display, in the case of collisions and avoidances, 
    # the mean number of steps necessary for the robot to 
    # either end a collision (after colliding) or avoid an obstacle
    stats['mEventSteps'] = stats['nSteps'] / stats['nEvents']
    
    # # %overallSteps = % of steps related to the total number of steps done
    # # This value greatly depends -- indirectly -- on the composition (difficulty and variance) of the environment
    # # Since considere ALL the steps and not only the significative ones (Collisions and Avoidances)
    # stats['%overallSteps'] = stats['nSteps'] / stats['nSteps'].sum()
    
    # %steps = % of steps related to the number of positive activations of the neurons in the collision layer 
    # This value exteem the goodness of the learning in relation to the number of SINGLE activations 
    # that is either if they are related to the same obstacle
    stats['%steps'] = stats[stats['activation'] == True]['nSteps'] / stats['nSteps'][stats['activation'] == True].sum()
    stats.loc[stats['activation'] == False, ['%steps']] = (
        stats[stats['activation'] == False]['nSteps'] / stats[stats['activation'] == False]['nSteps'].sum()
    )
    
    # # %overallEvents = % of events {'Collision', 'Avoidance', 'Going By'} related to the total number of events
    # # This Value as well depends -- indirectly -- on the composition (difficulty and variance) of the environment
    # # Since considere ALL the events and not only the significative ones (Collisions and Avoidances)
    # stats['%overallEvents'] = stats['nEvents'] / stats['nEvents'].sum()
    
    # %events = % of events related to the number of positive activations of the neurons in the collision layer 
    # This value exteem the goodness of the learning in relation to the number of (grouped) SEQUENTIAL (see NOTE #1) activations 
    # that is, sequential activation are seen as single events related to a collision or avoidance of a single obstacle
    stats['%events'] = stats[stats['activation'] == True]['nEvents'] / stats[stats['activation'] == True]['nEvents'].sum()
    stats.loc[stats['activation'] == False, ['%events']] = (
        stats['nEvents'][stats['activation'] == False] / stats['nEvents'][stats['activation'] == False].sum()
    )
    
    # Dipping some useful data

    stats['std(x)'] = dx
    stats['std(z)'] = dz
    stats['max(x)'] = maxx
    stats['max(z)'] = maxz

    stats['LR'] = model['parameters']['learning_rate']
    stats['FR'] = model['parameters']['forget_rate']
    stats['CT'] = model['parameters']['collision_threshold']
    stats['RT'] = model['parameters']['reverse_threshold']
    stats['MT'] = model['parameters']['motor_threshold']

    stats['origin'] = path.name
    
    # print(stats, end='\n\n')
    
    if not (path.parent / 'csv').is_dir():
        (path.parent / 'csv').mkdir()
    
    savePath = (path.parent / 'csv' / path.name).with_suffix('.csv')

    stats.sort_values(['event']).to_csv(savePath, index = False)

    print(f'Saved to: {savePath}', end='\n\n')

    return (savePath, data['mode'], data['version'])
