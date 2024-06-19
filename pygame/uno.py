import abc
import argparse
import itertools as it

suits = 'RYGB'
suits_fullname = {'R': 'red', 'Y': 'yellow', 'G': 'green', 'B': 'blue'}

actions = 'SDR'
actions_fullname = {'S': 'skip', 'D': 'draw two', 'R': 'reverse'}

# Card Types
# - suit and rank, color and number
# - suit and action, color and type of action
# - wild, just wild no attributes
# - wild draw four, no attributes but different than "wild"

class BaseCard(abc.ABC):

    @abc.abstractmethod
    def play(self, game, player):
        """
        Play card in game from player.
        """


class WildCard(Base):

    def play(self, game, player):
        pass


class WildDrawFourCard(Base):

    def play(self, game, player):
        pass


class SuitCard(Base):

    @property
    @abc.abstractmethod
    def suit(self):
        pass


class DrawTwoCard(SuitCard):

    def play(self, game, player):
        pass


class ReverseCard(SuitCard):

    def play(self, game, player):
        pass


class SkipCard(SuitCard):

    def play(self, game, player):
        pass


class Card(SuitCard):

    def __init__(self, id, suit, rank):
        self.id = id
        self.suit = suit
        self.rank = rank

    def __repr__(self):
        classname = self.__class__.__name__
        suit = suits_fullname[self.suit]
        rank = self.rank
        if isinstance(rank, str):
            rank = actions_fullname[rank]
        return f'{classname}({self.id}, {suit!r}, {rank!r})'


def generate_deck():
    id = 0
    for ranks in [range(10), range(1,10)]:
        for suit, rank in it.product(suits, ranks):
            yield Card(id, suit, rank)
            id += 1

    for suit, action in it.product(suits, actions):
        for _ in range(2):
            yield Card(id, suit, action)
            id += 1

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

    deck = list(generate_deck())
    print(deck)

if __name__ == '__main__':
    main()

# 2024-06-19 Wed.
# Uno Solver
# https://two-wrongs.com/troubles-in-solving-uno.html
