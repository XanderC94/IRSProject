import unittest
from libs.annutils import *
from libs.neuralnetstructure import *


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
        hf = lambda i, plOut, wij: ann.weightedSum(wij, plOut)
        self.assertEqual(2.0, inputComposition([], [1,1], [1.0, 1.0], hf))

    def test_sparselyConnected(self):       
        connectivities = sparselyConnected([0], [[1, 2]], gen = lambda:1.0)
        self.assertEqual({0: {1: 1.0, 2: 1.0}}, connectivities)
    
    def test_sparseInputComposition_for_reverse(self):
        o = [1,0,1]
        hf = compositionFunction[2]
        connectivities = sparselyConnected([0], [[0, 2]], gen = lambda:1.0)
        result = sparseInputComposition([], o, connectivities, hf)
        self.assertEqual(result, [2.0])


if __name__ == '__main__':
    unittest.main()