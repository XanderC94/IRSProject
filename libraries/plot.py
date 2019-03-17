import matplotlib.pyplot as plotter
import math, json, sys, copy
from pathlib import Path
import pandas as panda
import numpy as np

data = {}

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

if len(sys.argv) > 1:
    dataPath = sys.argv[1]

    with open(dataPath) as dataFile:
        data = json.load(dataFile)
    
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
    
    # %overallSteps = % of steps related to the total number of steps done
    # This value greatly depends -- indirectly -- on the composition (difficulty and variance) of the environment
    # Since considere ALL the steps and not only the significative ones (Collisions and Avoidances)
    stats['%overallSteps'] = stats['nSteps'] / stats['nSteps'].sum()
    
    # %steps = % of steps related to the number of positive activations of the neurons in the collision layer 
    # This value exteem the goodness of the learning in relation to the number of SINGLE activations 
    # that is either if they are related to the same obstacle
    stats['%steps'] = stats[stats['activation'] == True]['nSteps'] / stats['nSteps'][stats['activation'] == True].sum()
    stats.loc[stats['activation'] == False, ['%steps']] = (
        stats[stats['activation'] == False]['nSteps'] / stats[stats['activation'] == False]['nSteps'].sum()
    )
    
    # %overallEvents = % of events {'Collision', 'Avoidance', 'Going By'} related to the total number of events
    # This Value as well depends -- indirectly -- on the composition (difficulty and variance) of the environment
    # Since considere ALL the events and not only the significative ones (Collisions and Avoidances)
    stats['%overallEvents'] = stats['nEvents'] / stats['nEvents'].sum()
    
    # %events = % of events related to the number of positive activations of the neurons in the collision layer 
    # This value exteem the goodness of the learning in relation to the number of (grouped) SEQUENTIAL (see NOTE #1) activations 
    # that is, sequential activation are seen as single events related to a collision or avoidance of a single obstacle
    stats['%events'] = stats[stats['activation'] == True]['nEvents'] / stats[stats['activation'] == True]['nEvents'].sum()
    stats.loc[stats['activation'] == False, ['%events']] = (
        stats['nEvents'][stats['activation'] == False] / stats['nEvents'][stats['activation'] == False].sum()
    )
    

    print(stats, end='\n\n')

    savePath = Path(dataPath).with_suffix('.csv')
    stats.sort_values(['event']).to_csv(savePath, index = False)

    print(f'saved to: {savePath}')

    # -------------------------------------------------------------------------------------------------- #

    # 
    # Data Distributions:
    # 
    # ???

    # fig, ax = plotter.subplots(1,1)
    # ax.plot(
    #     df['step_number'].values, 
    #     df['touched'].values, 
    #     label='results', 
    #     linewidth=0.5)

    # plotter.legend()
    # plotter.show()