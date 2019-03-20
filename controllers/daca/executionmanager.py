import sys, subprocess
from libs.argutils import *
from libs.utils import *
from libs.parameterchangingstrategies import *


opt = Options.fromArgv(sys.argv)
controllerArgs = loaded_json("../../config/defaultControllerArgs.json")
modifiedControllerArgsFilePath = "../../config/controllerArgs.json"
webotArguments = " --mode=fast --batch"    

#train mode
def runTrain():
    changer = ParametersChanger.fromList(opt.changingInfo, bounded=False)
    while changer.hasNext():
        parameter = changer.next()
        for K in parameter.keys
            controllerArgs[k] = parameter[k]
            writeJsonOnFile(controllerArgs, modifiedControllerArgsFilePath)
            subprocess.call([ opt.webotsExecutablePath, webotArguments])


#test mode
def runTest():
    modelFiles = utils.getAllFilesIn(f"./{opt.modelPath}", "json")
    for modelPath in modelFiles
        controllerArgs["modelPath"] = modelPath
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