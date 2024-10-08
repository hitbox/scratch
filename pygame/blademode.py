import abc
import collections
import contextvars
import enum
import itertools as it
import math
import random

import pygamelib

from pygamelib import pygame

engine_var = contextvars.ContextVar('engine')

class Orientation(enum.Enum):

    COLLINEAR = 0
    CLOCKWISE = 1
    ANTICLOCKWISE = 2


class Engine:

    def __init__(self, clock=None):
        if clock is None:
            clock = pygame.time.Clock()
        self.clock = clock
        self.running = False
        self.state = None

    def run(self, state=None):
        self.state = state or self.state
        elapsed = 0
        self.running = True
        while self.running:
            self.state.update(elapsed)
            elapsed = self.clock.tick()

    def stop(self):
        self.running = False


class BaseState(abc.ABC):

    @abc.abstractmethod
    def update(self, elapsed):
        pass


class Timer:

    def __init__(self, duration, callback=None, autostart=False, once=False):
        self.duration = duration
        self.callback = callback
        self.once = once
        self.countdown = 0
        if autostart:
            self.start()

    def start(self):
        self.countdown = self.duration

    def update(self, elapsed):
        if self.countdown > 0:
            newcountdown = self.countdown - elapsed
            if newcountdown < 1 and self.callback:
                self.callback()
            self.countdown = newcountdown


class TimerManager:

    def __init__(self, timers=None):
        if not timers:
            timers = []
        self.timers = timers
        self._remove = []

    def append(self, timer):
        self.timers.append(timer)

    def remove(self, timer):
        self._remove.append(timer)

    def update(self, elapsed):
        # remove timers from queue
        while self._remove:
            timer = self._remove.pop()
            self.timers.remove(timer)

        for timer in self.timers:
            timer.update(elapsed)
            if timer.countdown <= 0 and timer.once:
                self.remove(timer)


class DemoTimers(BaseState):

    def __init__(self, timer_manager):
        self.timer_manager = timer_manager

    def update(self, elapsed):
        self.timer_manager.update(elapsed)


class Slicing:

    def __init__(self, max_angle_change=math.pi):
        self.max_angle_change = max_angle_change
        self.points = []

    def __bool__(self):
        return bool(self.points)

    def __iter__(self):
        return iter(self.points)

    def __len__(self):
        return len(self.points)

    def test_append(self, point):
        if not self.points:
            return True

        prev_point = self.points[-1]
        dy = prev_point[1] - point[1]
        dx = prev_point[0] - point[0]
        angle = math.atan2(dy, dx)

        return abs(angle) < self.max_angle_change

    def append(self, point):
        self.points.append(point)

    def clear(self):
        self.points.clear()

    def copy(self):
        slicing = Slicing()
        slicing.points = self.points.copy()
        return slicing

    def draw(self, surf):
        if len(self.points) > 1:
            pygame.draw.lines(surf, 'grey10', False, self.points)
            for point in self.points:
                pygame.draw.circle(surf, 'grey20', point, 4)


class SuccessManager:
    """
    Manage a list of success objects.
    """

    def __init__(self):
        self.successes = []

    def append(self, success):
        self.successes.append(success)

    def update(self, elapsed):
        self.successes = [s for s in self.successes if s.countdown > 0]
        for success in self.successes:
            success.update(elapsed)

    def draw(self, surf):
        for success in self.successes:
            for rect in success.tatami_omote_list:
                pygame.draw.rect(surf, 'brown', rect, 1)
            pygame.draw.lines(surf, 'grey15', False, success.slicing.points)


class Success:
    """
    Capture a successful slice through tatami omote rects.
    """

    def __init__(self, tatami_omote_list, slicing, countdown):
        self.tatami_omote_list = tatami_omote_list
        self.slicing = slicing
        self.countdown = countdown

    def update(self, elapsed):
        self.countdown -= elapsed
        for rect in self.tatami_omote_list:
            rect.update(rect.x, rect.y+1, rect.width, rect.height)
        self.slicing.points = [(px, py-1) for px, py in self.slicing.points]


class TatamiOmoteManager:

    def __init__(
        self,
        font,
        min_endpoint_distance = 200,
        max_endpoint_distance = 300,
    ):
        self.font = font
        self.min_endpoint_distance = min_endpoint_distance
        self.max_endpoint_distance = max_endpoint_distance
        self.rects = []

    def __bool__(self):
        return bool(self.rects)

    def clear(self):
        self.rects.clear()

    def draw(self, surf):
        for order, rect in enumerate(self.rects, start=1):
            pygame.draw.rect(surf, 'orange', rect, 1)
            image = self.font.render(str(order), True, 'azure')
            surf.blit(image, image.get_rect(center=rect.center))

    def valid_distance(self, p1, p2):
        distance = math.dist(p1, p2)
        return self.min_endpoint_distance < distance < self.max_endpoint_distance

    def spawn(self, inside):
        tatami_width = 50
        tatami_height = 50

        # find two points within the constraints
        while True:
            x1, y1 = random_point(inside)
            x3, y3 = random_point(inside)
            if self.valid_distance((x1, y1), (x3, y3)):
                break

        # midpoint between p1 and p3
        x2, y2 = midpoint((x1, y1), (x3, y3))

        self.rects.extend([
            pygame.Rect(x1, y1, tatami_width, tatami_height),
            pygame.Rect(x2, y2, tatami_width, tatami_height),
            pygame.Rect(x3, y3, tatami_width, tatami_height),
        ])

    def test_slice(self, slice_points):

        return test_blade_slice(self.rects, slice_points)

        # the slice lines go throught the tatami omote in order
        #slice_lines = it.pairwise(slice_points)
        sliced_order = []
        for rect in self.rects:
            for slice_line in it.pairwise(slice_points):
                rect_as_line = (rect.bottomleft, rect.topright)
                if is_line_intersecting_rect(slice_line, rect_as_line):
                    # break to test next rect
                    sliced_order.append(rect)
                    break
            else:
                # one rect not sliced, fail
                return False
        return sliced_order == self.rects


class Animation:

    def __init__(self, a, b, duration):
        self.a = a
        self.b = b
        self.duration = duration
        self.time = 0

    def update(self, elapsed):
        if self.time == self.duration:
            return

        if self.time + elapsed >= self.duration:
            self.time = self.duration
        else:
            self.time += elapsed

    def value(self):
        norm_time = pygamelib.remap(self.time, 0, self.duration, 0, 1)
        value = pygamelib.lerp(norm_time, self.a, self.b)
        return value


class BladeMode:

    def __init__(self):
        self.font = pygamelib.monospace_font(24)
        self.printer = pygamelib.FontPrinter(self.font, 'azure')
        self.screen = pygame.display.get_surface()
        self.rect = pygame.Rect(100, 300, 300, 300)
        self.animation = Animation(
            pygame.Vector2(self.rect.center),
            pygame.Vector2(self.rect.move(300, 0).center),
            1000
        )
        self.events = []

    def draw(self):
        self.screen.fill('black')
        pygame.draw.rect(self.screen, 'azure', self.rect)
        lines = [f'{self.rect}']
        image = self.printer(lines)
        self.screen.blit(image, (0,0))
        pygame.display.flip()

    def update(self, elapsed):
        self.events = pygame.event.get()
        for event in self.events:
            if event.type == pygame.QUIT:
                engine = engine_var.get()
                engine.stop()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
        self.animation.update(elapsed)
        self.rect.center = self.animation.value()
        self.draw()


def on_segment(p, q, r):
    """
    Check if point q lies on the line segment pr.

    Args:
    p (tuple): The first endpoint of the line segment, represented as a tuple (x, y).
    q (tuple): The point to check, represented as a tuple (x, y).
    r (tuple): The second endpoint of the line segment, represented as a tuple (x, y).

    Returns:
    bool: True if point q lies on the line segment pr, False otherwise.
    """
    return (
            q[0] <= max(p[0], r[0])
        and q[0] >= min(p[0], r[0])
        and q[1] <= max(p[1], r[1])
        and q[1] >= min(p[1], r[1])
    )

def orientation(p, q, r):
    """
    Determine the orientation of the triplet (p, q, r).

    The function returns:
    0 : Collinear points
    1 : Clockwise points
    2 : Counterclockwise points

    Args:
    p (tuple): The first point, represented as a tuple (x, y).
    q (tuple): The second point, represented as a tuple (x, y).
    r (tuple): The third point, represented as a tuple (x, y).

    Returns:
    int: The orientation of the triplet (p, q, r) as follows:
         0 -> p, q, and r are collinear
         1 -> Clockwise
         2 -> Counterclockwise
    """
    val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])

    if val > 0:
        val = 1
    elif val < 0:
        val = 2

    return val

def do_intersect(p1, q1, p2, q2):
    """
    Determine if the line segments p1q1 and p2q2 intersect.

    Args:
    p1 (tuple): The first endpoint of the first line segment, represented as a tuple (x, y).
    q1 (tuple): The second endpoint of the first line segment, represented as a tuple (x, y).
    p2 (tuple): The first endpoint of the second line segment, represented as a tuple (x, y).
    q2 (tuple): The second endpoint of the second line segment, represented as a tuple (x, y).

    Returns:
    bool: True if the line segments p1q1 and p2q2 intersect, False otherwise.
    """
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    # General case: line segments intersect if orientations are different
    if o1 != o2 and o3 != o4:
        return True

    # Special cases: check if the points are collinear and lie on the segment
    if o1 == 0 and on_segment(p1, p2, q1):
        return True
    if o2 == 0 and on_segment(p1, q2, q1):
        return True
    if o3 == 0 and on_segment(p2, p1, q2):
        return True
    if o4 == 0 and on_segment(p2, q1, q2):
        return True

    return False

def is_line_intersecting_rect(line, rect):
    """
    Determine if a line intersects a rectangle.

    :param line:
        A tuple containing two points that define the line, each represented as
        a tuple (x, y).
    :param rect:
        A tuple containing two points that define the rectangle:
        the bottom-left corner and the top-right corner, each represented as a
        tuple (x, y).

    Returns:
    bool: True if the line intersects the rectangle, False otherwise.
    """
    (x1, y1), (x2, y2) = line
    (rx1, ry1), (rx2, ry2) = rect

    rect_points = [
        (rx1, ry1),
        (rx1, ry2),
        (rx2, ry2),
        (rx2, ry1),
    ]

    # Check if the line intersects any of the four sides of the rectangle
    for i in range(4):
        if do_intersect(line[0], line[1], rect_points[i], rect_points[(i + 1) % 4]):
            return True

    return False

def midpoint(p1, p2):
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

def wrap_points(points):
    xs, ys = zip(*points)
    left = min(xs)
    top = min(ys)
    right = max(xs)
    bottom = max(ys)
    return (left, top, right - left, bottom - top)

def random_point(rect):
    x = random.randint(rect.left, rect.right)
    y = random.randint(rect.top, rect.bottom)
    return (x, y)

def test_blade_slice(tatami_omote_rects, slice_points):
    """
    Test that the points of a slice line collide each rect, in order.
    """
    # copy for stacks
    rects = collections.deque(tatami_omote_rects)
    slice_lines = collections.deque(it.pairwise(slice_points))

    # popleft slice_line and rect
    # line hits rect, yield line and rect, put line back in stack and leave rect off
    # line does not hit rect, continue to next line
    while slice_lines and rects:
        rect = rects.popleft()
        slice_line = slice_lines.popleft()
        is_intersecting = is_line_intersecting_rect(
            slice_line,
            (rect.bottomleft, rect.topright)
        )
        if is_intersecting:
            # keep line, lose rect
            slice_lines.appendleft(slice_line)
        else:
            # keep rect and test next line
            rects.appendleft(rect)

    # success for no remaining rects
    return not bool(rects)

def render_font_lines(font, color, lines, antialias=True):
    for line in lines:
        yield font.render(line, antialias, color)

def align_top_bottom(rects):
    for r1, r2 in it.pairwise(rects):
        r2.top = r1.bottom

def main(argv=None):
    """
    Simplified Metal Gear Rising blade mode toy.
    """
    # aka: tameshigiri
    parser = pygamelib.command_line_parser()
    args = parser.parse_args(argv)
    blade_mode_unlimited_framerate(args.display_size)

def timer_demo():
    # thinking of having a timer driven state
    # with cool slow down effects
    # also to capture the mouse position at a known rate
    # so that we can estimate how well the player did
    clock = pygame.time.Clock()
    engine = Engine(clock)

    timer_manager = TimerManager()

    def start_others():
        for timer in others:
            timer_manager.append(timer)
            timer.start()
        print('start_others')

    start_all_timer = Timer(
        duration = 1000,
        callback = start_others,
        autostart = True,
        once = True,
    )

    timer_manager.append(start_all_timer)

    def stop_engine():
        print('1000')
        engine.stop()

    others = [
        Timer(duration=1000, callback=stop_engine),
        Timer(duration=500, once=True, callback=lambda: print('500')),
        Timer(duration=250, once=True, callback=lambda: print('250')),
    ]

    state = DemoTimers(timer_manager)

    engine.state = state
    engine.run()

def blade_mode(display_size):
    pygame.font.init()
    clock = pygame.time.Clock()
    framerate = 60
    screen = pygame.display.set_mode(display_size)
    background = screen.copy()
    window = screen.get_rect()
    font = pygame.font.SysFont(None, 50)
    printer = pygamelib.FontPrinter(font, color='azure')

    image = printer(['Click and drag through rects, in order'])
    background.blit(image, (0,0))

    spawn_rect = window.copy()
    spawn_rect.size = (300, 300)
    spawn_rect.center = window.center

    # hide mouse cursor
    pygame.mouse.set_visible(False)

    # objects to slice
    tatami_omote_manager = TatamiOmoteManager(
        font,
    )
    tatami_spawn_timer = 0

    elapsed = 0
    slicing = Slicing(
        max_angle_change = math.pi / 2
    )
    success_manager = SuccessManager()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()

        mouse_position = pygame.mouse.get_pos()
        mouse1, mouse2, mouse3 = pygame.mouse.get_pressed()

        success_manager.update(elapsed)

        if mouse1:
            slicing.append(mouse_position)
        elif slicing:
            # mouse1 up, end slicing
            slicing.clear()

        if (
            slicing
            and tatami_omote_manager.rects
            and len(slicing.points) > 1
            and tatami_omote_manager.test_slice(slicing.points)
        ):
            slice_success = Success(
                tatami_omote_list = [rect.copy() for rect in tatami_omote_manager.rects],
                slicing = slicing.copy(),
                countdown = 2000,
            )
            success_manager.append(slice_success)
            slicing.clear()
            tatami_omote_manager.clear()
            tatami_spawn_timer = 0

        if not tatami_omote_manager:
            tatami_spawn_timer += elapsed
            if tatami_spawn_timer >= 1000:
                tatami_omote_manager.spawn(spawn_rect)

        screen.blit(background, (0,0))
        success_manager.draw(screen)
        slicing.draw(screen)
        tatami_omote_manager.draw(screen)
        pygame.draw.circle(screen, 'azure', mouse_position, 2)
        pygame.display.flip()

        elapsed = clock.tick(framerate)

def blade_mode_unlimited_framerate(display_size):
    pygame.font.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(display_size)

    engine = Engine()
    engine_token = engine_var.set(engine)

    state = BladeMode()
    engine.run(state)

    engine_var.reset(engine_token)

if __name__ == '__main__':
    main()
