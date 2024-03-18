import abc
import argparse
import random
import unittest

from collections import Counter
from enum import Enum
from enum import auto
from itertools import chain
from itertools import combinations
from itertools import groupby
from itertools import permutations
from itertools import starmap
from operator import itemgetter

class TestRoll(unittest.TestCase):

    def test_is_yahtzee(self):
        self.assertTrue(is_yahtzee([1]*5))
        self.assertTrue(is_yahtzee([2]*5))
        self.assertTrue(is_yahtzee([3]*5))
        self.assertTrue(is_yahtzee([4]*5))
        self.assertTrue(is_yahtzee([5]*5))
        self.assertTrue(is_yahtzee([6]*5))

    def test_is_not_yahtzee(self):
        self.assertFalse(is_yahtzee([1]*4 + [2]))
        self.assertFalse(is_yahtzee([]))
        self.assertFalse(is_yahtzee([1]*3))
        self.assertFalse(is_yahtzee([1]*6))

    def test_is_large_straight(self):
        self.assertTrue(is_large_straight(list(range(1,6))))
        self.assertTrue(is_large_straight(list(range(2,7))))

    def test_is_not_large_straight(self):
        self.assertFalse(is_large_straight([]))
        self.assertFalse(is_large_straight([1,2,4,5,6]))

    def test_is_small_straight(self):
        self.assertTrue(is_small_straight(list(range(1,5))))
        self.assertTrue(is_small_straight(list(range(2,6))))
        self.assertTrue(is_small_straight(list(range(3,7))))

    def test_is_not_small_straight(self):
        self.assertFalse(is_small_straight([]))
        self.assertFalse(is_small_straight([1,4,5,6]))

    def test_is_full_house(self):
        self.assertTrue(is_full_house([1,2,1,2,2]))
        self.assertTrue(is_full_house([5,1,1,1,5]))

    def test_is_not_full_house(self):
        self.assertFalse(is_full_house([]))
        self.assertFalse(is_full_house([1,2,3,4,5]))

    def test_is_four_of_a_kind(self):
        self.assertTrue(is_four_of_a_kind([1]*4))
        self.assertTrue(is_four_of_a_kind([5]*4))

    # NOTES
    # - not bothering with the remaining is_* test functions

    def check_generate_scores(self, dice, expect):
        scores = set(generate_scores(dice))
        self.assertSetEqual(scores, expect)

    def test_generate_scores_total_of_kind(self):
        dice = [1]
        expect = set([
            (Scores.TOTAL_OF, (1,)),
        ])
        self.check_generate_scores(dice, expect)

        dice = [1,1,1]
        expect = set([
            (Scores.THREE_OF_A_KIND, (1,1,1)),
            (Scores.TOTAL_OF, (1,1,1)),
        ])
        self.check_generate_scores(dice, expect)

    def test_generate_scores_full_house(self):
        dice = [1,1,2,2,2]
        expect = set([
            (Scores.FULL_HOUSE, (1,1,2,2,2)),
            (Scores.THREE_OF_A_KIND, (2,2,2,)),
            (Scores.TOTAL_OF, (1,1,)),
            (Scores.TOTAL_OF, (2,2,2,)),
        ])
        self.check_generate_scores(dice, expect)

    def test_generate_scores_yahtzee(self):
        dice = [2,2,2,2,2]
        expect = set([
            (Scores.YAHTZEE, (2, 2, 2, 2, 2)),
            (Scores.TOTAL_OF, (2, 2, 2, 2, 2)),
        ])
        self.check_generate_scores(dice, expect)

    def test_generate_scores_small_straight(self):
        dice = (1,5,3,4,6)
        expect = set([
            (Scores.SMALL_STRAIGHT, (5,3,4,6)),
            (Scores.TOTAL_OF, (1,)),
            (Scores.TOTAL_OF, (5,)),
            (Scores.TOTAL_OF, (3,)),
            (Scores.TOTAL_OF, (4,)),
            (Scores.TOTAL_OF, (6,)),
        ])
        self.check_generate_scores(dice, expect)


class alleq:

    def __init__(self, value):
        self.value = value

    def __call__(self, iterable):
        return all(value == self.value for value in iterable)


class Player:

    def __init__(self, name):
        self.name = name


class UpperSection:
    # saving for calculations

    def __init__(self):
        self.total_of = []

    def base_score(self):
        return sum(
            dice_value
            for dice_role in self.total_of
            for dice_value in dice_role
        )

    def score(self):
        base = self.base_score()
        if base >= 64:
            base += 35
        return base


class LowerSection:

    def __init__(self):
        self.three_of_a_kind = []
        self.four_of_a_kind = []
        self.full_house = []
        self.small_straight = []
        self.large_straight = []
        self.yahtzee = []
        self.chances = []

    def score(self):
        of_a_kind = sum(
            dice_value
            for dice_roll in chain(self.three_of_a_kind, self.four_of_a_kind)
            for dice_value in dice_roll
        )
        full_house = sum(25 for _ in self.full_house)
        small_straight = sum(30 for _ in self.small_straight)
        large_straight = sum(40 for _ in self.small_straight)
        yahtzee = sum(50 for _ in self.yahtzee)
        total = sum([
            of_a_kind,
            full_house,
            small_straight,
            large_straight,
            yahtzee,
        ])
        return total


def role_dice():
    return random.randint(1, 6)

def role_cup(n):
    return [role_dice() for _ in range(n)]

def is_kind(dice):
    return len(set(dice)) == 1

def is_yahtzee(dice):
    """
    Five of a kind.
    """
    return len(dice) == 5 and len(set(dice)) == 1

def is_sequence(dice):
    return sorted(dice) == list(range(min(dice), max(dice)+1))

def is_large_straight(dice):
    """
    Five sequential dice.
    """
    return len(dice) == 5 and is_sequence(dice)

def is_small_straight(dice):
    """
    Four sequential dice.
    """
    return len(dice) == 4 and is_sequence(dice)

def is_full_house(dice):
    """
    Five dice with three of a kind and two of kind.
    """
    counter = Counter(dice)
    return (
        len(counter) == 2
        and
        2 in counter.values()
        and
        3 in counter.values()
    )

def is_four_of_a_kind(dice):
    """
    Four of a kind.
    """
    return len(dice) == 4 and is_kind(dice)

def is_three_of_a_kind(dice):
    """
    Three of a kind.
    """
    return len(dice) == 3 and is_kind(dice)

def is_single(dice):
    return len(dice) == 1

class Scores(Enum):
    TOTAL_OF = auto()
    THREE_OF_A_KIND = auto()
    FOUR_OF_A_KIND = auto()
    FULL_HOUSE = auto()
    SMALL_STRAIGHT = auto()
    LARGE_STRAIGHT = auto()
    YAHTZEE = auto()

    def __lt__(self, other):
        assert isinstance(other, Scores)
        return self.value < other.value

    def score_box_name(self, dice):
        if self != Scores.TOTAL_OF:
            return self.name.lower()
        else:
            pips = range(1, 7)
            names = [
                'aces',
                'twos',
                'threes',
                'fours',
                'fives',
                'sixes',
            ]
            for pip, name in zip(pips, names):
                if all(die == pip for die in dice):
                    return name


Scores.YAHTZEE.is_func = is_yahtzee
Scores.LARGE_STRAIGHT.is_func = is_large_straight
Scores.SMALL_STRAIGHT.is_func = is_small_straight
Scores.FULL_HOUSE.is_func = is_full_house
Scores.FOUR_OF_A_KIND.is_func = is_four_of_a_kind
Scores.THREE_OF_A_KIND.is_func = is_three_of_a_kind
Scores.TOTAL_OF.is_func = is_single

class Scorebox:

    def __init__(self, name, validator, value=None):
        self.name = name
        self.validator = validator
        self.value = value


class GameScorecard:
    """
    Scorecard for single game.
    """
    score_boxes = [
        # name, validator
        ('aces', alleq(1)),
        ('twos', alleq(2)),
        ('threes', alleq(3)),
        ('fours', alleq(4)),
        ('fives', alleq(5)),
        ('sixes', alleq(6)),
        ('three_of_a_kind', is_three_of_a_kind),
        ('four_of_a_kind', is_three_of_a_kind),
        ('full_house', is_full_house),
        ('small_straight', is_small_straight),
        ('large_straight', is_large_straight),
        ('yahtzee', is_yahtzee),
        ('chance', lambda dice: len(dice) == 5),
    ]

    upper_section = [
        'aces',
        'twos',
        'threes',
        'fours',
        'fives',
        'sixes',
    ]

    lower_section = [
        'three_of_a_kind',
        'four_of_a_kind',
        'full_house',
        'small_straight',
        'large_straight',
        'yahtzee',
        'chance',
    ]

    def __init__(self):
        self.score_boxes = [
            Scorebox(name, validator)
            for name, validator in GameScorecard.score_boxes
        ]

    def available_score_boxes(self):
        for scorebox in self.score_boxes:
            if scorebox.value is None:
                yield scorebox

    def score(self):
        lower_section = sum(
            score_box.value
            for name in self.lower_section
            for score_box in self.score_boxes
            if score_box.name == name
        )
        return lower_section


def with_value(data, value):
    for key, data_value in data.items():
        if data_value == value:
            yield (key, data_value)

def generate_scores(dice):
    """
    Generate all the scorable dice combinations in a dice roll.
    """
    counter = Counter(dice)
    counts = counter.values()
    if 5 in counts:
        yield (Scores.YAHTZEE, tuple(dice))

    if is_large_straight(dice):
        yield (Scores.LARGE_STRAIGHT, tuple(dice))

    for subdice in combinations(dice, 4):
        if is_small_straight(subdice):
            yield (Scores.SMALL_STRAIGHT, tuple(subdice))

    if 3 in counts and 2 in counts:
        yield (
            Scores.FULL_HOUSE,
            tuple(die for die in dice if counter[die] in (3, 2)),
        )

    for count, score in zip([4,3], [Scores.FOUR_OF_A_KIND, Scores.THREE_OF_A_KIND]):
        if count in counts:
            yield (score, tuple(die for die in dice if counter[die] == count))

    for die_value in dice:
        dies = tuple(die for die in dice if die == die_value)
        yield (Scores.TOTAL_OF, dies)

def command_dice():
    # NOTES
    # - this was inside `main`
    # - would like to have it available as a sub-command
    parser.add_argument('dice', nargs='+')
    # convert to ints and allow multiple args or one string of ints
    dice = list(map(int, (d for dice_ in args.dice for d in dice_)))

    def count_string(pip, count):
        return f'{pip}X{count}'

    sep = ', '
    for score in generate_scores(dice):
        print(score)

def run():
    players = [Player(name) for name in map(str, range(3))]
    scorecards = [GameScorecard() for _ in players]

    for game_round in range(3):
        for scorecard in scorecards:
            for turn in range(3):
                # TODO
                # - hold dice
                # - choose roll to take
                # - loop until something is filled instead of range(3)
                # - force filling zero if all fails
                cup_role = role_cup(5)
                sorted_roll = sorted(generate_scores(cup_role), key=itemgetter(0))
                available_boxes = scorecard.available_score_boxes()
                for dice_score, dice_roll in sorted_roll:
                    if dice_score.score_box_name(dice_roll) in available_boxes:
                        available_boxes.value = dice_score()
                        break
    # FIXME
    # - why aren't the scorecards filled in by now?
    for scorecard in scorecards:
        for score_box in scorecard.score_boxes:
            if score_box.value is None:
                score_box.value = 0
    winner = max(scorecards, key=lambda scorecard: scorecard.score())
    print(winner, winner.score())

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)
    run()

if __name__ == '__main__':
    main()

# https://gamerules.com/rules/yahtzee-dice-game/
# https://yahtzee-rules.com/
