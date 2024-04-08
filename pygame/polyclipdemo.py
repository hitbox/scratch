import pygamelib

from pygamelib import pygame

def inside(p, clip_window):
    x, y = p
    # Check if the point is inside the clip window
    return (
        clip_window[0][0] <= x <= clip_window[2][0]
        and clip_window[0][1] <= y <= clip_window[2][1]
    )

def compute_intersection(p1, p2, p3, p4):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denominator == 0:
        return
    intersect_x = (
        ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4))
        / denominator
    )
    intersect_y = (
        ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4))
        / denominator
    )
    return (intersect_x, intersect_y)

def clip_polygon(subject_polygon, clip_window):
    output_list = subject_polygon
    for edge in clip_window:
        input_list = output_list
        output_list = []
        S = input_list[-1]
        for E in input_list:
            if inside(E, clip_window):
                if not inside(S, clip_window):
                    intersect = compute_intersection(S, E, clip_window[0], clip_window[1])
                    if intersect:
                        output_list.append(intersect)
                output_list.append(E)
            elif inside(S, clip_window):
                intersect = compute_intersection(S, E, clip_window[0], clip_window[1])
                if intersect:
                    output_list.append(intersect)
            S = E
        if not output_list:
            break
    return output_list

def run(display_size, framerate, background, poly1, poly2):
    screen = pygame.display.set_mode((900, 800))
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
        screen.fill('black')
        pygame.draw.polygon(screen, 'grey20', poly1, 2)
        pygame.draw.polygon(screen, 'grey20', poly2, 3)
        for vertex in poly1:
            pygame.draw.circle(screen, 'grey20', vertex, 5)
        clipped_polygon = clip_polygon(poly1, poly2)
        pygame.draw.polygon(screen, 'brown', clipped_polygon, 1)
        for vertex in clipped_polygon:
            pygame.draw.circle(screen, 'green', vertex, 4)
        pygame.display.flip()
        clock.tick(60)

def poly_type(string):
    return [tuple(map(int, nums.split())) for nums in string.split(',')]

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument(
        'poly1',
        type = poly_type,
    )
    parser.add_argument(
        'poly2',
        type = poly_type,
    )
    args = parser.parse_args(argv)
    run(args.display_size, args.framerate, args.background, args.poly1, args.poly2)

if __name__ == '__main__':
    main()
