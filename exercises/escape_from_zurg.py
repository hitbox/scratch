# https://web.engr.oregonstate.edu/~erwig/papers/Zurg_JFP04.pdf
# https://www.metalevel.at/zurg/zurg.pl
import argparse

from collections import namedtuple
from enum import Enum
from enum import auto
from itertools import combinations
from operator import attrgetter

PROBLEM = """\
Buzz, Woody, Rex, and Hamm have to escape from Zurg(a) They merely have to
cross one last bridge before they are free. However, the bridge is fragile and
can hold at most two of them at the same time. Moreover, to cross the bridge a
ﬂashlight is needed to avoid traps and broken parts. The problem is that our
friends have only one ﬂashlight with one battery that lasts for only 60 minutes
(this is not a typo: sixty). The toys need different times to cross the bridge
(in either direction):

TOY TIME
Buzz  5 minutes
Woody 10 minutes
Rex   20 minutes
Hamm  25 minutes

Since there can be only two toys on the bridge at the same time, they cannot
cross the bridge all at once. Since they need the ﬂashlight to cross the
bridge, whenever two have crossed the bridge, somebody has to go back and bring
the ﬂashlight to those toys on the other side that still have to cross the
bridge.

The problem now is: In which order can the four toys cross the bridge in time
(that is, in 60 minutes) to be saved from Zurg?

(a) These are characters from the animation movie “Toy Story 2”."""

Toy = namedtuple('Toy', 'name time')

class MoveType(Enum):
    LEFT = auto()
    RIGHT = auto()


class State(
    namedtuple('_State', ('left', 'right', 'moves', 'time_limit'))
):
    """
    A state of toys on the right or left or the bridge and accumulated moves.
    """

    def move_func(self, move):
        assert move in MoveType
        if move == MoveType.LEFT:
            return self.move_left
        else:
            return self.move_right

    def move_right(self, move_toys):
        new_state = self.__class__(
            left = [toy for toy in self.left if toy not in move_toys],
            right = self.right + list(move_toys),
            moves = self.moves + [(move_toys, MoveType.RIGHT)],
            time_limit = self.time_limit,
        )
        return new_state

    def move_left(self, move_toys):
        new_state = self.__class__(
            left = self.left + list(move_toys),
            right = [toy for toy in self.right if toy not in move_toys],
            moves = self.moves + [(move_toys, MoveType.LEFT)],
            time_limit = self.time_limit,
        )
        return new_state

    def total_time(self):
        return sum(
            max(toy.time for toy in move_toys)
            for move_toys, _ in self.moves
        )

    def is_solved(self):
        return not self.left and self.total_time() <= self.time_limit

    def move_strings(self):
        running_total = 0
        for move_toys, move_type in self.moves:
            who = ' and '.join( toy.name for toy in move_toys)
            move_time = max(toy.time for toy in move_toys)
            running_total += move_time
            line = f'{who} {move_type} in {move_time}'
            if running_total != move_time:
                line += f', for {running_total}'
            yield line


def solve_escape_zurg(options):
    """
    Find solutions to Escape from Zurg.
    """
    state = State(
        left = [
            Toy('buzz', 5),
            Toy('woody', 10),
            Toy('rex', 20),
            Toy('hamm', 25),
        ],
        right = [],
        moves = [],
        time_limit = 60,
    )
    for state in solve(state, MoveType.RIGHT):
        print('\n'.join(state.move_strings()))
        print()

def solve(state, move):
    """
    Recursively alternate between right and left moves searching valid moves
    for a solution.
    """
    assert move in MoveType

    if state.is_solved():
        # solved state
        yield state

    move_func = state.move_func(move)
    if move == MoveType.RIGHT:
        move_gen = combinations(state.left, 2)
        new_move = MoveType.LEFT
    else:
        move_gen = combinations(state.right, 1)
        new_move = MoveType.RIGHT

    for move_toys in move_gen:
        move_time = max(toy.time for toy in move_toys)
        new_time = state.total_time() + move_time
        if new_time <= state.time_limit:
            new_state = move_func(move_toys)
            yield from solve(new_state, new_move)

def print_problem(options):
    print(PROBLEM)

def parse_command_line(argv=None):
    parser = argparse.ArgumentParser(
        description = 'Escape from Zurg',
    )
    subparsers = parser.add_subparsers(required=True)
    show = subparsers.add_parser(
        'show',
        help = 'Print the problem text.',
    )
    show.set_defaults(func=print_problem)
    solve = subparsers.add_parser(
        'solve',
        help = 'Solve Escape from Zurg.',
    )
    solve.set_defaults(func=solve_escape_zurg)
    args = parser.parse_args(argv)
    return args

def main():
    args = parse_command_line()

    func = args.func
    del args.func
    func(vars(args))

if __name__ == '__main__':
    main()
