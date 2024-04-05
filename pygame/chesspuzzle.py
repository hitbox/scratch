import argparse
import csv
import fileinput

import pygamelib

from pygamelib import pygame

player_name = {'w': 'white', 'b': 'black'}

white_pieces = {
    'K': 'King',
    'Q': 'Queen',
    'R': 'Rook',
    'B': 'Bishop',
    'N': 'Knight',
    'P': 'Pawn',
}

black_pieces = {key.lower(): name for key, name in white_pieces.items()}

def lichess_puzzle_format():
    return {
        'PuzzleId': str,
        'FEN': parse_fen,

        # Moves:
        # - UCI parse and convert to SAN
        # - believe that this is minimum 2
        # - first is opponent's move
        'Moves': str.split,

        'Rating': int,
        'RatingDeviation': int,
        'Popularity': int,
        'NbPlays': int, # not documented, looks like int
        'Themes': str,
        'GameUrl': str,
        'OpeningTags': str,
    }

def get_print_formatters():
    return dict()

def generate_lichess_puzzle(rowstring):
    keys_types = lichess_puzzle_format().items()
    values = rowstring.split(',')
    yield from typify_lichess_values(keys_types, values)

def typify_lichess_values(keys_types, values):
    for (key, type_), value in zip(keys_types, values):
        typed = type_(value)
        yield (key, typed)

def parse_lichess_puzzle(rowstring):
    data = dict(generate_lichess_puzzle(rowstring))
    return data

def parse_fen(fen):
    optional_keys = (
        'active', # (w)hite or (b)lack
        'castling', # TODO: string indicating castling rights
        'en_passant', # TODO: string of some kind
        'halfmove_clock', # a digit? what are halfmoves?
        'fullmove', # number of black and white moves in this position
    )
    placement, *remaining = fen.split(' ')
    data = dict(zip(optional_keys, remaining))

    data['board'] = board = []
    rows = fen.split()[0].split('/')
    for row in rows:
        board_row = []
        for char in row:
            if char.isdigit():
                for i in range(int(char)):
                    # Represents empty squares
                    board_row.append(None)
            else:
                board_row.append(char)
        board.append(board_row)

    return data

def format_board_row(row):
    return ''.join(' ' if value is None else value for value in row)

def format_board(board):
    return '\n'.join(map(format_board_row, board))

def pygame_simple_render(board):
    pass

def example():
    fen_str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
    board = parse_fen(fen_str)

    # Printing the parsed board
    for row in board['board']:
        print(''.join(' ' if value is None else value for value in row))

def lichess_keys_choices():
    keys_and_types = lichess_puzzle_format()
    keys_choices = list(keys_and_types.keys())
    return keys_choices

def add_parse_subcommand(subparsers):
    sp = subparsers.add_parser('parse')
    add_common_arguments(sp)

    keys_choices = lichess_keys_choices()
    default_help = ' '.join(keys_choices)
    sp.add_argument(
        '--display',
        default = keys_choices,
        type = pygamelib.splitarg,
        help = f'Keys to display. Default {default_help}.'
    )

    sp.add_argument(
        '--filter',
        help = 'Eval-able string with puzzle data context.'
    )

    sp.add_argument(
        '--quiet',
        action = 'store_true',
        help = 'No output.'
    )
    sp.set_defaults(subfunc=print_rows_data)

def argument_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    add_parse_subcommand(subparsers)
    return parser

def cli(args):
    for line in fileinput.input():
        puzzle_data = parse_lichess_puzzle(line)
        print(format_board_row(puzzle_data['FEN']['board']))
        print(f"{player_name[puzzle_data['FEN']['active']]} to play")

def lichess_puzzles_from_csv(csvfile):
    keys_types = lichess_puzzle_format().items()
    reader = csv.reader(csvfile)
    next(reader)
    for values in reader:
        yield dict(typify_lichess_values(keys_types, values))

def print_rows_data(args):
    if not set(args.display).issubset(lichess_keys_choices()):
        raise ValueError('invalid key')
        return

    print_formatters = get_print_formatters()

    def filter_keys(data):

        # NOTES
        # - does not work to print board
        # - need to access subkey 'board'

        def format_value(key, value):
            if key in print_formatters:
                return print_formatters[key](value)
            else:
                return value

        display_data = {
            key: format_value(key, value)
            for key, value in puzzle_data.items()
            if key in args.display
        }
        return display_data

    if args.from_csv:
        rows = lichess_puzzles_from_csv(args.from_csv)
    else:
        rows = fileinput.input()

    if args.filter:
        filter_expr = compile(args.filter, __name__, 'eval')
    else:
        filter_expr = None

    for puzzle_data in rows:
        if filter_expr:
            if not eval(filter_expr, puzzle_data):
                continue
        display_data = filter_keys(puzzle_data)
        if args.quiet:
            continue
        print(display_data)

def default_subcommand():
    return print_rows_data

def add_common_arguments(parser):
    parser.add_argument(
        '--from-csv',
        type = argparse.FileType('r'),
        help = 'Load puzzles from CSV.',
    )

def main(argv=None):
    parser = argument_parser()
    add_common_arguments(parser)
    args = parser.parse_args(argv)

    if 'subfunc' not in args:
        args.subfunc = default_subcommand()

    subfunc = args.subfunc
    del args.subfunc
    subfunc(args)

if __name__ == '__main__':
    main()

# 2024-04-05 Fri.
# https://database.lichess.org/#puzzles
# - use chess puzzles as a minigame
# - easiest should be mate in one
# - difficulty == number of moves to solve
# - further difficulty: require perfect play or allow attempts or even infinite attempts
# - maybe allow bypass (for any kind of minigame) for easiest
# - allow bypass but reward playing and winning?
# TODO
# - parse database
# - represent chess game state
#   - [X] list-o-lists
# - render game state
#   - [X] console print
#   - [ ] graphical
# - user input and check against solution loop
