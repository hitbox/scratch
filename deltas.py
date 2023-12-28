import argparse
import math

from pprint import pprint

half_pi = math.pi / 2

named_deltas = {
    'topleft': (-1, -1),
    'midtop': (0, -1),
    'topright': (1, -1),
    'midleft': (-1,  0),
    'center': (0,  0),
    'midright': (1,  0),
    'bottomleft': (-1,  1),
    'midbottom': (0,  1),
    'bottomright': (1,  1),
}

delta_names = {val: key for key, val in named_deltas.items()}

def logical_xor(x, y):
    return bool(x) ^ bool(y)

def anglekey(item):
    x, y = item
    # half-pi to shift atan into 0 -> 2pi
    return half_pi + math.atan2(y, x)

def main(argv=None):
    """
    Test that function produces neighborhood indexes around, and including, the
    center.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', type=int, default=9)
    parser.add_argument('-c', '--cardinal', action='store_true')
    parser.add_argument('-o', '--no-origin', action='store_true')
    args = parser.parse_args(argv)

    # symmectrical so x,y or i,j is up to interpretation
    deltas = set(tuple(v-1 for v in divmod(i, 3)) for i in range(9))
    reference = set(delta_names)
    assert deltas == reference, deltas

    if args.cardinal:
        deltas = set((x, y) for x, y in deltas if logical_xor(x, y))

        if not args.no_origin:
            # add origin back because xor removes it
            deltas.add((0,0))

    if args.no_origin:
        deltas.discard((0,0))

    deltas = sorted(deltas, key=anglekey)

    pprint([(delta, delta_names[delta]) for delta in deltas])

if __name__ == '__main__':
    main()

# Saw this lua function
# https://github.com/heav-4/relocation/blob/main/src/main.lua#L33
# see also: /home/hitbox/repos/reference/heav-4/relocation
# 2023-10-15 Sat.
# - another thing I put down a while ago.
# - I think my interest was that I could just shift the values by -1
# - common need to get the neighbors in a matrix.
