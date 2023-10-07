import argparse
import os
import pickle

from itertools import combinations
from itertools import cycle
from types import SimpleNamespace

import lib.event
import rectop

from lib.external import pygame
from tools import CutRectTool
from tools import DefragRectTool
from tools import DeleteTool
from tools import IntersetRectTool
from tools import NewRectTool
from tools import SelectTool
from tools import SubdivideTool

BACKGROUND_COLOR = (0,)*3
SAVE_FILENAME = 'save.pickle'

g = SimpleNamespace(
    running = False,
    window = None,
    frame = None,

    rects = None,
    tool = None,
    highlight = None,

    entities = set(),
)

rects_getter = lambda: g.rects

tools = cycle([
    DefragRectTool(
        rects_getter = rects_getter,
    ),
    NewRectTool(
        new_rect_callback = lambda rect: g.rects.append(rect),
    ),
    SubdivideTool(
        rects_getter = rects_getter,
    ),
    #IntersetRectTool(
    #    rects_getter = rects_getter,
    #    new_rect_callback = lambda rect: g.rects.append(rect),
    #),
    DeleteTool(
        rects_getter = rects_getter,
    ),
    #SelectTool(
    #    rects_getter = rects_getter,
    #    selected_callback = lambda rect: g.highlight.update({id(rect): rect}),
    #    unselected_callback = lambda rect: g.highlight.pop(id(rect), None),
    #),
    CutRectTool(
        rects_getter = rects_getter,
    ),
])

@lib.event.listen_for(pygame.QUIT)
def on_quit(event):
    """
    On quit.
    """
    g.running = False

@lib.event.listen_for(pygame.KEYDOWN)
def on_keydown(event):
    """
    On key down.
    """
    if event.key in (pygame.K_ESCAPE, pygame.K_q):
        pygame.event.post(pygame.event.Event(pygame.QUIT))
    elif event.key == pygame.K_SPACE:
        next_tool()
    elif event.key == pygame.K_s:
        save(SAVE_FILENAME)

@lib.event.listen_for(lib.event.ANYEVENT)
def on_anyevent(event):
    """
    On any event give current tool a change to respond to the event.
    """
    if g.tool:
        g.tool.on_event(event)

def get_border_color(rect):
    """
    """
    # default
    color = (175,)*3
    if id(rect) in g.highlight:
        color = (200,10,10)
    elif hasattr(g.tool, 'hover'):
        # trying to handle both hover = set(...) or hover = id(rect)
        if (
            (isinstance(g.tool.hover, int) and id(rect) == g.tool.hover)
            or
            (isinstance(g.tool.hover, set) and id(rect) in g.tool.hover)
        ):
            color = (200,200,30)
    return color

def get_fill_color(rect):
    """
    """
    # default
    color = BACKGROUND_COLOR
    if hasattr(g.tool, 'hover'):
        # trying to handle both hover = set(...) or hover = id(rect)
        if (
            (isinstance(g.tool.hover, int) and id(rect) == g.tool.hover)
            or
            (isinstance(g.tool.hover, set) and id(rect) in g.tool.hover)
        ):
            color = (200,30,200)
    return color

def draw_rects():
    for rect in g.rects:
        background_color = get_fill_color(rect)
        pygame.draw.rect(g.window, background_color, rect)
        border_color = get_border_color(rect)
        pygame.draw.rect(g.window, border_color, rect, 1)

def draw_intersections():
    for r1, r2 in combinations(g.rects, 2):
        if r1.colliderect(r2):
            #points = rectop.get.intersection_points(r1, r2)
            #for p in points:
            #    pygame.draw.circle(g.window, (200,30,200), p, 10)

            intersectrect = rectop.get.intersection(r1, r2)
            pygame.draw.rect(g.window, (200,30,200), intersectrect, 1)

def draw_selection():
    if hasattr(g.tool, 'selection') and isinstance(g.tool.selection, pygame.Rect):
        pygame.draw.rect(g.window, (200,30,10), g.tool.selection, 1)

def draw_tool_name():
    txtimg = g.font.render(str(g.tool), True, (200,)*3)
    g.window.blit(txtimg, txtimg.get_rect(bottomright=g.frame.bottomright))

def draw():
    """
    Draw everything
    """
    g.window.fill(BACKGROUND_COLOR)
    draw_rects()
    #draw_intersections()
    draw_selection()
    draw_tool_name()
    pygame.display.flip()

def next_tool():
    """
    Cycle to next rect tool.
    """
    g.tool = next(tools)
    g.tool.reset()

def loop():
    while g.running:
        for event in pygame.event.get():
            lib.event.dispatch(event)
            lib.event.for_drag(event)
        draw()

def save(filename):
    """
    """
    with open(filename, 'wb') as fp:
        pickle.dump({'rects': g.rects}, fp)

def restore(filename):
    """
    """
    if os.path.exists(filename):
        with open(filename, 'rb') as fp:
            data = pickle.load(fp)
            for key, value in data.items():
                setattr(g, key, value)

def main():
    pygame.font.init()
    g.font = pygame.font.Font(None, 24)
    g.window = pygame.display.set_mode((800,600))
    g.frame = g.window.get_rect()
    g.rects = []
    g.highlight = set()
    g.running = True
    next_tool()

    restore(SAVE_FILENAME)
    loop()

def cli(argv=None):
    """
    """
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)
    main()

if __name__ == '__main__':
    cli()
