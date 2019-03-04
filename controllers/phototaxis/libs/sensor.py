class Sensor:

    def __init__(self, device, position):
        self.device = device
        self.position = position

def ids(template, n):
    names = {}
    for i in range(0, n):
        names.update({i:template.format(id = i)})
    
    return names

def sensorArray(ids, timestep, getter, pos = [0.0], enable = True): 
    ss = {}
    i = 0
    
    for k, name in ids.items():
        
        s = getter(name)
        
        if (enable) : s.enable(timestep)
        
        ss.update({k:Sensor(s, pos[i])})

        if len(pos) > i+1 : i += 1
        
    return ss