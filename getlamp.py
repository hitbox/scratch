import abc
import argparse
import cmd
import csv
import inspect
import pickle
import string

from collections import UserList
from operator import attrgetter

class Entity:

    def __init__(self, id, description):
        self.id = id
        self.description = description

    @classmethod
    def from_data(cls, data):
        return cls(id=data['id'], description=data['description'])


class Location(Entity):
    pass


class Object(Entity):
    pass


class Portal:
    """
    A path between two locations.
    """

    def __init__(self, a, b):
        self.a = a
        self.b = b

    @classmethod
    def from_data(cls, data):
        return cls(a=data['a'], b=data['b'])


class ThingList(abc.ABC, UserList):

    @property
    @abc.abstractmethod
    def for_class(self):
        """
        The class to create instances of.
        """

    def load_csv(self, filename):
        with open(filename, newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            for data in reader:
                instance = self.for_class.from_data(data)
                self.append(instance)


class ObjectList(ThingList):
    for_class = Object


class LocationList(ThingList):
    for_class = Location


class PortalList(ThingList):
    for_class = Portal


class Game:

    def __init__(self):
        self.here = None
        self.locations = LocationList()
        self.objects = ObjectList()

    def location_by_id(self, id_):
        for location in self.locations:
            if location.id == id_:
                return location


class EditShell(cmd.Cmd):
    intro = 'Game shell. Type help or ? to list commands.\n'
    _error_prefix = '*** '
    _dirty = 0
    _dirty_prompt = 3

    def __init__(self, game, completekey='tab', stdin=None, stdout=None):
        super().__init__(completekey, stdin, stdout)
        self._game = game

    def _confirm(self, prompt, default=''):
        answer = input(prompt)
        if answer == '':
            answer = default
        return answer.lower().startswith('y')

    def _prompt_truthy(
        self,
        prompt,
        invalid = 'invalid input',
        cancel = '',
    ):
        while True:
            answer = input(prompt)
            if answer == cancel:
                return
            elif answer:
                return answer
            self._write_error(invalid)

    def _write_error(self, message):
        self.stdout.write(f'{self._error_prefix}{message}\n')

    def _write_message(self, message):
        self.stdout.write(f'{message}\n')

    def _no_args(self, arg):
        if arg:
            self._write_error('function takes no arguments')

    def _set_clean(self):
        self._dirty = 0

    def _dirtier(self):
        self._dirty += 1
        # TODO
        # - a dirty threshold to automatically prompt to save
        # - current filename default

    @property
    def prompt(self):
        parts = ['edit']
        if self._dirty >= self._dirty_prompt:
            parts.append('dirty')
        return f'({" ".join(parts)}) '

    def do_quit(self, arg):
        """
        Quit
        """
        self._no_args(arg)
        if not self._dirty:
            return True
        prompt = 'Unsaved changes. Are you sure? '
        return self._confirm(prompt, default='y')

    def do_save(self, arg):
        """
        Save to file.
        """
        if not arg:
            self._write_error('invalid filename')
            return
        with open(arg, 'wb') as save_file:
            pickle.dump(self._game, save_file)
        self._set_clean()

    def do_load(self, arg):
        """
        Load from file.
        """
        if not arg:
            self._write_error('invalid filename')
            return
        self._game = Game()
        with open(arg, 'rb') as load_file:
            self._game.__dict__.update(pickle.load(load_file).__dict__)
        self._set_clean()

    def do_here(self, arg):
        """
        Show current location or create.
        """
        if arg:
            location = self._game.location_by_id(arg)
            if location is None:
                self._write_error('location not found')
                return
            self._game.here = location
        if self._game.here is not None:
            self.stdout.write(f'{self._game.here}')
        else:
            self._write_error('*** no current location')
            prompt = 'create a new location? '
            if self._confirm(prompt):
                self.do_create_location(arg)

    def _list_by_id(self, attr):
        self.columnize(list(map(attrgetter('id'), attr)))

    def do_list_locations(self, arg):
        """
        List locations
        """
        self._no_args(arg)
        self._list_by_id(self._game.locations)

    def do_list_objects(self, arg):
        """
        List objects
        """
        self._no_args(arg)
        self._list_by_id(self._game.objects)

    def _create(self, arg):
        if arg:
            try:
                id_, _, description = arg.partition(' ')
            except ValueError:
                self._write_error('invalid args')
        else:
            self.stdout.write('New location\n')
            id_ = self._prompt_truthy('id> ')
            if id_ is None:
                return
            description = self._prompt_truthy('description> ')
            if description is None:
                return
        return (id_, description)

    def do_create_location(self, arg):
        """
        Create location and set current location if None.
        """
        result = self._create(arg)
        if result is None:
            return
        id_, description = result
        location = Location(id=id_, description=description)
        self._game.locations.append(location)
        self._dirtier()

    def do_describe_location(self, arg):
        """
        Show location description.
        """
        location = self._game.location_by_id(arg)
        if location is None:
            self._write_error('location not found')
            return
        self._write_message(location.description)


def lengths(iterable):
    return map(len, iterable)

def menu(choices):
    items = list(zip(string.ascii_lowercase, choices))
    column_lengths = map(lengths, zip(*items))
    return items

def choose(prompt, choices, invalid='Invalid'):
    while True:
        answer = input(prompt)
        if answer in choices:
            return answer
        print(invalid)

def load(filename, class_):
    with open(filename, newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        for data in reader:
            instance = class_.from_data(data)
            yield instance

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?')
    args = parser.parse_args(argv)

    game = Game()
    editshell = EditShell(game)
    if args.file:
        editshell.do_load(args.file)
    editshell.cmdloop()
    # TODO
    # - help_* attributes for cleaner help strings
    # - automatically create editor from class and attributes

if __name__ == '__main__':
    main()
