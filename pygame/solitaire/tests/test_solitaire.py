import unittest

from solitaire.model import Solitaire
from solitaire.model import make_deck

class TestSolitaire(unittest.TestCase):

    def setUp(self):
        self.game = Solitaire()
        self.cards = make_deck()
        self.game.setup(self.cards)

    def test_draw_from_stock(self):
        # stock aka hand
        # stock top cards goes to waste pile, facing up
        top_card = self.game.piles['stock'].cards[-1]
        self.game.draw('stock')
        self.assertEqual(top_card, self.game.piles['waste'].cards[-1])
        self.assertTrue(top_card.facing)
