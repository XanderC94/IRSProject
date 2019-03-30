_nSteps = lambda x:f'n{x}Steps'
_nEvents = lambda x:f'n{x}Events'
_mEventSteps = lambda x:f'm{x}Steps'
_pSteps = lambda x:f'%{x}Steps'
_pEvents = lambda x:f'%{x}Events'

VERSION = 'version'
MODE='mode'

EVENT='event'
COLLISION='collision'
ACTIVATION='activation'

POSITION='position'

N_STEPS=_nSteps('')
N_AVOID_STEPS=_nSteps('Avoid')
N_COLLIDE_STEPS=_nSteps('Collide')
N_ERROR_STEPS=_nSteps('Error')
N_GOINGBY_STEPS=_nSteps('GoingBy')

N_EVENTS=_nEvents('')
N_AVOID_EVENTS=_nEvents('Avoid')
N_COLLIDE_EVENTS=_nEvents('Collide')
N_ERROR_EVENTS=_nEvents('Error')

MEAN_EVENT_STEPS=_mEventSteps('')
MEAN_AVOID_STEPS=_mEventSteps('Avoid')
MEAN_COLLIDE_STEPS=_mEventSteps('Collide')
MEAN_ERROR_STEPS=_mEventSteps('Error')

P_STEPS=_pSteps('')
P_AVOID_STEPS=_pSteps('Avoid')
P_COLLIDE_STEPS=_pSteps('Collide')
P_ERROR_STEPS=_pSteps('Error')

P_EVENTS=_pEvents('')
P_AVOID_EVENTS=_pEvents('Avoid')
P_COLLIDE_EVENTS=_pEvents('Collide')
P_ERROR_EVENTS=_pEvents('Error')

STDX='std(x)'
STDZ='std(z)'
MAXX='max(x)'
MAXZ='max(z)'
LR='LR'
FR='FR'
CT='CT'
RT='RT'
MT='MT'
ORIGIN='origin'

ordered_columns = [
    VERSION,
    MODE,

    N_GOINGBY_STEPS,
    N_AVOID_STEPS,
    N_COLLIDE_STEPS,

    N_AVOID_EVENTS,
    N_COLLIDE_EVENTS,

    MEAN_AVOID_STEPS,
    MEAN_COLLIDE_STEPS,

    P_AVOID_STEPS,
    P_COLLIDE_STEPS,

    P_AVOID_EVENTS,
    P_COLLIDE_EVENTS,
    
    STDX,
    STDZ,
    # MAXX,
    # MAXZ,
    
    LR,
    FR,
    CT,
    RT,
    MT,

    ORIGIN
]

standalone_columns = [
    VERSION,
    MODE,
    STDX,
    STDZ,
    # MAXX,
    # MAXZ,
    LR,
    FR,
    CT,
    RT,
    MT,
    ORIGIN
]