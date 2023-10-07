import argparse

from pathlib import Path

from oct2rwx import oct2rwx

def main(argv=None):
    """
    Print table of all possible rwx.
    """
    parser = argparse.ArgumentParser(prog=Path(__file__).stem,
            description=main.__doc__)
    args = parser.parse_args(argv)

    # build list of liens - header
    lines = [('Dec', 'Bin', 'RWX')]
    # all values for decimal, binary, and rwx.
    lines += [ (str(i), '{:>03}'.format(bin(i)[2:]), oct2rwx(i)) for i in range(8) ]
    # max length of each column
    maxes = [max(map(len, column)) for column in zip(*lines)]
    # per-column formatters
    formatters = list('{:>%s}' % width for width in maxes)
    # format and print each line
    for tup in lines:
        print(' '.join(f.format(s) for s, f in zip(tup, formatters)))

if __name__ == '__main__':
    main()
