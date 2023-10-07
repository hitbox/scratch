import argparse
from pathlib import Path

charmap = dict(zip('-rwx', (2 ** n if n > -1 else 0 for n in range(-1, 5))))

def rwx2oct(perm):
    return sum(charmap[char] for char in perm)

def main(argv=None):
    """
    Utility to turn user-friendly rwx into an integer representation.
    """
    # change prefix chars to allow --- as a permission
    parser = argparse.ArgumentParser(prog=Path(__file__).stem,
            description=main.__doc__, prefix_chars='/')
    parser.add_argument('permissions', nargs='+',
            help='Up to three sets of permissions (rwx-) sets for user, group,'
                 ' and others.')
    args = parser.parse_args(argv)

    if len(args.permissions) > 3:
        parser.error('permissions only takes up to three args.')

    for perm in args.permissions:
        if set(perm) - set(charmap):
            parser.error(f'invalid character in {perm!r}')

    print(''.join(str(rwx2oct(perm)) for perm in args.permissions))

if __name__ == '__main__':
    main()
