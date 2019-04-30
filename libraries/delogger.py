import sys, json, regex, re, ast
from pathlib import Path

distances_pattern = re.compile(r"Distances:(\[.*\])")
collision_input_pattern = re.compile(r"Collision Layer Composed Input: (\[.*\])")
activations_pattern = re.compile(r"Collision Layer Output: ({.*})")

def recursiveExtractDictWithStrKey(json: dict)-> dict:
    d = {}
    for K,V in json.items():
        if isinstance(V, dict):
            d.update({str(K): recursiveExtractDictWithStrKey(V)})
        else:
            d.update({str(K): V})
    return d

def delog(filepath: Path):
    tokens = list()

    with open(filepath, mode='r') as fp:
        line = fp.readline()
        
        step = 0
        dist = None
        act = None
        cin = None

        while line:

            if dist is None:
                md = distances_pattern.match(line)
                if not (md is None):
                    dist = ast.literal_eval(md.group(1))
            elif cin is None:
                mc = collision_input_pattern.match(line)
                if not (mc is None):
                    cin = ast.literal_eval(mc.group(1))
            elif act is None:
                ma = activations_pattern.match(line)
                if not (ma is None):
                    act = ast.literal_eval(ma.group(1))
            
            if not (act is None) and not (dist is None) and not (cin is None):
                tokens.append({'step':step,'distances':dist, 'collision_input':cin, 'collision_pattern':act})
                act = None
                dist = None
                cin = None
                step+=1
            else:
                pass

            line = fp.readline()
        
    with open(filepath.with_suffix(".log.json"), mode="w") as fp:
        json.dump(tokens, fp, indent=4)


if __name__== "__main__" and len(sys.argv) > 1: 

    path = Path(sys.argv[1])

    if path.is_file() and path.suffix == '.log':
        delog(path)
        
    elif path.is_dir():

        for f in path.iterdir():
            if f.is_file() and f.suffix == '.log':
                delog(f)
    
                