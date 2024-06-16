import argparse
import configparser
import unittest

class TestConfigArgs(unittest.TestCase):

    def test_empty_argument_parser(self):
        ap = argparse.ArgumentParser()
        cp = configparser.ConfigParser()
        cp.read([])

        args = configargs(ap, cp['DEFAULT'])
        self.assertEqual(args, argparse.Namespace())

    def test_boolean_flag(self):
        ap = argparse.ArgumentParser()
        ap.add_argument('--dry', action='store_true')
        cp = configparser.ConfigParser()
        cp.read_dict({
            '__test__': {
                'dry': '',
            },
        })

        args = configargs(ap, cp['__test__'])
        self.assertEqual(args, argparse.Namespace(dry=True))


def ensure_prefix(key, prefix):
    if not key.startswith(prefix):
        key = prefix + key
    return key

def section_as_arguments(section, long_option_prefix='--'):
    """
    """
    for key, val in section.items():
        yield ensure_prefix(key, long_option_prefix)
        yield val

def configargs(argument_parser, config_section):
    """
    Parse arguments from a configparser section using a command line argument
    parser, treating the keys like long options.
    """
    # TODO
    # - probably extend argparse to accept yes, no, etc. for booleans
    # - probably call .getboolean somehow
    secargs = list(section_as_arguments(config_section))
    print(secargs)
    breakpoint()
    return argument_parser.parse_args(secargs)

# NOTES
# - always have argparse parser
# - almost always requires one argument to a config file
# - want to pick up argparse arguments from the config file
# - want config file to be the defaults
# - want to override them with command line arguments
# - problem with argparse is very complex and intended to parse list of strings
#   from argv
# - thinking about a generic library the takes strings and turns them into
#   Python objects and validates them
#   - a general purpose wtforms
#   - very often have strings from some stream and want to validate and convert
#   - automatically produce an argparse parser
#   - automatically produce a configparser parser that imposes validation and
#     and conversion like argparse
#   - automatically produce wtforms forms that could take similar from things
#     like what the web frameworks produce
#   - automatically produce sqlalchemy mapped classes and/or tables
#   - automatically marshmallow
