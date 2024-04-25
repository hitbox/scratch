import argparse
import configparser
import enum
import itertools as it
import random
import re

from collections import defaultdict
from pprint import pprint
from types import SimpleNamespace

class StringWidget:

    def __call__(self, field, **kwargs):
        return str(field)


class SelectWidget:

    def __call__(self, field, **kwargs):
        for choice in field.choices:
            print(choice)


class Input:

    def __init__(self, prompt, input_=input):
        self.prompt = prompt
        self.input_ = input_

    def __call__(self):
        return self.input_(self.prompt)


class Field:

    prompt = '> '

    def __init__(self, label=None):
        self.label = label
        self.accepted = False
        self.errors = []

    def validate(self):
        pass

    def accept(self, value):
        self.value = value
        self.accepted = True


class StringField(Field):

    def validate(self, value):
        return value != ''


class IntegerField(Field):

    def validate(self, value):
        pass


class Form:

    def __init__(self, **fields):
        self.fields = fields

    def unaccepted(self):
        for field in self.fields.values():
            if not field.accepted:
                yield field

    def validate(self):
        for field in self.fields.values():
            field.validate()


def read_input_loop(form, default=None):
    while (unaccepted := list(form.unaccepted())):
        for field in unaccepted:
            print(field.label)
            value = input(field.prompt)
            field.accept(value)

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

    # 1. define fields inside a container
    # 2. display form
    # 3. take input
    # 4. goto 3 until all fields have input
    # 5. process strings and validate
    # 6. if errors goto 2
    # 7. use data from form

    form = Form(
        name = StringField(
            label = 'Name',
        ),
    )
    while True:
        read_input_loop(form)
        if form.validate():
            break

if __name__ == '__main__':
    main()
