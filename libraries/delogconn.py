import sys, json, regex, re, ast
from pathlib import Path

connectivity_pattern = re.compile(r"(\d*)->({.*})")

neurons = [0,1,2,5,6,7]

def delogconn(filepath: Path):
    tokens = list()

    with open(filepath, mode='r') as fp:
        line = fp.readline()
        
        step = 0
        conn = {}

        while line:

            if len(conn) < len(neurons):
                md = connectivity_pattern.match(line)
                if not (md is None):
                    k = md.group(1)
                    v = md.group(2)
                    conn.update({k:ast.literal_eval(v)})
            
            if len(conn) >= len(neurons):
                tokens.append(conn)
                conn = {}
                step+=1
            else:
                pass

            line = fp.readline()
        
    with open(filepath.with_suffix(".conn.json"), mode="w") as fp:
        json.dump(tokens, fp, indent=4)


if __name__== "__main__" and len(sys.argv) > 1: 

    path = Path(sys.argv[1])

    if path.is_file() and path.suffix == '.log':
        delogconn(path)
        
    elif path.is_dir():

        for f in path.iterdir():
            if f.is_file() and f.suffix == '.log':
                delogconn(f)
    
                