import sys, subprocess
from libs.argutils import opt
from libs.utils import loadJsonFile, writeJsonOnFile, getAllFilesIn
from libs.parameterchangingstrategies import ParametersChanger

print(opt)
    
controllerArgs = loadJsonFile("../../config/defaultControllerArgs.json")
modifiedControllerArgsFilePath = "../../config/controllerArgs.json"
webotsBootArguments = [str(opt.webotsExecutablePath), "--mode=fast", "--batch"] 

#train mode
def runTrain():
    webotsBootArguments.append(opt.worldTrainPath) 
    controllerArgs["mode"] = "train"
    for version in opt.versionList:
        controllerArgs['version'] = version
        print(f"Train neural net version {version}")
        changer = ParametersChanger.fromList(opt.changingInfo.copy(), bounded=False)
        while changer.hasNext():
            parameter = changer.next()
            for K,V in parameter.items():
                    controllerArgs['parameters'][K] = V
            print(webotsBootArguments)
            print(f"Run with parameters {controllerArgs}")
            writeJsonOnFile(controllerArgs, modifiedControllerArgsFilePath)
            subprocess.run(webotsBootArguments)

#test mode
def runTest():
    webotsBootArguments.append(opt.worldTestPath)
    controllerArgs["mode"] = "test"   
    modelFiles = getAllFilesIn(f"./{controllerArgs['modelPath']}", "json")
    print(f"Model path {opt.modelPath}")
    for modelPath in modelFiles:
        controllerArgs["modelPath"] = str(modelPath)
        print(f"Test with model: {modelPath}")
        writeJsonOnFile(controllerArgs, modifiedControllerArgsFilePath)
        subprocess.call(webotsBootArguments)
            

if opt.executionMode == "train":
    print("START TRAIN...")
    runTrain()
    print("END TRAIN!")
elif opt.executionMode == "test":
    print("START TEST...")
    runTest()
    print("END TEST...")
else:
    print("UNKWON MODE")
