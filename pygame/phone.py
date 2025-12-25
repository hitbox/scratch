import argparse
import contextlib
import math
import os
import random
import string
import subprocess

from itertools import pairwise
from itertools import tee
from operator import attrgetter

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

import numpy as np
import cv2

extents = attrgetter('left', 'top', 'right', 'bottom')

def video_to_surfaces(path, width, height):
    cmd = [
        'ffmpeg',
        '-i', path,
        '-loglevel', 'error',
        '-vf', f'scale={width}:{height}',
        '-pix_fmt', 'rgb24',
        '-f', 'rawvideo',
        '-',
    ]

    try:
        pipe = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=10**8,
        )

        frame_size = width * height * 3
        while raw := pipe.stdout.read(frame_size):
            if len(raw) != frame_size:
                break

            frame = np.frombuffer(raw, dtype=np.uint8)
            frame = frame.reshape((height, width, 3))

            surf = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
            yield surf
    finally:
        pipe.terminate()

def rsetattr(obj, dotted, value):
    all_names = dotted.split('.')
    before_attr = all_names[:-1]
    while before_attr:
        attr = before_attr.pop(0)
        obj = getattr(obj, attr)
    return setattr(obj, all_names[-1], value)

class PairwiseSetter:

    def __init__(self, set_attr, get_attr):
        self.get_attr = get_attr
        self.set_attr = set_attr

    def __call__(self, items):
        for item1, item2 in pairwise(items):
            setattr(item2, self.set_attr, getattr(item1, self.get_attr))


class FontRenderer:

    def __init__(self, font, color='ghostwhite', antialias=True):
        self.font = font
        self.color = color
        self.antialias = antialias

    def __getattr__(self, name):
        return getattr(self.font, name)

    def render(self, text):
        return self.font.render(text, self.antialias, self.color)


class Anchor:

    def __init__(self, getobj, setobj, set_attr, get_attr):
        self.getobj = getobj
        self.setobj = setobj
        self.set_attr = set_attr
        self.get_attr = attrgetter(get_attr)

    def __call__(self):
        value = self.get_attr(self.getobj)
        rsetattr(self.setobj, self.set_attr, value)


class Timer:

    def __init__(self, duration):
        """
        :param duration: integer milliseconds
        """
        self.duration = self.original_duration = duration

    def __bool__(self):
        return self.duration > 0

    def time(self):
        return 1 - self.duration / self.original_duration

    def update(self, elapsed):
        t = self.duration - elapsed
        self.duration = max(t, 0)


class RectMaker(pygame.Rect):

    def __init__(self, minimum=None, class_=pygame.Rect):
        self.minimum = minimum
        self.class_ = class_

    def __call__(self, *rectargs):
        r = self.class_(*rectargs)
        for key in dir(r):
            if key in self.minimum:
                if getattr(r, key) < self.minimum[key]:
                    setattr(r, key, self.minimum[key])
        return r


class Animation:

    def __init__(self, timer, origin, destination, lerp, ease=None):
        self.timer = timer
        self.origin = origin
        self.destination = destination
        self.current = self.origin
        self.lerp = lerp
        self.ease = ease

    def __bool__(self):
        return bool(self.timer)

    def update(self, elapsed):
        self.timer.update(elapsed)
        t = self.timer.time()
        if self.ease:
            t = self.ease(t)
        self.current = self.lerp(self.origin, self.destination, t)


class MessageList:

    def __init__(self, font, color, group_align=None, rect=None, rect_maker=None, anim_duration=400):
        self.font = font
        self.color = color
        self.group_align = group_align
        self.items = []

        if rect_maker is None:
            rect_maker = pygame.Rect
        self.rect_maker = rect_maker
        self.anim_duration = anim_duration
        self.pending = None
        self.target_rect = pygame.Rect(0, 0, 0, 0)
        if rect is None:
            rect = pygame.Rect(0, 0, 0, 0)
        self.rect = rect
        self.animation = None

    def add_message(self, text_image):
        if not self.animation:
            last = self.rect
            if self.items:
                last = self.items[-1][1]
            text_rect = text_image.get_rect(topleft=last.bottomleft)
            self.pending = (text_image, text_rect)
            self.animation = Animation(
                timer = Timer(self.anim_duration),
                origin = self.rect,
                destination = self.rect_maker(get_bounding([self.rect, text_rect])),
                lerp = lerp_containers,
                ease = ease_out_bounce,
            )

    def update(self, elapsed):
        if self.animation:
            self.animation.update(elapsed)
            t = self.animation.timer.time()
            if t == 1:
                # Animation is finished.
                self.items.append(self.pending)
                rects = [rect for image, rect in self.items]
                if self.group_align:
                    self.group_align(rects)
                self.rect = self.rect_maker(get_bounding(rects))
            else:
                self.rect = self.animation.current

    def draw(self, surface, camera):
        offset = -pygame.Vector2(tuple(camera[:2]))
        for image, rect in self.items:
            surface.blit(image, rect.move(offset))

        if self.rect:
            pygame.draw.rect(surface, self.color, self.rect.move(offset), 1)


class Sigmoid:

    def __init__(self, center=0.5, k=10):
        self.center = center
        self.k = k

    def formula(self):
        return f'sigmoid(center={self.center:.2f}, k={self.k})'

    def __str__(self):
        return self.formula()

    def __call__(self, t):
        return 1 / (1 + math.exp(-self.k * (t - self.center)))


class BouncySigmoid(Sigmoid):

    def __init__(self, center=0.5, k=10, bounces=3, decay=8):
        self.center = center
        self.k = k
        self.bounces = bounces
        self.decay = decay

    def __call__(self, t):
        base = super().__call__(t)

        bounce = math.sin(self.bounces * math.pi * t) * math.exp(-self.decay * t)

        return base + bounce * (1 - base)


class InputBox:

    def __init__(self, font, rect, align=None, text=None):
        self.font = font
        self.rect = rect
        self.align = align
        if text is None:
            text = ''
        self.text = text

    def reset(self):
        self.text = ''

    def on_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode

    def get_message(self):
        return self.font.render(self.text)

    def update(self, elapsed):
        if self.align:
            self.align()

    def draw(self, surface, camera):
        offset = -pygame.Vector2(tuple(camera[:2]))
        pygame.draw.rect(surface, 'ghostwhite', self.rect.move(offset), 1)
        image = self.font.render(self.text)
        surface.blit(image, self.rect.move(offset))


class AutoInputBox(InputBox):

    def __init__(self, root, font, rect, align=None, text=None):
        self.font = font
        self.root = root
        self.rect = rect
        self.align = align
        if text is None:
            text = ''
        self.text = text

    def get_message(self):
        text_image = super().get_message()
        paths = os.listdir(self.root)
        while True:
            path = os.path.join(self.root, random.choice(paths))
            print(path)
            index = random.randint(0, 2000)
            for framei, frame in enumerate(video_to_surfaces(path, 150, 150)):
                if framei == index:
                    break
            else:
                # Try another path
                continue
            break
        # Video frame under text message image.
        frame_rect = frame.get_rect()
        text_rect = text_image.get_rect(topleft=frame_rect.bottomleft)
        rects = [text_rect, frame_rect]
        total_rect = pygame.Rect(get_bounding(rects))
        total_surf = pygame.Surface(total_rect.size)
        total_surf.blit(text_image, text_rect)
        total_surf.blit(frame, frame_rect)
        return total_surf


class MessageInput:

    def __init__(self, message_list, input_box):
        self.message_list = message_list
        self.input_box = input_box

    def on_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.message_list.add_message(self.input_box.get_message())
                self.input_box.reset()
            else:
                self.input_box.on_event(event)

    def update(self, elapsed):
        self.message_list.update(elapsed)
        self.input_box.update(elapsed)

    def draw(self, surface, camera):
        self.message_list.draw(surface, camera)
        self.input_box.draw(surface, camera)


def make_rect(**kwargs):
    r = pygame.Rect(0, 0, 0, 0)
    for key, value in kwargs.items():
        setattr(r, key, value)
    return r

def lerp_scalar(a, b, t):
    return a + (b - a) * t

def lerp_containers(a, b, t):
    class_ = type(a)
    return class_(*(lerp_scalar(aa, bb, t) for aa, bb in zip(a, b)))

def get_bounding(rects):
    lefts, tops, rights, bottoms = zip(*map(extents, rects))
    left = min(lefts)
    top = min(tops)
    right = max(rights)
    bottom = max(bottoms)
    return (left, top, right - left, bottom - top)

def update_kwargs(obj, **kwargs):
    for key, value in kwargs.items():
        setattr(obj, key, value)

def move_group(rects, **kwargs):
    origin = pygame.Rect(get_bounding(rects))
    dest = origin.copy()
    update_kwargs(dest, **kwargs)
    dx = dest.x - origin.x
    dy = dest.y - origin.y
    for rect in rects:
        rect.x += dx
        rect.y += dy

standard_sigmoid = Sigmoid()
ease_out_bounce = BouncySigmoid(decay=2)
align_top_to_bottom = PairwiseSetter(set_attr='topleft', get_attr='bottomleft')
align_left_to_right = PairwiseSetter(set_attr='left', get_attr='right')

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'path',
    )
    args = parser.parse_args(argv)

    SCREEN = pygame.Rect(0, 0, 360, 640)
    WINDOW = pygame.Rect(0, 0, 360*1.5, 640*1.5)

    screen = pygame.Surface(SCREEN.size)
    window_surf = pygame.display.set_mode(WINDOW.size)
    clock = pygame.time.Clock()
    framerate = 60
    pygame.font.init()
    font = FontRenderer(pygame.font.SysFont(None, 24))

    text_height = font.size(string.ascii_uppercase)[1]
    rect_maker = RectMaker(
        minimum = {
            'x': 0,
            'width': 300,
            'height': text_height,
        },
    )

    message_list = MessageList(
        font,
        color = 'red',
        rect = make_rect(size=(300, text_height), centerx=SCREEN.centerx),
        group_align = align_top_to_bottom,
        rect_maker = rect_maker,
    )

    input_box = InputBox(font, pygame.Rect(0, 0, 200, text_height))
    message_input = MessageInput(message_list, input_box)

    # Camera as rect for ease of alignment.
    camera = SCREEN.copy()

    anchors = [
        Anchor(
            getobj = SCREEN,
            get_attr = 'centerx',
            setobj = message_list,
            set_attr = 'rect.centerx',
        ),
        Anchor(
            getobj = message_list,
            get_attr = 'rect.bottomright',
            setobj = input_box,
            set_attr = 'rect.topright',
        ),
        #Anchor(
        #    getobj = input_box,
        #    get_attr = 'rect.bottom',
        #    setobj = camera,
        #    set_attr = 'bottom',
        #),
    ]

    focused = message_input
    running = True
    while running:
        elapsed = clock.tick(framerate)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                focused.on_event(event)

        message_input.update(elapsed)
        for anchor in anchors:
            anchor()

        if input_box.rect.bottom > camera.bottom:
            #camera.bottom = input_box.rect.bottom
            pass

        screen.fill('gray5')
        message_input.draw(screen, camera)
        pygame.transform.scale(screen, WINDOW.size, window_surf)
        pygame.display.update()

if __name__ == '__main__':
    main()
