import argparse
import contextlib
import os

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    from pygame import Vector3
    from pygame.color import THECOLORS as colors

def main(argv=None):
    """
    Find a pygame color.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('rgb', nargs=3, type=int)
    parser.add_argument('-n', type=int, default=3)
    args = parser.parse_args(argv)

    reference = Vector3(args.rgb)

    def rgb_distance(item):
        name, color = item
        return reference.distance_squared_to(color[:3])

    result = sorted(colors.items(), key=rgb_distance)
    result = result[:args.n]
    for name, color in result:
        print(name, color)

if __name__ == '__main__':
    main()
