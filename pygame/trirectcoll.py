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

def main():
    # Example usage:
    triangle = [(0, 0), (2, 0), (1, 2)]
    rectangle = [(1, 1), (4, 1), (4, 4), (1, 4)]

    collision = triangle_rect_collision(triangle, rectangle)
    print("Collision:", collision)

if __name__ == '__main__':
    main()
