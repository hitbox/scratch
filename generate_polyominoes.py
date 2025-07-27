import argparse

from collections import deque
from itertools import tee

# Motivations:
# - https://log.pfad.fr/2025/optimi-zig-sudoku-solving/
# - https://en.wikipedia.org/wiki/Dancing_Links
# I was reading those and tore off on polyominoes generation, inspired by the
# animation on the wikipedia page.

# 1. Initial shape: [(0,0)]
# 2. For each square in shape, choose all valid side-connected squares.
# 3. Add new squares to shape until length is satisfied.
# 4. Add shape to a set.

def create_shape(length, _shape=None):
    if _shape is None:
        _shape = [(0,0)]
    elif len(_shape) == length:
        yield _shape
        return

    for square in _shape:
        for delta in [(1,0), (0,1)]:
            new_square = tuple(sd + dd for sd, dd in zip(square, delta))
            if new_square not in _shape:
                yield from create_shape(length, _shape=_shape + [new_square])

def to_string(shape):
    # shape is a list of (x, y) points
    xs, ys = zip(*shape)
    maxx = max(xs)
    maxy = max(ys)

    lines = []
    for y in range(maxy+1):
        line = ''
        for x in range(maxx+1):
            line += '#' if (x, y) in shape else '_'
        lines.append(line)

    return '\n'.join(lines)

def rotate_90(x, y, steps=1):
    for _ in range(steps):
        x, y = (y, -x)
    return (x, y)

def rotate_90_shape(shape, steps=1):
    yield from (rotate_90(x, y, steps) for x, y in shape)

def normalize_shape(shape):
    shape1, shape2 = tee(shape)
    xs, ys = zip(*shape1)
    normx = -min(xs)
    normy = -min(ys)
    yield from ((x + normx, y + normy) for x, y in shape2)

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-n', '--squares',
        type = int,
        default = 4,
        help = 'Number of squares per polyominoes.',
    )
    args = parser.parse_args(argv)

    shapes = set()
    unique_shapes = set()
    for index, shape_coords in enumerate(create_shape(args.squares)):
        shape_coords = frozenset(shape_coords)
        rotated = set(
            frozenset(normalize_shape(rotate_90_shape(shape_coords, steps=steps)))
            for steps in range(3)
        )
        if (
            shape_coords not in shapes
            and rotated.isdisjoint(shapes)
        ):
            unique_shapes.add(shape_coords)
            shapes.add(shape_coords)
            for shape_coords in rotated:
                shapes.add(shape_coords)

    for index, shape_coords in enumerate(unique_shapes, start=1):
        shape = to_string(shape_coords)
        print(f'Shape: {index}')
        print(f'{shape}')

if __name__ == '__main__':
    main()
