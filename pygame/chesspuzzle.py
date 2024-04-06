import argparse
import csv
import fileinput
import itertools as it
import string

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

fen_optional_keys = (
    'active',
    'castling',
    'en_passant',
    'halfmove_clock',
    'fullmove',
)

lichess_puzzle_keys = (
    'PuzzleId',
    'FEN',
    'Moves',
    'Rating',
    'RatingDeviation',
    'Popularity',
    'NbPlays',
    'Themes',
    'GameUrl',
    'OpeningTags',
)

class KeyFilter:

    def __init__(self, keys):
        self.keys = keys

    def __call__(self, items):
        for key, value in items:
            if key in self.keys:
                yield (key, value)


class TypeConverter:

    def __init__(self, **keys_and_types):
        self.keys_and_types = keys_and_types

    def __call__(self, iterable):
        matched = zip(self.keys_and_types.items(), iterable)
        return tuple((key, type_(value)) for (key, type_), value in matched)


class FENOptionalFieldsConverter(TypeConverter):

    def __init__(self):
        super().__init__(
            # (w)hite or (b)lack
            active = dict(w='white', b='black').__getitem__,
            castling = str_for_dash,
            en_passant = str_for_dash,
            halfmove_clock = int,
            # number of turns
            fullmove = int,
        )


class FENType:

    container_type = tuple

    def generate_row(self, row_string):
        for char in row_string:
            if char.isdigit():
                for i in range(int(char)):
                    # Represents empty squares
                    yield None
            else:
                yield char

    def __call__(self, fen_string):
        board_string, *optional_strings = fen_string.split()
        row_strings = board_string.split('/')
        data = dict(map(FENOptionalFieldsConverter(), optional_strings))
        board = self.container_type(
            map(self.container_type, map(self.generate_row, row_strings))
        )
        data['board'] = board
        return data


class LichessPuzzleType(TypeConverter):

    fen_type_class = FENType

    keys = [
        'PuzzleId',
        'FEN',
        'Moves',
        'Rating',
        'RatingDeviation',
        'Popularity',
        'NbPlays',
        'Themes',
        'GameUrl',
        'OpeningTags',
    ]

    types = [
        str,
        None, # FEN
        # Moves =
        # - UCI parse and convert to SAN
        # - believe that this is minimum 2
        # - first is opponent's move
        str.split,
        int,
        int,
        int,
        int, # not documented, looks like int
        str,
        str,
        str,
    ]

    def __init__(self, fen_type_class=None):
        fen_type_class = fen_type_class or self.fen_type_class
        # NOTES
        # - keywords match CSV by order
        kwargs = dict(
            (key, fen_type_class() if key == 'FEN' else type_)
            for key, type_ in zip(self.keys, self.types)
        )
        super().__init__(**kwargs)

    def from_csv(self, csv_file, fen_type_class=None):
        for row in csv.reader(csv_file):
            yield self(row)



class ChessPuzzleDatabase:

    def __init__(self, nextrows, keys=None):
        self.nextrows = nextrows
        self.rows = []
        self.keys = keys

    @classmethod
    def from_csv(cls, csvfile, skipfirst=True):
        reader = csv.reader(csvfile)
        if skipfirst:
            next(reader)
        return cls(reader)

    def __iter__(self):
        return self

    def __next__(self):
        row = next(self.nextrows)
        self.rows.append(row)
        return row


def expand_fen_row(row):
    for char in row:
        if char.isdigit():
            for _ in range(int(char)):
                yield None
        else:
            yield char

def parse_fen(string):
    board, *rest = string.split()
    data = dict(zip(fen_optional_keys, rest))
    board = [list(expand_fen_row(row)) for row in board.split('/')]
    data['board'] = board
    return data

def parse_lichess_puzzle(values):
    data = dict(zip(lichess_puzzle_keys, values))
    data['FEN'] = parse_fen(data['FEN'])
    return data

def positions(board):
    for rownum, row in enumerate(board):
        for col, piece in zip(string.ascii_lowercase, row):
            yield (f'{col}{rownum}', piece)

def str_for_dash(value):
    if value == '-':
        value = None
    return value

def format_square(value):
    if value is None:
        return ' '
    else:
        return value

def format_board_row(row):
    return ''.join(map(format_square, row))

def format_board(board):
    return '\n'.join(map(format_board_row, board))

def labeled_board(board):
    yield ('  ', ) + tuple(string.ascii_lowercase[:8])
    for inverse_rank, row in enumerate(board):
        yield (f'{8 - inverse_rank} ', ) + tuple(map(format_square, row))

def labeled_board_string(board):
    return "\n".join(map("".join, labeled_board(board)))

def pygame_simple_render(args):
    """
    Display a chess game state with pygame.
    """
    puzzle_type = LichessPuzzleType()
    database = map(parse_lichess_puzzle, database_from_args(args))
    for _ in range(2):
        puzzle = next(database)
    board = puzzle['FEN']['board']

    window = pygame.Rect((0,0), args.display_size)
    clock = pygame.time.Clock()
    framerate = args.framerate
    background = args.background
    running = True
    font = pygamelib.monospace_font(30)
    printfont = pygamelib.FontPrinter(font, 'white')

    def image_for_piece(piece):
        if piece.islower():
            color = 'grey50'
        else:
            color = 'floralwhite'
        image = pygame.Surface((48,)*2)
        text = font.render(piece, True, color)
        image.blit(text, text.get_rect(center=image.get_rect().center))
        pygame.draw.rect(image, 'grey20', image.get_rect(), 1)
        return image

    all_pieces = it.chain(white_pieces, black_pieces)
    piece_images = {piece: image_for_piece(piece) for piece in all_pieces}
    piece_rects = {piece: image.get_rect() for piece, image in piece_images.items()}

    # add empty square
    widths, heights = zip(*map(lambda r: r.size, piece_rects.values()))
    max_width = max(widths)
    max_height = max(heights)
    max_size = (max_width, max_height)
    empty_image = pygame.Surface(max_size)
    empty_rect = empty_image.get_rect()
    pygame.draw.rect(empty_image, 'grey20', empty_rect, 1)
    piece_images[None] = empty_image
    piece_rects[None] = empty_rect

    def get_blit_for_piece(piece):
        if piece:
            image = piece_images[piece]
            rect = piece_rects[piece]
        else:
            image = empty_image
            rect = empty_rect
        # copy for all non-unique pieces
        if piece not in set('KQkq'):
            image = image.copy()
            rect = rect.copy()
        return (image, rect)

    board_blits = tuple(
        get_blit_for_piece(piece) for row in board for piece in row
    )

    board_rects = [rect for image, rect in board_blits]
    pygamelib.arrange_columns(board_rects, 8, 'centerx', 'centery')
    board_frame = pygame.Rect(pygamelib.wrap(board_rects))

    screen = pygame.display.set_mode(window.size)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
        screen.fill(background)
        screen.blits(board_blits)
        lines = [f'{key}={val}' for key, val in puzzle['FEN'].items() if key != 'board']
        image = printfont(lines)
        screen.blit(image, image.get_rect(topleft=board_frame.bottomleft))
        pygame.display.flip()
        elapsed = clock.tick(framerate)

def argument_parser():
    parser = argparse.ArgumentParser()
    add_common_arguments(parser)

    subparsers = parser.add_subparsers()
    add_parse_and_print_subcommand(subparsers)
    add_display_pygame_subcommand(subparsers)

    return parser

def default_subcommand():
    return parse_and_print

def add_common_arguments(parser):
    """
    Add arguments common to parser and all subparsers.
    """
    parser.add_argument(
        '--from-csv',
        type = argparse.FileType('r'),
        help = 'Load puzzles from CSV.',
    )

def add_parse_and_print_subcommand(subparsers):
    """
    Parse command line arguments for filtering and diplaying lichess puzzles
    data.
    """
    sp = subparsers.add_parser('parse')
    add_common_arguments(sp)

    default_help = ' '.join(LichessPuzzleType.keys)
    sp.add_argument(
        '--list-keys',
        action = 'store_true',
        help = 'List keys that can be displayed.',
    )

    sp.add_argument(
        '--display',
        help = f'Expression eval-ed with puzzle data.'
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
    sp.set_defaults(subfunc=parse_and_print)

def add_display_pygame_subcommand(subparsers):
    sp = subparsers.add_parser('pygame')
    add_common_arguments(sp)
    pygamelib.add_display_size_option(sp)
    pygamelib.add_framerate_option(sp)
    pygamelib.add_background_color_option(sp)
    sp.set_defaults(subfunc=pygame_simple_render)

def default_display_expression():
    return ','.join(LichessPuzzleType.keys)

def database_from_args(args):
    if args.from_csv:
        reader = csv.reader(args.from_csv)
        # skip header
        next(reader)
        return reader
    else:
        return fileinput.input()

def parse_and_print(args):
    if args.list_keys:
        for key in LichessPuzzleType.keys:
            print(key)
        return

    puzzle_type = LichessPuzzleType()
    displayer = KeyFilter(args.display)

    display_expr = args.display or default_display_expression()
    display_expr = compile(display_expr, __name__, 'eval')

    filter_expr = compile(args.filter or 'True', __name__, 'eval')
    database = database_from_args(args)
    for puzzle in map(dict, map(puzzle_type, database)):
        if not eval(filter_expr, puzzle):
            continue
        if not args.quiet:
            print(eval(display_expr, globals(), puzzle))

def main(argv=None):
    parser = argument_parser()
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
