import unittest

from game_of_life import evolve
from patterns import blinker

class TestEvolve(unittest.TestCase):

    def test_blinker(self):
        state = blinker()
        self.assertEqual(state, {(1,0), (1,1), (1,2)})
        state = evolve(state)
        self.assertEqual(state, {(0,1), (1,1), (2,1)})
        state = evolve(state)
        self.assertEqual(state, {(1,0), (1,1), (1,2)})
