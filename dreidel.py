import argparse
import enum
import random

from itertools import count

class Dreidel(enum.Enum):

    NUN = enum.auto()
    HEY = enum.auto()
    GIMMEL = enum.auto()
    SHIN = enum.auto()


def play(players):
    player = 0
    choices = list(Dreidel)
    pot = 0
    for turns in count():
        # ante up when pot is empty
        if pot == 0:
            for player, coins in players.items():
                if coins > 0:
                    players[player] -= 1
                    pot += 1
        turn = random.choice(choices)
        if turn == Dreidel.NUN:
            # nothing happens
            pass
        elif turn == Dreidel.HEY:
            # player takes half pot
            half_pot = pot // 2
            players[player] += half_pot
            pot -= half_pot
        elif turn == Dreidel.GIMMEL:
            # players takes pot
            players[player] += pot
            pot = 0
        elif turn == Dreidel.SHIN:
            # player antes coin
            players[player] -= 1
            pot += 1
        if sum(1 for coins in players.values() if coins > 0) == 1:
            # winner!
            break
        else:
            # find next player with coins
            while True:
                player = (player + 1) % len(players)
                if players[player] > 0:
                    break
    print(turns, [player for player, coins in players.items() if coins > 0])

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--players', type=int, default='4')
    parser.add_argument('--pieces', type=int, default='10')
    args = parser.parse_args(argv)
    players = {player_index: args.pieces for player_index in range(args.players)}
    play(players)

if __name__ == '__main__':
    main()

# 2023-12-12
# - https://buttondown.email/hillelwayne/archive/i-formally-modeled-dreidel-for-no-good-reason/
# - didn't know dreidel was a game
# - make the dreidel game in Python
