import argparse

from pathlib import Path

def oct2rwx(i):
    bits = '{:>03}'.format(bin(i)[2:])
    return ''.join(perm if bit == '1' else '-' for bit, perm in zip(bits, 'rwx'))

def main(argv=None):
    """
    Convert integer to rwx.
    """
    parser = argparse.ArgumentParser(prog=Path(__file__).stem, description=main.__doc__)
    parser.add_argument('oct', type=int)
    args = parser.parse_args(argv)
    print(oct2rwx(args.oct))

if __name__ == '__main__':
    main()
