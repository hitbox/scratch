"""
Silence the import of pygame
"""
import contextlib
import os

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame
