import argparse
import csv
import pickle

import pygamelib

from pygamelib import pygame

FIELDS = ['hexcolor', 'user_named', 'votes']

def deserialize(rows):
    for hexcolor, user_named, votes in rows:
        hexcolor = int(hexcolor, 16)
        votes = int(votes)
        yield (hexcolor, user_named, votes)

def to_pickle(args):
    with open(args.csvfile) as csv_file:
        reader = csv.reader(csv_file)
        next(reader)
        colors = list(deserialize(reader))

    with open(args.output, 'wb') as pickle_file:
        pickle.dump(colors, pickle_file)

def from_pickle(inputpath):
    with open(inputpath, 'rb') as input_file:
        return pickle.load(input_file)

def display(colors):
    framerate = 60
    clock = pygame.time.Clock()
    window = pygame.Rect(0, 0, 800, 800)
    screen = pygame.display.set_mode(window.size)
    background = screen.copy()
    width = window.width // len(colors)
    for color, x in zip(colors, range(0, window.width, width)):
        pygame.draw.rect(background, color, (x, 0, width, window.height))
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
        screen.blit(background, (0,0))
        pygame.display.flip()
        elapsed = clock.tick(framerate)

def select(args):
    do_pygame = args.pygame
    if args.select:
        select_fields = args.select.replace(',', ' ').split()
    else:
        select_fields = FIELDS
    if args.where:
        where = args.where
    else:
        where = 'True'
    where = compile(where, __name__, 'eval')
    colors = from_pickle(args.pickle)
    selected = []
    for values in colors:
        data = dict(zip(FIELDS, values))
        if eval(where, data):
            if not do_pygame:
                print(' '.join(str(data[field]) for field in select_fields))
            else:
                selected.append(data['hexcolor'])

    if do_pygame:
        display(selected)

def add_pygame_arguments(parser):
    parser.add_argument(
        '--pygame',
        action = 'store_true',
        help = 'Display colors with pygame.',
    )

def argument_parser():
    parser = argparse.ArgumentParser()
    add_pygame_arguments(parser)

    subparsers = parser.add_subparsers()

    sp = subparsers.add_parser('to_pickle')
    sp.add_argument('csvfile')
    sp.add_argument('output')
    sp.set_defaults(func=to_pickle)

    sp = subparsers.add_parser('select')
    add_pygame_arguments(sp)
    sp.add_argument('pickle')
    sp.add_argument('--select')
    sp.add_argument('--where')
    sp.set_defaults(func=select)

    return parser

def main(argv=None):
    parser = argument_parser()
    args = parser.parse_args(argv)

    func = args.func
    del args.func

    func(args)

if __name__ == '__main__':
    main()

# 2024-04-23 Tue.
# parse and display colors from colornames.org
# https://colornames.org/download/
