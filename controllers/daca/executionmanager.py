import sys, subprocess
from libs.argutils import Options
from libs.utils import *
from libs.parameterchangingstrategies import *


opt = Options.fromArgv(sys.argv)
print(opt)
    
controllerArgs = loadJsonFile("../../config/defaultControllerArgs.json")
modifiedControllerArgsFilePath = "../../config/controllerArgs.json"
webotArguments = [opt.webotsExecutablePath, "--mode=fast", "--batch"] 

#train mode
def runTrain():
    changer = ParametersChanger.fromList(opt.changingInfo, bounded=False)
    while changer.hasNext():
        parameter = changer.next()
        for K,V in parameter.items():
            controllerArgs['parameters'][K] = V
            print(f"Run with parameters {controllerArgs}")
            writeJsonOnFile(controllerArgs, modifiedControllerArgsFilePath)
            subprocess.run(webotArguments)


#test mode
def runTest():
    modelFiles = utils.getAllFilesIn(f"./{opt.modelPath}", "json")
    for modelPath in modelFiles:
        controllerArgs["modelPath"] = modelPath
        print(f"Test with model: {modelPath}")
        writeJsonOnFile(controllerArgs, modifiedControllerArgsFilePath)
        subprocess.call([ opt.webotsExecutablePath, webotArguments])
            

print("START TRAIN...")
runTrain()
print("END TRAIN!")
"""
print("START TEST...")
controllerArgs = loaded_json("../../config/defaultControllerArgs.json")
runTest()
print("END TEST...")
"""