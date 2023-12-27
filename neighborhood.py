import argparse
import math

def main(argv=None):
    """
    Test that function produces neighborhood indexes around, and including, the
    center.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', type=int, default=9)
    args = parser.parse_args(argv)

    deltas = set(tuple(value - 1 for value in divmod(i, 3)) for i in range(9))
    reference = set([
        (-1, -1), (0, -1), (1, -1),
        (-1,  0), (0,  0), (1,  0),
        (-1,  1), (0,  1), (1,  1),
    ])
    assert deltas == reference, deltas

    deltas.remove((0,0))

    def key(item):
        x, y = item
        angle = math.pi - math.atan2(y, x) % math.tau
        return angle

    from pprint import pprint
    pprint([(delta, math.degrees(key(delta))) for delta in sorted(deltas, key=key)])

if __name__ == '__main__':
    main()

# Saw this lua function
# https://github.com/heav-4/relocation/blob/main/src/main.lua#L33
# see also: /home/hitbox/repos/reference/heav-4/relocation
# 2023-10-15 Sat.
# - another thing I put down a while ago.
# - I think my interest was that I could just shift the values by -1
# - common need to get the neighbors in a matrix.
