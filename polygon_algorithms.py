import argparse
import enum

class Orientation(enum.Enum):
    COLINEAR = enum.auto()
    CLOCKWISE = enum.auto()
    COUNTER_CLOCKWISE = enum.auto()



def area_polygon(vertices):
    return abs(first_moment(vertices))

def first_moment(vertices):
    n = len(vertices)
    moment = 0.0
    for i in range(n):
        p1 = vertices[i]
        p2 = vertices[(i + 1) % n]
        moment += p1[0] * p2[1] - p1[1] * p2[0]
    moment *= 0.5
    return moment

def get_orientation(p, q, r, atol=1e-6):
    """
    """
    px, py = p
    qx, qy = q
    rx, ry = r
    cross_product = (qy - py) * (rx - qx) - (ry - qy) * (qx - px)

    if abs(cross_product) < atol:
        orientation = Orientation.COLINEAR
    elif cross_product > 0:
        orientation = Orientation.CLOCKWISE
    else:
        orientation = Orientation.COUNTER_CLOCKWISE

    return orientation

def on_segment(q, segment, atol=1e-6, on_line=None):
    """
    Determine if a point lies on the segment.
    """
    p, r = segment
    if on_line is None:
        on_line = get_orientation(p, q, r) == Orientation.COLINEAR
    px, py = p
    rx, ry = r
    is_on_segment = (
        on_line
        and (
            (qx <= max(px + atol, rx + atol))
            and
            (qx >= min(px - atol, rx - atol))
            and
            (qy <= max(py + atol, ry + atol))
            and
            (qy >= min(py - atol, ry - atol))
        )
    )
    return is_on_segment

def point_in_polygon(
    point,
    vertices,
    on_border_is_inside = True,
):
    """
    point_in_polygon(point, vertices)

    Runs in `O(n)` time when `n=length(vertices)`.

    This algorithm is an an extension of the odd-even ray algorithm.
    It is based on "A Simple and Correct Even-Odd Algorithm for the
    Point-in-Polygon Problem for Complex Polygons" by Michael Galetzka and
    Patrick Glauner (2017).
    It skips vertices that are on the ray. To compensate, the ray is projected
    backwards (to the left) so that an intersection can be found for a skipped
    vertix if needed.
    """
    n = len(vertices)
    num_intersections = 0

    xs = [x for x, y in vertices]
    extreme_left = min(xs, default=point[1])
    extreme_right = max(xs, default=point[1])

    # step 1: point intersects a vertex or edge
    for segment in zip(vertices, vertices[1:] + vertices[:1]):
        if point == segment[0] or on_segment(point, segment):
            return on_border_is_inside

    # step 3: check intersections with vertices
    s = 1
    while s <= n:
        # step 2: find a vertix not on the horizontal ray
        while s <= n and vertices[s][1] == point[1]:
            s += 1
        if s > n:
            break
        # step 3a: find the next vertix not on the horizontal ray
        next_s = s
        skipped_right = False
        for i in range(n):
            next_s %= n
            if vertices[next_s][1] != point[1]:
                break
            skipped_right = skipped_right or vertices[next_s][0] > point[0]
        # step 3b: edge intersect with the ray
        edge = (vertices[s], vertices[next_s])
        intersect = 0
        if next_s - s == 1 or s == n and next_s == 1: # 3b.i
            intersect = do_intersect(edge, (point, extreme_right))
        elif skipped_right: # 3b.ii
            intersect = do_intersect(edge, (extreme_left, extreme_right))
        num_intersections += intersect
        if next_s <= s: # gone in a full loop
            break
        s = next_s
    return num_intersections % 2 == 1

def readme_example():
    poly1 = [
        (0.4, 0.5), (0.7, 2.0), (5.3, 1.4), (4.0, -0.6),
    ]

    area_polygon(poly1) # ~= 7.855

    poly2 = [
        (3.0, 3.0), (4.0, 1.0), (3.0, 0.5), (2.0, -0.5), (1.5, 0.9)
    ]

def main(argv=None):
    """
    """
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)
    readme_example()

if __name__ == '__main__':
    main()

# 2023-10-14 Sat.
# Polygon intersections
# - https://liorsinai.github.io/mathematics/2023/09/30/polygon-clipping.html
# - https://github.com/LiorSinai/PolygonAlgorithms.jl
