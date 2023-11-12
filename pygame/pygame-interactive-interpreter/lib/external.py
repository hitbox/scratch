import contextlib
import os

# silence pygame's cute little message
with open(os.devnull, 'w') as blackhole:
    with contextlib.redirect_stdout(blackhole):
        import pygame

del blackhole
