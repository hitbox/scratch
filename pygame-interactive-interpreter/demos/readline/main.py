from engine.engine import Engine
from engine.engine import stopengine
from lib.cli import simple_parser
from lib.external import pygame
from lib.font import PygameFont
from lib.readline import Readline
from lib.rect import wraprects
from lib.screen import Screen

from .scene import ReadlineScene

def main(argv=None):
    parser = simple_parser(description=ReadlineScene.__doc__)
    args = parser.parse_args(argv)

    engine = Engine()
    scene = ReadlineScene(args.screen_size)
    engine.run(scene)
