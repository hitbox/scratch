import argparse
import configparser
import enum
import itertools as it
import random
import re

from collections import defaultdict
from pprint import pprint
from types import SimpleNamespace

import forms

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

    def randomize_from_obj(self, settings):
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

def inttuple(string):
    return tuple(map(int, string.split(',')))

def newshuffle(iterable):
    list_ = list(iterable)
    return random.sample(list_, len(list_))

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
    db.randomize_from_obj(game)

    indexed_places = list(enumerate(sorted(db.places), start=1))
    while True:
        taxi_form = forms.Form(
            dict(
                place = forms.SelectField(
                    name = 'place',
                    label = 'Goto',
                    choices = dict(indexed_places),
                ),
            ),
        )
        # this would be something like the response step in html
        # render the form to screen
        # collect input
        print(forms.render_form(taxi_form))
        # now like another request from browser submitting the form
        # need to process and validate input/data
        # if valid use it, if not report errors and loop for input again
        formdata = SimpleNamespace(**dict(forms.read_form(taxi_form)))
        print(formdata)
        break

if __name__ == '__main__':
    main()

# https://github.com/asweigart/gamesbyexample/blob/main/src/gamesbyexample/jaccuse.py
