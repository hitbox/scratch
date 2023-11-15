import abc
import argparse
import cmd
import csv
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
    intro = 'Edit shell. Type help or ? to list commands.\n'
    _error_prefix = '*** '
    _dirty = 0
    _dirty_prompt = 3

    def __init__(self, data=None, completekey='tab', stdin=None, stdout=None):
        super().__init__(completekey, stdin, stdout)
        if data is None:
            data = dict()
        self.data = data
        self.path = []
        self.last_filename = None

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

    def _list_by_id(self, attr):
        """
        Columnar list of a list attribute attr.
        """
        self.columnize(list(map(attrgetter('id'), attr)))

    def _interactive_create(self, name):
        """
        Prompt for attribute values and return them.
        """
        self.stdout.write(f'New {name}\n')
        id_ = self._prompt_truthy('id> ')
        if id_ is None:
            return
        description = self._prompt_truthy('description> ')
        if description is None:
            return
        return (id_, description)

    def _create(self, name, arg):
        if arg:
            try:
                id_, _, description = arg.partition(' ')
            except ValueError:
                self._write_error('invalid args')
            else:
                return (id_, description)
        else:
            return self._interactive_create(name)

    @property
    def prompt(self):
        """
        Dynamic prompt.
        """
        parts = ['edit']
        if self.path:
            parts.append('/'.join(self.path))
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

    def do_save(self, filename):
        """
        Save to file.
        """
        if not filename:
            if not self.last_filename:
                self._write_error('invalid filename')
                return
            filename = self.last_filename
            self._write_message(filename)
        with open(filename, 'wb') as file:
            pickle.dump(self.data, file)
        self._set_clean()

    def do_load(self, filename):
        """
        Load from file.
        """
        if not filename:
            self._write_error('invalid filename')
            return
        with open(filename, 'rb') as file:
            self.data = pickle.load(file)
        self.last_filename = filename
        self._set_clean()

    def _current_data(self):
        data = self.data
        for key in self.path:
            data = data[key]
        return data

    def _complete_keys(self, line):
        cmd, args, foo = self.parseline(line)
        data = self._current_data()
        return list(key for key in data if key.startswith(args))

    def do_list(self, arg):
        """
        List current data keys.
        """
        data = self._current_data()
        self.columnize(list(data))

    def complete_list(self, text, line, begin, end):
        return self._complete_keys(line)

    def do_show(self, arg):
        """
        Show value of key.
        """
        data = self._current_data()
        if not arg:
            self._write_error('key argument required')
            return
        if arg not in data:
            self._write_error('invalid key')
            return
        values = data[arg]
        if isinstance(values, dict):
            values = list(map(str, values.items()))
        else:
            values = [values]
        self.columnize(values)

    def complete_show(self, text, line, begin, end):
        return self._complete_keys(line)

    def do_down(self, arg):
        data = self._current_data()
        if arg in data:
            self.path.append(arg)
        else:
            self._write_error('invalid key')

    def complete_down(self, text, line, begin, end):
        return self._complete_keys(line)

    def do_up(self, arg):
        if arg:
            self._write_error('command takes no arguments')
            return
        if not self.path:
            self._write_error('already at top')
            return
        self.path.pop()

    def do_add(self, arg):
        """
        Add key.
        """
        data = self._current_data()
        key, _, rest = arg.partition(' ')
        if key in data:
            self._write_error('key exists')
            return
        data[key] = rest if rest else dict()

    def do_set(self, arg):
        """
        Set key value
        """
        data = self._current_data()
        key, _, rest = arg.partition(' ')
        if key not in data:
            self._write_error('key does not exist')
            return
        data[key] = rest if rest else dict()

    def do_del(self, arg):
        """
        Delete key.
        """
        data = self._current_data()
        del data[arg]


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

    editshell = EditShell()
    if args.file:
        editshell.do_load(args.file)
    editshell.cmdloop()
    # TODO
    # - help_* attributes for cleaner help strings
    # - automatically create editor from class and attributes

if __name__ == '__main__':
    main()
