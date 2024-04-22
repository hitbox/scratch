import sqlalchemy as sa

from flask import Flask

from . import extensions
from . import models

class StringWrapper:

    def __init__(self, left_and_right):
        left, right = left_and_right
        self.left = left
        self.right = right

    def __call__(self, string):
        return f'{self.left}{string}{self.right}'


def column_converter(column):
    name = column.type.python_type.__name__
    if name == 'str':
        name = 'string'
    return name

def rule_item(column):
    return (column_converter(column), column.name)

def url_rules_for_model(model):
    mapper = sa.inspect(model)
    items = map(rule_item, mapper.primary_key)
    for converter_and_name in items:
        yield ':'.join(map(str, converter_and_name))

def create_app():
    app = Flask(__name__)

    app.config.from_envvar('NEEDFUL_CONFIG')

    extensions.init_app(app)

    tagger = StringWrapper('<>')

    # NOTES
    # - not so sure this is a good idea
    # - you got the automatic generation of url rules but then you have to give
    #   the function arguments
    # - what order?
    # - how much is really being saved?

    @app.route('/'.join(map(tagger, url_rules_for_model(models.Book))))
    def test(isbn):
        return str(isbn)

    return app
