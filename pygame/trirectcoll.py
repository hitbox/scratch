import argparse

def dot(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1]

def subtract(v1, v2):
    return (v1[0] - v2[0], v1[1] - v2[1])

def perp(v):
    return (-v[1], v[0])

def project(shape, axis):
    min_val = float('inf')
    max_val = float('-inf')

    for point in shape:
        projection = dot(point, axis)
        min_val = min(min_val, projection)
        max_val = max(max_val, projection)

    return (min_val, max_val)

def overlap(interval1, interval2):
    return interval1[1] >= interval2[0] and interval2[1] >= interval1[0]

def triangle_rect_collision(triangle, rect):
    # TODO
    # - pull this apart
    # - understand it
    # - put it in pygamelib
    axes = [
        perp(subtract(triangle[0], triangle[1])),
        perp(subtract(triangle[1], triangle[2])),
        (1, 0),  # x-axis
        (0, 1),  # y-axis
    ]

    for axis in axes:
        proj_triangle = project(triangle, axis)
        proj_rect = project(rect, axis)

        if not overlap(proj_triangle, proj_rect):
            return False

    return True

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--tri',
        type = eval,
        default = '[(0, 0), (2, 0), (1, 2)]',
        help = 'Three points of a triangle.',
    )
    parser.add_argument(
        '--rect',
        type = eval,
        default = '[(1, 1), (4, 1), (4, 4), (1, 4)]',
        help = 'Four points of a rectangle.',
    )
    args = parser.parse_args(argv)

    collision = triangle_rect_collision(args.tri, args.rect)
    print(f'{collision=}')

if __name__ == '__main__':
    main()

# 2024-03-15 Fri.
# - popping back in here
# - looked interesting enough to keep
# - added argparse
# - this must have come from chatgpt
