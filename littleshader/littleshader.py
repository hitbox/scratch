import argparse
import contextlib
import math
import os
import random
import string
import time

from collections import deque
from decimal import Decimal
from itertools import groupby
from itertools import product

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

MATH_CONTEXT = {k: getattr(math, k) for k in dir(math) if not k.startswith('_')}
BASE_CONTEXT = dict(
    Decimal = Decimal,
    random = random.random,
    **MATH_CONTEXT
)

EXAMPLES = [
    'sin(y/8+t)',
    #'sin(t - dist(graph_center, (x,y)))',
    'sin(t-sqrt(x*x+y*y))',
    'sin(t)',
    'sin(t+i)',
]

def post_quit():
    pygame.event.post(pygame.event.Event(pygame.QUIT))

def get_font(size, *sysfonts, fallback=None):
    for font in sysfonts:
        try:
            return pygame.font.SysFont(font, size)
        except FileNotFoundError:
            continue
    return pygame.fon.SysFont(fallback, size)

def lerp(a, b, t):
    return a * (1 - t) + b * t

def invlerp(a, b, x):
    return (x - a) / (b - a)

def remap(a, b, c, d, x):
    return x * (d-c) / (b-a) + c-a * (d-c) / (b-a)
    return lerp(c, d, invlerp(a, b, x))

def calc(expr, i, t, x, y, **extra_context):
    context = dict(
        x = x,
        y = y,
        i = i,
        t = t,
        **BASE_CONTEXT,
        **extra_context,
    )
    return eval(expr, context)

def loop(
    expression_list,
    size = None,
    color1 = (2*255/3,)*3,
    color2 = (2*255/3, 255/3, 255/3),
    export_frames_path = None,
):
    if size is None:
        size = (1024,)*2
    window = pygame.display.set_mode(size)
    frame = window.get_rect()
    graph = frame.inflate(-frame.width/3, -frame.height/3)

    # step such that there are 20 positions for circles across the graph
    step = int(min(graph.size) / 20)
    # ranges of each dimension of the graph
    ranges = map(lambda d: range(0, d, step), graph.size)
    # all the (x,y) pairs we care about
    circle_positions = list(product(*ranges))
    extra_context = dict(
        step = step,
        # the expressions are in cartesiann space, therefore can't use
        # graph.center it's in screen space
        graph_center = (graph.width / 2, graph.height / 2),
    )

    gui_frame = frame.inflate(-step*2,-step*2)
    pygame.font.init()
    # NOTE: untested for windows
    # https://support.microsoft.com/en-us/topic/microsoft-supplied-monospaced-truetype-fonts-93aa7a47-2149-be09-31a9-c22df598c952
    gui_font = get_font(min(size) // 32, 'DejaVuSansMono', 'Courier New')
    clock = pygame.time.Clock()

    key_stack = deque(maxlen=min(size)//10)
    display_key_stack = (
        pygame.K_ESCAPE,
        pygame.K_LEFT,
        pygame.K_RIGHT,
        pygame.K_DELETE,
        pygame.K_BACKSPACE,
        pygame.K_RETURN,
    )

    new_expression_allowed = string.ascii_letters + string.punctuation + string.digits
    new_expression = ''
    new_expression_placeholder = '(new expression)'
    new_expression_flash = ''

    expression_index = 0
    expression = expression_list[expression_index]
    last_good_expression = expression

    frame_index = 0
    start = time.time()
    running = True
    while running:
        clock.tick()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # keystrokes
                if event.key in display_key_stack:
                    keyname = pygame.key.name(event.key)
                    key_stack.appendleft(keyname)

                if event.key == pygame.K_ESCAPE:
                    post_quit()
                elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    if expression_list:
                        di = -1 if event.key == pygame.K_LEFT else 1
                        expression_index = (expression_index + di) % len(expression_list)
                        expression = expression_list[expression_index]
                        new_expression = ''
                elif event.key == pygame.K_DELETE:
                    # delete current expression
                    if expression in expression_list:
                        expression_list.remove(expression)
                        expression = ''
                    if expression_list:
                        expression_index = (expression_index - 1) % len(expression_list)
                        expression = expression_list[expression_index]
                elif event.key == pygame.K_BACKSPACE:
                    new_expression = new_expression[:-1]
                elif event.key == pygame.K_RETURN:
                    # try to commit new expression
                    if new_expression not in expression_list:
                        try:
                            calc(new_expression, 0, t, 0, 0, **extra_context)
                        except:
                            key_stack.appendleft(f'Invalid: {new_expression}')
                        else:
                            expression_list.append(new_expression)
                            key_stack.appendleft(new_expression)
                    if new_expression in expression_list:
                        expression_index = expression_list.index(new_expression)
                        expression = expression_list[expression_index]
                        new_expression = ''
                elif event.unicode in new_expression_allowed:
                    new_expression += event.unicode
        # draw circles
        t = time.time() - start
        window.fill((255/16, 255/16, 255/16))
        if expression:
            for i, (x, y) in enumerate(circle_positions):
                radius = calc(expression, i, t, x, y, **extra_context)
                radius = remap(-1, 1, -step/2, step/2, radius)
                color = color1 if radius < 0 else color2
                pos = (graph.x + x, graph.y + y)
                pygame.draw.circle(window, color, pos, abs(radius))
        # draw the current expression
        expr_image = gui_font.render(expression, True, color2)
        expr_rect = expr_image.get_rect(midbottom=gui_frame.midbottom)
        window.blit(expr_image, expr_rect)
        # draw fps
        fps_image = gui_font.render(f'{clock.get_fps():.2f}', True, color1)
        fps_rect = fps_image.get_rect(
            topleft = gui_frame.topleft,
        )
        window.blit(fps_image, fps_rect)
        # draw new expression or placeholder
        new_expr_image = gui_font.render(
            new_expression or new_expression_placeholder,
            True,
            color1)
        new_expr_rect = new_expr_image.get_rect(midtop=gui_frame.midtop)
        window.blit(new_expr_image, new_expr_rect)
        # draw key strokes
        key_groups = [(key, list(group)) for key, group in groupby(key_stack)]
        key_strings = [
            f'{key}({len(group)})' if len(group) > 1 else key
            for key, group in key_groups
        ]
        keyname_images = [gui_font.render(keyname, True, color2) for keyname in key_strings]
        keyname_rects = [image.get_rect() for image in keyname_images]
        if keyname_rects:
            keyname_rects[0].bottomleft = gui_frame.bottomleft
            for r1, r2 in zip(keyname_rects[:-1], keyname_rects[1:]):
                r2.bottomleft = r1.topleft
            for image, rect in zip(keyname_images, keyname_rects):
                window.blit(image, rect)
        # export frames
        if export_frames_path:
            frame_path = export_frames_path % (frame_index, )
            pygame.image.save(window, frame_path)
            frame_index += 1
        # update display
        pygame.display.update()

def sizetype(string):
    return tuple(map(int, string.replace(',', ' ').split()))

def main(argv=None):
    """
    """
    # https://tixy.land/
    parser = argparse.ArgumentParser(
        description = main.__doc__,
    )
    parser.add_argument('--expr', help='Expression to render.')
    parser.add_argument('--export')
    parser.add_argument('--size', type=sizetype)
    args = parser.parse_args(argv)

    expressions = [args.expr] if args.expr else EXAMPLES
    loop(
        expressions,
        export_frames_path = args.export,
        size = args.size,
    )

if __name__ == '__main__':
    main()
