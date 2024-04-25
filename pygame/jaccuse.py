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

class Database:

    def __init__(self, suspects, items, places):
        self.suspects = suspects
        self.items = items
        self.places = places
        self.suspects_places = set()
        self.suspects_items = set()
        self.known_suspects = set()
        self.culprit = None

    def tables(self):
        yield ('suspects', self.suspects)
        yield ('items', self.items)
        yield ('places', self.places)
        yield ('suspects_places', self.suspects_places)
        yield ('suspects_items', self.suspects_items)
        yield ('known_suspects', self.known_suspects)
        yield ('culprit', self.culprit)

    def reset(self):
        self.suspects_places.clear()
        self.suspects_items.clear()
        self.known_suspects.clear()

    def random_suspects_places(self):
        return zip(newshuffle(self.suspects), newshuffle(self.places))

    def random_suspects_items(self):
        return zip(newshuffle(self.suspects), newshuffle(self.items))

    def randomize(self, num_liars, num_zophie):
        """
        :param num_liars: number of liars to generate.
        :param num_zophie: numer of suspects to give clues about Zophie.
        """
        self.suspects_places.update(self.random_suspects_places())
        self.suspects_items.update(self.random_suspects_items())
        self.culprit = random.choice(list(self.suspects))

    def randomize_from_settings(self, settings):
        num_liars = random.randint(settings.minliars, settings.maxliars)
        num_zophie = random.randint(settings.minzophie, settings.maxzophie)
        self.randomize(num_liars, num_zophie)

    def suspect_place(self, suspect):
        """
        Where a suspect is.
        """
        for _suspect, place in self.suspects_places:
            if _suspect == suspect:
                return place

    def suspect_item(self, suspect):
        """
        Item that suspect has.
        """
        for _suspect, item in self.suspects_items:
            if _suspect == suspect:
                return item


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


class StringWidget:

    def __call__(self, field, **kwargs):
        return str(field)


class Field:

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self

    def render(self, **kwargs):
        return self.widget(self, **kwargs)


class SelectField(Field):

    widget = StringWidget()


class CommandField(Field):

    widget = StringWidget()


class Form:

    @classmethod
    def _unbound_fields(cls):
        for name in dir(cls):
            attr = getattr(cls, name)
            if isinstance(attr, Field):
                yield (name, attr)

    @classmethod
    def from_data(cls, data):
        form = cls()
        form._fields = []
        fields = dict(cls._unbound_fields())
        for key, val in data.items():
            if key in fields:
                field = fields[key]
                setattr(form, key, field)
                form._fields.append(field)
                del fields[key]
        for name, field in fields.items():
            setattr(form, name, field)
            form._fields.append(field)
        return form

    def __iter__(self):
        yield from self._fields


class TaxiForm(Form):
    """
    WIP: Form for selecting place to go or...
    """

    places = SelectField()
    quit_ = CommandField()


def config_data(cp):
    jaccuse_config = cp['jaccuse']
    time_to_solve = jaccuse_config.getint('time_to_solve_seconds')
    accuse_limit = jaccuse_config.getint('accuse_limit')
    minliars, maxliars = inttuple(jaccuse_config['liars_range'])
    minzophie, maxzophie = inttuple(jaccuse_config['zophie_range'])
    yield ('time_to_solve', time_to_solve)
    yield ('accuse_limit', accuse_limit)
    yield ('minliars', minliars)
    yield ('maxliars', maxliars)
    yield ('minzophie', minzophie)
    yield ('maxzophie', maxzophie)

def tables_from_config(cp):
    for tablename in cp['jaccuse']['tables'].split():
        section = cp[f'jaccuse.{tablename}']
        rows = section.values()
        yield (tablename, rows)

def database_from_config(cp):
    tables = defaultdict(set)
    for tablename, rows in tables_from_config(cp):
        tables[tablename].update(rows)
    return Database(**tables)

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

def newshuffle(iterable):
    list_ = list(iterable)
    return random.sample(list_, len(list_))

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

def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'config',
        nargs = '+',
    )
    parser.add_argument(
        '--seed',
        type = int,
    )
    return parser

def main(argv=None):
    parser = argument_parser()
    args = parser.parse_args(argv)

    if args.seed:
        random.seed(args.seed)

    cp = configparser.ConfigParser()
    cp.read(args.config)

    game = SimpleNamespace(**dict(config_data(cp)))
    db = database_from_config(cp)
    db.randomize_from_settings(game)

    taxi_form = TaxiForm.from_data(dict(db.tables()))
    for field in taxi_form:
        print(field)

if __name__ == '__main__':
    main()

# https://github.com/asweigart/gamesbyexample/blob/main/src/gamesbyexample/jaccuse.py
