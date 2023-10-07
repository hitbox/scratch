import argparse

from . import run

def main(argv=None):
    """
    Rect cutter.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    args = parser.parse_args(argv)
    run()
