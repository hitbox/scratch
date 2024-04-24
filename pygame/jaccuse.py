import argparse
import configparser
import enum
import itertools as it
import random
import re

from collections import defaultdict
from pprint import pprint
from types import SimpleNamespace

TAXI = 'TAXI'

class Jaccuse:

    def __init__(
        self,
        time_to_solve,
        database,
        accuse_limit,
        liars_range,
        zophie_range,
    ):
        self._time_to_solve = time_to_solve
        self._database = database
        self.accuse_limit = accuse_limit
        self.liars_range = liars_range
        self.zophie_range = zophie_range
        self.reset()

    def reset(self):
        """
        Reset J'Accuse game for new game.
        """
        self.time_to_solve = self._time_to_solve

        self.truth = {key: list_.copy() for key, list_ in self._database.items()}
        for list_ in self.truth.values():
            random.shuffle(list_)

        # insertion order should keep alignment
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


def config_data(cp):
    jaccuse_config = cp['jaccuse']
    time_to_solve = jaccuse_config.getint('time_to_solve_seconds')
    accuse_limit = jaccuse_config.getint('accuse_limit')
    minliars, maxliars = inttuple(jaccuse_config['liars_range'])
    zophie_range = inttuple(jaccuse_config['zophie_range'])
    database = {
        key: list(cp[f'jaccuse.{key}'].values())
        for key in jaccuse_config['database'].split()
    }
    # all lists are same length
    assert len(set(map(len, database.values()))) == 1
    data = dict(
        time_to_solve = time_to_solve,
        database = database,
        accuse_limit = accuse_limit,
        minliars = minliars,
        maxliars = maxliars,
        zophie_range = zophie_range,
    )
    return data

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


def command_line_menu(prompt, items):
    indexes = range(len(items))
    while True:
        for index, item in enumerate(items):
            print(f'({index}) {item}')
        try:
            selected = int(input(prompt))
        except ValueError:
            print('Invalid input')
        else:
            if selected in indexes:
                return selected
            else:
                print('Invalid index')

def command_line_main(state):
    db = state.database
    # TODO
    # - start time and enforce
    # - enfore accusations limit
    state.current_location = TAXI
    while True:
        print(f'You are at {state.current_location}')
        if state.current_location == TAXI:
            # hub transport
            items = []
            for place in db.places:
                item_parts = [place]
                suspect = next(
                    _suspect for _suspect, _place in db.suspects_places
                    if _place == place
                )
                if suspect in db.known_suspects:
                    their_item = next(
                        item for _suspect, item in db.suspects_items if _suspect == suspect
                    )
                    item_parts.append(f'{suspect} with {their_item}')
                items.append(' : '.join(item_parts))
            items.append('QUIT')
            index = command_line_menu('Select place ', items)
            if items[index] == 'QUIT':
                break
            else:
                state.current_location = items[index]
        elif state.current_location in db.places:
            current_suspect = next(
                suspect for suspect, place in db.suspects_places
                if place == state.current_location
            )
            current_item = next(
                item for suspect, item in db.suspects_items
                if suspect == current_suspect
            )
            print(f'{current_suspect} is at {state.current_location} with {current_item}.')
            db.known_suspects.add(current_suspect)
            input(f'Back to {TAXI} ')
            state.current_location = TAXI

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

    config = config_data(cp)
    state = SimpleNamespace(**{
        key: SimpleNamespace(**val) if isinstance(val, dict) else val
        for key, val in config.items()
    })
    db = state.database
    # random where suspects are (truth)
    db.suspects_places = set(zip(
        random.sample(db.suspects, len(db.suspects)),
        random.sample(db.places, len(db.places)),
    ))
    # random what item suspect has (truth)
    db.suspects_items = set(zip(
        random.sample(db.suspects, len(db.suspects)),
        random.sample(db.items, len(db.items)),
    ))
    # liars and lies
    # some random number of liars
    num_liars = random.randint(state.minliars, state.maxliars)
    db.liars = set(random.sample(db.suspects, num_liars))
    # anti-truths about where suspects are and what items they have
    db.lies = set(it.product(db.suspects, db.places)).difference(db.suspects_places)
    db.lies.update(set(it.product(db.suspects, db.items)).difference(db.suspects_items))
    #
    db.known_suspects = set()

    #jaccuse = Jaccuse.from_config(cp)
    command_line_main(state)

if __name__ == '__main__':
    main()

# https://github.com/asweigart/gamesbyexample/blob/main/src/gamesbyexample/jaccuse.py
