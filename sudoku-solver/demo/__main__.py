import argparse

from . import run

def main(argv=None):
    """
    Testing this framework thing I'm sketching out.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    args = parser.parse_args(argv)
    run.run()

main()
