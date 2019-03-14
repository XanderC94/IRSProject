import unittest
from libs.annutils import *
from libs.netversions.version3 import *
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
        hf = lambda i, plOut, wij: weightedSum(wij, plOut)
        connectivities = sparselyConnected([0], [[0, 2]], gen = lambda:1.0)
        result = sparseInputComposition([], o, connectivities, hf)
        self.assertEqual(result, [2.0])

    def test_saveAndLoadTrainedModel(self):
        parameters = NetParameters(0.65, 0.08, 0.8, 1, 2)
        
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
        model_name = saveTrainedModel(test_model, f"{test_model.version_name}.json")
        loaded_model = loadTrainedModel(f"{test_model.version_name}.json")
        print(f"LOADED MODEL: {str(loaded_model)}")        
        self.assertEqual(str(loaded_model), str(test_model))



if __name__ == '__main__':
    unittest.main()