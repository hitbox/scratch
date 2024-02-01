import argparse

import pygamelib

from pygamelib import pygame

# 2024-02-01
# - giant function was in wireroute.py
# - tired of working around it
# - want to just save interesting configurations of rects in a file anyway
# - there should be a rect editor around here somewhere with snapping

def make_rects(frame, thickness, percent):
    # original below
    frame_quads = list(map(pygame.Rect, pygamelib.rectquadrants(frame)))
    rects = []
    # top left horizontal wall
    rects.append(
        pygame.Rect(frame.topleft, (frame.width * percent, thickness))
    )
    # top right horizontal wall
    rects.append(
        pygame.Rect(
            rects[-1].right + thickness,
            rects[-1].top,
            frame.right - rects[-1].right - thickness,
            thickness
        )
    )
    # left wall
    rects.append(
        pygame.Rect(
            frame.left,
            rects[0].bottom,
            thickness,
            frame.height - rects[0].height - thickness,
        )
    )
    # right wall
    rects.append(
        pygame.Rect(
            frame.right - thickness,
            rects[0].bottom,
            thickness,
            rects[2].height, # left wall height
        )
    )
    # top left inner box
    box = pygamelib.make_rect(
        size = pygame.Vector2(frame.size) * percent,
    )
    rects.append(
        pygame.Rect(
            pygamelib.make_rect(
                box,
                center = frame_quads[0].center,
            )
        )
    )
    # center inner box
    rects.append(
        pygame.Rect(
            pygamelib.make_rect(
                box,
                center = frame.center,
            )
        )
    )
    # right upper inner box
    rects.append(
        pygame.Rect(
            pygamelib.make_rect(
                box,
                center = frame_quads[2].center,
            )
        )
    )
    # center lower box
    rects.append(
        pygame.Rect(
            pygamelib.make_rect(
                box,
                center = (
                    frame.centerx,
                    frame.centery + frame.height * .25,
                )
            )
        )
    )
    # bottom left wall
    rects.append(
        pygame.Rect(
            pygamelib.make_rect(
                rects[1], # top right horizontal wall
                bottomleft = frame.bottomleft,
            )
        )
    )
    # bottom right wall
    rects.append(
        pygame.Rect(
            pygamelib.make_rect(
                rects[0], # top left horizontal wall
                bottomright = frame.bottomright,
            )
        )
    )
    return rects

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'size',
        type = pygamelib.sizetype()
    )
    parser.add_argument(
        '--thickness',
        type = int,
        default = 20,
    )
    parser.add_argument(
        '--percent',
        type = int,
        default = 20,
    )
    pygamelib.add_null_separator_flag(parser)
    pygamelib.add_rect_dimension_separator_option(parser)
    args = parser.parse_args(argv)

    null_separator = vars(args)['0']
    frame = pygame.Rect((0,)*2, args.size)
    rects = make_rects(frame, args.thickness, args.percent / 100)

    rect_string = pygamelib.format_pipe(map(tuple, rects), null_separator, args.dimsep)
    pygamelib.print_pipe(rect_string, null_separator)

if __name__ == '__main__':
    main()
