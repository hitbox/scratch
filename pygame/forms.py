import argparse
import configparser
import enum
import itertools as it
import random
import re

from collections import OrderedDict
from collections import defaultdict
from pprint import pprint
from types import SimpleNamespace

unset_value = object()

class Field:

    prompt = '> '

    def __init__(self, name=None, label=None, default=None):
        self.name = name
        self.label = label
        self.default = default
        self.accepted = False
        self.errors = []
        self.data = None

    def validate(self):
        pass

    def process(self, formdata, data=unset_value):
        """
        Set data attribute from arguments or to default, and collect errors.
        """
        self.process_errors = []

        if data is unset_value:
            data = self.default
            if callable(data):
                data = data()

        self.object_data = data

        try:
            self.process_data(data)
        except ValueError as e:
            self.process_errors.append(e)

        if formdata is not None:
            if self.name in formdata:
                self.raw_data = formdata[self.name]
            else:
                self.raw_data = []

            try:
                self.process_formdata(self.raw_data)
            except ValueError as e:
                self.process_errors.append(e)

    def process_data(self, value):
        self.data = value

    def process_formdata(self, value):
        # Check here to avoid overwriting default.
        # TODO: valuelist
        if value:
            self.data = value


class StringField(Field):
    pass


class IntegerField(Field):

    def process_data(self, value):
        self.data = None
        if value is None or value is unset_value:
            return

        self.data = int(value)

    def process_formdata(self, value):
        # TODO: valuelist
        # TODO: just have a coerce attribute for all fields?
        if value:
            self.data = int(value)


class SelectField(Field):

    def __init__(self, name=None, label=None, default=None, coerce=str, choices=None):
        super().__init__(name, label, default)
        self.coerce = coerce
        self._process_choices(choices)

    def _process_choices(self, choices):
        if callable(choices):
            choices = choices()
        if choices is not None:
            if not isinstance(choices, dict):
                choices = list(choices)
        else:
            choices = None
        self.choices = choices

    def process_data(self, value):
        self.data = None
        if value is not None:
            self.data = self.coerce(value)

    def process_formdata(self, value):
        # TODO: valuelist
        if value:
            self.data = self.coerce(value)


class Form:

    def __init__(self, fields):
        self._fields = fields
        for key, field in fields.items():
            setattr(self, key, field)

    def validate(self):
        success = True
        for field in self._fields.values():
            field.validate()
        return success

    def process(self, formdata=None, obj=None, data=None, **kwargs):
        # TODO: multivalue dict wrapper?
        if data is not None:
            kwargs = dict(data, **kwargs)

        for name, field in self._fields.items():
            if obj is not None and hasattr(obj, name):
                data = getattr(obj, name)
            elif name in kwargs:
                data = kwargs[name]
            else:
                data = unset_value
            field.process(formdata, data)

    def __iter__(self):
        yield from self._fields.values()

    @property
    def data(self):
        return {name: f.data for name, f in self._fields.items()}


def read_form(form):
    for field in form:
        formdata = input(f'{field.label} ({field.default}): ')
        yield (field.name, formdata)

def test_form():
    fields = dict(
        name = StringField(
            name = 'name',
            label = 'Name',
            default = 'name1',
        ),
        age = IntegerField(
            name = 'age',
            label = 'Age',
            default = 30,
        ),
        country = SelectField(
            name = 'country',
            label = 'Country',
            default = '1',
            choices = {
                '0': 'USA',
                '1': 'Britain',
                '2': 'Africa',
                '3': 'Other',
            },
        ),
    )

    form = Form(fields)
    return form

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

    # This is much like wtforms minus declarative style, multidict handling,
    # and most field types.
    # And of course, it is not html

    # TODO make from here on, like a request-response loop
    form = test_form()

    # one-shot, command line analogue to sending html form out to browser and
    # getting it back
    formdata = dict(read_form(form))

    # TODO: this would normally be validate for wtforms
    form.process(formdata)
    print(form.data)

if __name__ == '__main__':
    main()
