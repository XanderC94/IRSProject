import unittest
from libs.annutils import *
from libs.netversions.version3 import *
from libs.learningparameters import *
from libs.parameterchangingstrategies import *
from libs.utils import *


class TestStringMethods(unittest.TestCase):

    def test_mapToSensorsOutput(self):
        sensors = [0.0,1.1,2.2,3.3,4.4,5.5,6.6,7.7]
        sensorsConnections = sparselyConnected(range(0, 3), [[0, 1, 2], [3, 4], [5, 6, 7]], gen = lambda:1.0)
        bumperOutputByConnection = mapToSensorsOutput(sensors, sensorsConnections)
        self.assertEqual(bumperOutputByConnection, [[0.0, 1.1, 2.2], [3.3, 4.4], [5.5, 6.6, 7.7]])

    def test_logicSum(self):
        result = logicSum([1,0])
        self.assertEqual(result, 1)
        result = logicSum([0,1])
        self.assertEqual(result, 1)
        result = logicSum([1,1])
        self.assertEqual(result, 1)
        result = logicSum([0,0])
        self.assertEqual(result, 0)

    def test_inputComposition(self):
        hf = lambda i, plOut, wij: weightedSum(wij, plOut)
        self.assertEqual(2.0, inputComposition([], [1,1], [1.0, 1.0], hf))

    def test_sparselyConnected(self):       
        connectivities = sparselyConnected([0], [[1, 2]], gen = lambda:1.0)
        self.assertEqual({0: {1: 1.0, 2: 1.0}}, connectivities)
    
    def test_sparseInputComposition_for_reverse(self):
        o = [1,0,1]
        hf = lambda sIn, plOut, w: weightedSum(w, plOut)
        connectivities = sparselyConnected([0], [[0, 2]], gen = lambda:1.0)
        result = sparseLayerInputComposition([], o, connectivities, hf)
        self.assertEqual(result, [2.0])
        

    def test_saveAndLoadTrainedModel(self):
        parameters = LearningParameters(0.65, 0.08, 0.8, 1, 2)
        
        nCollisionNodes = 3
        nMotors = 2
        nDistanceSensors = 8
        bumpersConnections = sparselyConnected(range(0, nCollisionNodes), [[5, 6, 7], [3, 4], [0, 1, 2]], gen = lambda:1.0)

        proximityToCollisionConnections = matrix(nCollisionNodes, nDistanceSensors)
        collisionToReverseConnections = sparselyConnected([0], [[0, 2]], gen = lambda:1.0)
        collisionToMotorConnections = sparselyConnected(range(0, nMotors), [[0], [2]], gen = lambda:1.0)
        connectivities = {
            1: proximityToCollisionConnections, # Collision <- Proximity ==> FULLY CONNECTED
            2: collisionToReverseConnections,  # Reverse Command <- Collision, not fully connected 
            3: collisionToMotorConnections # Motor Command <- Collision, not fully connected 
        }

        test_model = TrainedModel("TestExample", parameters, connectivities)
        print(f"TEST MODEL: {str(test_model)}")
        directory = "./../../model/modelforunittests/"
        writeModelOnFile(test_model, f"{directory}{test_model.version}.json")
        loaded_model = loadTrainedModel(f"{directory}{test_model.version}.json")
        print(f"LOADED MODEL: {str(loaded_model)}")        
        self.assertEqual(str(loaded_model), str(test_model))

    def test_setParameter(self):
        parameters = LearningParameters(5.0, 6.0, 7.0, 8.0, 9.0)
        value = 1.0
        parameters.setParameter("collisionThreshold", value)
        self.assertEqual(value, parameters.collisionThreshold)

        value = 2.0
        parameters.setParameter("learningRate", value)
        self.assertEqual(value, parameters.learningRate)

        value = 3.0
        parameters.setParameter("forgetRate", value)
        self.assertEqual(value, parameters.forgetRate)

        value = 4.0
        parameters.setParameter("motorThreshold", value)
        self.assertEqual(value, parameters.motorThreshold)

        value = 5.0
        parameters.setParameter("reverseThreshold", value)
        self.assertEqual(value, parameters.reverseThreshold)

    def test_parameterChanger(self):

        parameters = LearningParameters(3.0, 4.0, 5.0, 6.0, 7.0)
        minVal = 3.0
        maxVal = 4.0
        step = 0.1

        changer = ParameterChanger(parameters, "collisionThreshold", minVal, maxVal, step)

        current_val = minVal

        while not changer.hasEnded():

            current_val = min(current_val + step, maxVal).__round__(3)
            
            changer.updateParameter()

            self.assertEqual(current_val, parameters.collisionThreshold.__round__(3))
            
        self.assertEqual(maxVal, parameters.collisionThreshold)
    
    def test_changerDecorator(self):

        parameters = LearningParameters(0.05, 0.8, 0.65, 2.0, 1.0)

        info = [
            {
                "parameter": "learningRate",
                "minVal": 0.0,
                "maxVal": 0.015,
                "changeStep": 0.004
            },
            {
                "parameter": "forgetRate",
                "minVal": 0.0,
                "maxVal": 0.20,
                "changeStep": 0.05
            }
        ]

        step1, step2 = info[0]['changeStep'], info[1]['changeStep']
        max1, max2 = info[0]['maxVal'], info[1]['maxVal']
        min1, min2 = info[0]['minVal'], info[1]['minVal']
        v1, v2 = 0.0, 0.0

        # UNBOUNDED = value in [minValue, maxValue]
        print('Unbounded')
        changer = ParametersChanger.fromList(info.copy(), bounded=False)

        while changer.hasNext():
            __next = changer.next()
            changed = parameters.setParameters(__next)

            self.assertEqual(v1, parameters.learningRate)
            self.assertEqual(v2, parameters.forgetRate)

            print(__next)

            v1 = (v1 + step1).__round__(3)
            
            if v1 >= max1 + step1:
                v2 = (v2 + step2).__round__(3)
                v1 = min1
            
            v1 = min(v1, max1)
            v2 = min(v2, max2)

        self.assertEqual(max1, parameters.learningRate)
        self.assertEqual(max2, parameters.forgetRate)

        # BOUNDED => value in [minValue, maxValue)
        print('Bounded')
        changer = ParametersChanger.fromList(info.copy(), bounded=True)

        v1, v2 = 0.0, 0.0

        while changer.hasNext():
            __next = changer.next()
            changed = parameters.setParameters(__next)

            self.assertEqual(v1, parameters.learningRate)
            self.assertEqual(v2, parameters.forgetRate)

            print(__next)

            v1 = (v1 + step1).__round__(3)
            
            if v1 >= max1:
                v2 = (v2 + step2).__round__(3)
                v1 = min1
            
            v1 = min(v1, max1)
            v2 = min(v2, max2)
        
        self.assertGreater(max1, parameters.learningRate)
        self.assertGreater(max2, parameters.forgetRate)


    def test_modelChangerIterations(self):
        files = getAllFilesIn("./../../model/modelforunittests", "json")
        changer = ModelChanger.createFromFilePaths(files)
        for file in files:
            self.assertEqual(changer.next(), loadTrainedModel(file))
    
    def test_modelChangerHasNext(self):
        files = getAllFilesIn("./../../model/modelforunittests", "json")
        changer = ModelChanger.createFromFilePaths(files)
        for file in files:
            self.assertTrue(changer.hasNext())
            changer.next()
        self.assertFalse(changer.hasNext())
        
if __name__ == '__main__':
    unittest.main()