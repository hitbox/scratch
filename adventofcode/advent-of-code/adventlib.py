import os
import argparse

__all__ = ['thisdir', 'input_path', 'safeint']

def thisdir():
    return os.path.dirname(os.path.abspath(__file__))

def input_path(filepath, part):
    """
    :param filepath: __file__ from the script
    :param part: the part number
    """

    root, ext = os.path.splitext(filepath)
    input_name = root + '.input' + ('2' if part == 2 else '')
    input_path = os.path.join(thisdir(), 'inputs', input_name)
    return input_path

def safeint(thing):
    try:
        return int(thing)
    except ValueError:
        return thing

def rrange(depth, start, stop=None, step=None, _accum=None):
    """
    Generate n-nested tuples
    rrange(3, 3) => ( (i, j, k) for i in range(3) for j in range(3) for k in range(3) )
    """

    if _accum is None:
        _accum = tuple()

    # range doesn't like being passed None
    if stop and step:
        ranger = range(start, stop, step)
    elif stop:
        ranger = range(start, stop)
    else:
        ranger = range(start)

    for i in ranger:
        if depth == 1:
            yield _accum + (i, )
        else:
            for t in rrange(depth-1, start, stop, step, _accum + (i, )):
                yield t

def parseargs2(other=None):
    parser = argparse.ArgumentParser()

    choices=['part1', 'part2', 'tests']

    if other is not None:
        if isinstance(other, basestring):
            other = [other]
        choices += list(other)

    parser.add_argument('command', choices=choices, help='Command to run.')

    return parser.parse_args()

def parseargs(requirepart=False):
    parser = argparse.ArgumentParser()

    _a = parser.add_argument

    _a('-t', '--test', action='store_true', help='run tests')
    _a('-p', '--part', metavar='n', type=int, choices=[1,2], help='run part n (1, 2)')

    args = parser.parse_args()

    if requirepart and not args.part:
        parser.exit('Part number required')

    return args
