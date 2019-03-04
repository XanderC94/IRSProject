def parseArgs(argv):
    opt = {}
    for arg in argv:
        if (arg.startswith("--")): 
            v = arg.split("=")
            v[0] = v[0].replace("--", "")
            opt.update({v[0]:v[1]})
    return opt