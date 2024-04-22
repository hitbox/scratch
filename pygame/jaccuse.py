import argparse
import configparser
import enum
import itertools as it
import random
import re

from collections import defaultdict
from pprint import pprint

TAXI = 'TAXI'

class Jaccuse:

    def __init__(
        self,
        time_to_solve,
        entities,
        accuse_limit,
        liars_range,
        zophie_range,
    ):
        self._time_to_solve = time_to_solve
        self._entities = entities
        self.accuse_limit = accuse_limit
        self.liars_range = liars_range
        self.zophie_range = zophie_range
        self.reset()

    def reset(self):
        """
        Reset J'Accuse game for new game.
        """
        self.time_to_solve = self._time_to_solve

        self.truth = {key: list_.copy() for key, list_ in self._entities.items()}
        for list_ in self.truth.values():
            random.shuffle(list_)

        # insertion order should keep in alignment
        self.lies = {key: list_.copy() for key, list_ in self.truth.items()}
        for truth, lies in zip(self.truth.values(), self.lies.values()):
            different_shuffle(truth, lies)

        num_liars = random.randint(*self.liars_range)
        self.liars = self.truth['suspects'][:num_liars]
        self.truthfuls = self.truth['suspects'][num_liars:]

        num_zophie_sayers = random.randint(*self.zophie_range)
        self.says_zophie = random.sample(self.truth['suspects'], num_zophie_sayers)

        # who has stolen the cat, Zophie
        self.culprit = random.choice(self.truth['suspects'])
        culprit_index = self.truth['suspects'].index(self.culprit)

        self.testimony = {}
        for interviewee in self.truth['suspects']:
            self.testimony[interviewee] = {}
            is_liar = interviewee in self.liars
            if is_liar:
                source = self.lies
            else:
                source = self.truth
            for aboutkey in ['items', 'suspects']:
                otherkeys = list(set(source) - set([aboutkey]))
                # truth or falsehood for aboutkey
                for index, thing in enumerate(source[aboutkey]):
                    # randomly say either where it is or who has it
                    otherkey = random.choice(otherkeys)
                    self.testimony[interviewee][thing] = (otherkey, source[otherkey][index])
            if interviewee not in self.says_zophie:
                continue
            # gives clue, lie or truth, about Zophie
            # NOTES
            # thingkey is one of:
            #   suspects: who has Zophie
            #   items: what item Zophie is near
            #   places: where Zophie is
            thingkey = random.choice(list(source))
            # TODO
            # - avoid treating Zophie clue differently and specially
            if is_liar:
                index = random.randrange(len(source[thingkey]))
                value = source[thingkey][index]
            else:
                index = culprit_index
                value = self.truth[thingkey][index]

            self.testimony[interviewee]['zophie'] = (thingkey, value)

        pprint(self.testimony)
        self.current_location = TAXI
        self.accused = []

    @classmethod
    def from_config(cls, cp):
        """
        Jaccuse instance from config.
        """
        jaccuse_config = cp['jaccuse']
        time_to_solve = jaccuse_config.getint('time_to_solve_seconds')
        accuse_limit = jaccuse_config.getint('accuse_limit')
        liars_range = inttuple(jaccuse_config['liars_range'])
        zophie_range = inttuple(jaccuse_config['zophie_range'])

        entities = {
            key: list(cp[f'jaccuse.{key}'].values())
            for key in jaccuse_config['entities'].split()
        }

        # all lists are same length
        assert len(set(map(len, entities.values()))) == 1

        instance = cls(
            time_to_solve = time_to_solve,
            entities = entities,
            accuse_limit = accuse_limit,
            liars_range = liars_range,
            zophie_range = zophie_range,
        )
        return instance


def different_shuffle(original, x):
    """
    Shuffle list so that no items are in original position.
    """
    while original == x:
        random.shuffle(x)

def predicatize(person, item, place):
    yield ('item_place', item, place)
    yield ('person_place', person, place)
    yield ('person_item', person, item)

def inttuple(string):
    return tuple(map(int, string.split(',')))

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'config',
        nargs = '+',
    )
    parser.add_argument(
        '--seed',
        type = int,
    )
    args = parser.parse_args(argv)

    if args.seed:
        random.seed(args.seed)

    cp = configparser.ConfigParser()
    cp.read(args.config)

    jaccuse = Jaccuse.from_config(cp)

if __name__ == '__main__':
    main()

# https://github.com/asweigart/gamesbyexample/blob/main/src/gamesbyexample/jaccuse.py
