import argparse
import random

from .model import Solitaire
from .model import make_deck
from .pygame_gui import pygame_gui

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

    solitaire = Solitaire()
    deck = make_deck()
    assert len(deck) == 52
    random.shuffle(deck)
    solitaire.setup(deck)
    solitaire.reveal_stock()

    pygame_gui(solitaire)

main()
