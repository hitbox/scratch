import abc
import argparse
import csv
import fileinput
import itertools as it
import string

import pygamelib

from pygamelib import pygame

PLAYER_NAME = {'w': 'white', 'b': 'black'}

RANKS = string.digits[8:0:-1]
FILES = string.ascii_lowercase[:8]

SQUARES = tuple(map(''.join, it.product(FILES, RANKS)))

assert len(SQUARES) == 8*8

SQUARES_BY_RANK = {
    rank: tuple(map(''.join, (zip(FILES, it.repeat(rank)))))
    for rank in RANKS
}

assert all(len(values) == 8 for values in SQUARES_BY_RANK.values())

WHITE_PIECES = {
    'K': 'King',
    'Q': 'Queen',
    'R': 'Rook',
    'B': 'Bishop',
    'N': 'Knight',
    'P': 'Pawn',
}

WHITE_ROYALTY = 'KQ'

BLACK_PIECES = {key.lower(): name for key, name in WHITE_PIECES.items()}
BLACK_ROYALTY = 'kq'

ROYALTY = WHITE_ROYALTY + BLACK_ROYALTY
PIECES = dict(
    (symbol, ('White ' if symbol.isupper() else 'Black ') + name)
    for symbol, name in it.chain(WHITE_PIECES.items(), BLACK_PIECES.items())
)

FEN_OPTIONAL_KEYS = (
    'active',
    'castling',
    'en_passant',
    'halfmove_clock',
    'fullmove',
)

LICHESS_PUZZLE_KEYS = (
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
    data = dict(zip(FEN_OPTIONAL_KEYS, rest))
    board = [list(expand_fen_row(row)) for row in board.split('/')]
    data['board'] = board
    return data

def parse_lichess_puzzle(values):
    data = dict(zip(LICHESS_PUZZLE_KEYS, values))
    data['FEN'] = parse_fen(data['FEN'])
    return data

def positions(board):
    for rownum, row in enumerate(board):
        for col, piece in zip(RANKS, row):
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
    yield ('  ', ) + tuple(FILES)
    for inverse_rank, row in enumerate(board):
        yield (f'{8 - inverse_rank} ', ) + tuple(map(format_square, row))

def labeled_board_string(board):
    return "\n".join(map("".join, labeled_board(board)))

class FontRendererBase(abc.ABC):

    @abc.abstractmethod
    def __call__(self, piece):
        pass


class FontRenderer(FontRendererBase):

    def __init__(
        self,
        font,
        color,
        size_and_position = None,
        antialias = True,
    ):
        """
        :param size_and_position:
            two-tuple size to use instead of font.render result and an
            attribute to align the rect on.
        """
        self.font = font
        self.color = color
        self.size_and_position = size_and_position
        self.antialias = antialias

    def __call__(self, text):
        text_image = self.font.render(text, self.antialias, self.color)
        if self.size_and_position:
            size, attr = self.size_and_position
            bg_image = pygame.Surface(size, pygame.SRCALPHA)
            bg_rect = bg_image.get_rect()
            kwargs = {attr: getattr(bg_rect, attr)}
            bg_image.blit(text_image, text_image.get_rect(**kwargs))
            text_image = bg_image
        return text_image


class FontPieceRenderer(FontRendererBase):

    def __init__(
        self,
        font,
        white_color,
        black_color,
        size_and_position = None,
        antialias = True,
    ):
        """
        :param size_and_position:
            two-tuple size to use instead of font.render result and an
            attribute to align the rect on.
        """
        self.font = font
        self.white_color = white_color
        self.black_color = black_color
        self.size_and_position = size_and_position
        self.antialias = antialias

    def __call__(self, piece):
        if piece.islower():
            color = self.black_color
        else:
            color = self.white_color
        text_image = self.font.render(piece, self.antialias, color)
        if self.size_and_position:
            size, attr = self.size_and_position
            bg_image = pygame.Surface(size, pygame.SRCALPHA)
            bg_rect = bg_image.get_rect()
            kwargs = {attr: getattr(bg_rect, attr)}
            bg_image.blit(text_image, text_image.get_rect(**kwargs))
            text_image = bg_image
        return text_image


class ImageSet:

    def __init__(self, pieces, ranks, files):
        self.pieces = pieces
        self.ranks = ranks
        self.files = files

    @classmethod
    def from_renderer(cls, piece_renderer, label_renderer):
        return cls(
            pieces = {piece: piece_renderer(piece) for piece in PIECES},
            ranks = {rank: label_renderer(rank) for rank in RANKS},
            files = {file: label_renderer(file) for file in FILES},
        )


def default_piece_renderer(font):
    piece_renderer = FontPieceRenderer(
        font,
        'floralwhite',
        'grey50',
        size_and_position = (
            (64,)*2, 'center'
        ),
    )
    return piece_renderer

def pygame_simple_render(args):
    """
    Display a chess game state with pygame.
    """
    database = map(parse_lichess_puzzle, database_from_args(args))
    puzzle = next(database)
    board = puzzle['FEN']['board']
    board_dict = {
        f'{column}{rank}': piece
        for rank, row in zip(RANKS, board)
        for column, piece in zip(FILES, row)
        if piece is not None
    }

    window = pygame.Rect((0,0), args.display_size)
    clock = pygame.time.Clock()
    framerate = args.framerate
    background = args.background
    running = True
    piece_font = pygamelib.monospace_font(30)
    small_font = pygamelib.monospace_font(18)
    printfont = pygamelib.FontPrinter(small_font, 'white')

    piece_renderer = default_piece_renderer(piece_font)
    label_renderer = FontRenderer(
        piece_font,
        'grey35',
        size_and_position = (
            (64,)*2, 'center'
        ),
    )
    images = ImageSet.from_renderer(piece_renderer, label_renderer)

    square_rect = pygame.Rect(pygamelib.make_rect(size=args.square_size))

    # NOTES
    # - relies on insertion order for column arrangement
    squares_rects = {}
    board_rects = {None: square_rect.copy()}
    files_rects = {file: square_rect.copy() for file in FILES}
    board_rects.update(files_rects)
    ranks_rects = {}
    for rank in RANKS:
        ranks_rects[rank] = square_rect.copy()
        board_rects[rank] = ranks_rects[rank]
        squares_for_rank = SQUARES_BY_RANK[rank]
        squares_rects.update({square: square_rect.copy() for square in squares_for_rank})
        board_rects.update(squares_rects)

    pygamelib.arrange_columns(board_rects.values(), 8+1, 'centerx', 'centery')
    pygamelib.move_as_one(board_rects.values(), center=window.center)
    # labels and square are all in a grid now
    # want to center the squares and align the label to them
    delta = pygamelib.move_as_one(squares_rects.values(), center=window.center)

    for file_rect in files_rects.values():
        file_rect.topleft += delta
    for rank_rect in ranks_rects.values():
        rank_rect.topleft += delta

    screen = pygame.display.set_mode(window.size)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
        screen.fill(background)
        for square, rect in board_rects.items():
            if square is None:
                continue
            image = None
            color = None
            if square in images.ranks:
                image = images.ranks[square]
            elif square in images.files:
                image = images.files[square]
            elif square in board_dict:
                color = 'grey20'
                piece = board_dict[square]
                image = images.pieces[piece]
            else:
                color = 'grey20'
            if color:
                pygame.draw.rect(screen, color, rect, 1)
            if image:
                screen.blit(image, rect)
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
    """
    Display with pygame.
    """
    sp = subparsers.add_parser('pygame')
    add_common_arguments(sp)
    pygamelib.add_display_size_option(sp)
    pygamelib.add_framerate_option(sp)
    pygamelib.add_background_color_option(sp)
    sp.add_argument(
        '--square-size',
        type = pygamelib.sizetype(),
        default = '48',
        help = 'Pixel size of square. Default %(default)s.',
    )
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

def display_expr_from_args(args, default=default_display_expression):
    display_expr = args.display or (default() if callable(default) else default)
    display_expr = compile(display_expr, __name__, 'eval')
    return display_expr

def filter_expr_from_args(args, default='True'):
    expr = args.filter or (default() if callable(default) else default)
    expr = compile(expr, __name__, 'eval')
    return expr

def parse_and_print(args):
    """
    Parse Lichess puzzle database and print.
    """
    if args.list_keys:
        for key in LICHESS_PUZZLE_KEYS:
            print(key)
        return

    display_expr = display_expr_from_args(args)
    filter_expr = filter_expr_from_args(args)

    database = database_from_args(args)
    database = map(parse_lichess_puzzle, database)
    for puzzle in database:
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
