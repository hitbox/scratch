import argparse
import code
import io
import sys
import textwrap

from abc import ABC
from abc import abstractmethod
from itertools import tee

from lib.readline import Readline

STATEPOP = pygame.USEREVENT
STATEPUSH = STATEPOP + 1

class StateManagerError(Exception):
    pass


def pushstate(state):
    pygame.event.post(pygame.event.Event(STATEPUSH, state=state))

def popstate():
    pygame.event.post(pygame.event.Event(STATEPOP))

class BaseState(ABC):
    """
    A state the main loop is controlling.
    """

    @abstractmethod
    def enter(self, previous):
        "This state now has control."

    @abstractmethod
    def exit(self):
        "This state is losing control."

    @abstractmethod
    def on_event(self, event):
        "Handle event"

    @abstractmethod
    def update(self, elapsed_ms):
        "Update after event handling."


class InteractiveInterpreterState(
    code.InteractiveInterpreter,
    BaseState,
):

    def __init__(self, output, locals=None, filename='<console>'):
        super().__init__(locals)
        self.output = output
        self.filename = filename
        self.more = False
        self.line = None
        self.readline_state = None
        self.resetbuffer()
        try:
            sys.ps1
        except AttributeError:
            sys.ps1 = ">>> "
        try:
            sys.ps2
        except AttributeError:
            sys.ps2 = "... "

    def resetbuffer(self):
        self.buffer = []

    def make_banner(self, banner=None):
        cprt = 'Type "help", "copyright", "credits" or "license" for more information.'
        if banner is None:
            banner = ("Python %s on %s\n%s\n(%s)\n" %
                       (sys.version, sys.platform, cprt,
                        self.__class__.__name__))
        elif banner:
            banner = ("%s\n" % str(banner))
        return banner

    def enter(self, previous_state):
        if self.readline_state:
            self.line = self.readline_state.readline.get_line()
            self.readline_state = None

    def exit(self):
        pass

    def on_event(self, event):
        pass

    def update(self, elapsed_ms):
        if not self.readline_state:
            if not self.line:
                if self.more:
                    prompt = sys.ps2
                else:
                    prompt = sys.ps1
                self.raw_input(prompt)
            else:
                self.more = self.push(self.line)
                self.line = None

    def push(self, line):
        self.buffer.append(line)
        source = '\n'.join(self.buffer)
        more = self.runsource(source, self.filename)
        if not more:
            self.resetbuffer()
        return more

    def raw_input(self, prompt=""):
        self.readline_state = PygameReadlineState(prompt)
        pushstate(self.readline_state)

    def write(self, data):
        self.output.write(data)


class BaseRenderer(ABC):

    @abstractmethod
    def render(self):
        pass


class ReadlineRenderer(BaseRenderer):

    def __init__(self, font, color):
        self.font = font
        self.color = color

    def render(self, chars):
        rects = [pygame.Rect(0,0,0,0)]
        items = []
        for line in self.buffer.lines:
            image = self.font.render(line, self.antialias, self.color)
            rect = image.get_rect(left = rects[-1].right)
            items.append((image, rect))
        #
        wrap = wraprects(rect for image, rect in items)
        result = pygame.Surface(wrap.size, flags=pygame.SRCALPHA)
        for image, rect in items:
            result.blit(image, rect)
        return result


class PygameReadlineState(BaseState):
    """
    Read a line of input from keyboard
    """
    # holds the state of reading a line
    readline_class = Readline
    # readline state renderer
    renderer_class = ReadlineRenderer
    #
    movements = {
        pygame.K_BACKSPACE: 'backspace',
        pygame.K_DELETE: 'delete',
        pygame.K_LEFT: 'cursor_left',
        pygame.K_RIGHT: 'cursor_right',
        pygame.K_END: 'move_end',
        pygame.K_HOME: 'move_start',
    }

    def __init__(self, prompt=None, readline_class=None, renderer_class=None):
        self.prompt = prompt
        self.readline = readline_class or self.readline_class()
        self.renderer = renderer_class or self.renderer_class()
        self.movements = {keytype: getattr(self.readline, attr)
                          for keytype, attr in self.movements.items()}

    def enter(self, previous):
        "Silence enter"

    def exit(self):
        "Silence exit"

    def on_event(self, event):
        if event.type == pygame.KEYDOWN:
            self.on_keydown(event)

    def on_keydown(self, event):
        if event.key == pygame.K_RETURN:
            # pop ourself on RETURN
            popstate()
        elif event.key in self.movements:
            # movement keys
            func = self.movements[event.key]
            func()
        else:
            # consume character
            self.readline.putchar(event.unicode)

    def update(self, elapsed_ms):
        pass


class StateManager:

    def __init__(self, initial=None):
        self.stack = []
        self.pushing = None
        self.popping = None
        if initial:
            self.push(initial)

    def current(self):
        if self.stack:
            return self.stack[-1]

    def raise_for_pending(self):
        if self.pushing or self.popping:
            raise StateManagerError('Push or pop already pending')

    def pop(self):
        self.raise_for_pending()
        self.popping = True

    def push(self, state):
        self.raise_for_pending()
        self.pushing = state

    def update(self, elapsed_ms):
        "Do pending pushes and pops."
        if not (self.pushing or self.popping):
            return

        if self.pushing:
            if self.stack:
                previous = self.current()
            else:
                previous = None
            self.stack.append(self.pushing)
        elif self.popping:
            previous = self.stack.pop()

        current = self.current()
        current.enter(previous)
        self.popping = None
        self.pushing = None


class OutputBuffer:

    def __init__(self):
        self.lines = []

    def write(self, data):
        self.lines.append(data)


class OutputBufferRenderer(BaseRenderer):

    def __init__(self, font, buffer):
        self.font = font
        self.buffer = buffer
        self.antialias = True
        self.color = (200,200,200)

    def render(self):
        rects = [pygame.Rect(0,0,0,0)]
        items = []
        for line in self.buffer.lines:
            image = self.font.render(line, self.antialias, self.color)
            rect = image.get_rect(top = rects[-1].bottom)
            items.append((image, rect))
        #
        wrap = wraprects(rect for image, rect in items)
        result = pygame.Surface(wrap.size, flags=pygame.SRCALPHA)
        for image, rect in items:
            result.blit(image, rect)
        return result


def loop(**config):
    # config
    framerate = config.get('framerate')
    if framerate is None:
        framerate = 60
    screen_size = config.get('screen_size')
    if screen_size is None:
        screen_size = (800, 600)
    # outside loop init
    screen = pygame.display.set_mode(screen_size)
    background = screen.copy()
    window = screen.get_rect()
    clock = pygame.time.Clock()
    # font init
    pygame.font.init()
    # XXX: path
    font = pygame.font.Font('/usr/share/fonts/TTF/DejaVuSansMono.ttf', 24)
    antialias = True
    #
    buffer = OutputBuffer()
    initial_state = InteractiveInterpreterState(buffer)
    statemanager = StateManager(initial_state)
    output_renderer = OutputBufferRenderer(font, buffer)
    #
    running = True
    while running:
        # tick
        elapsed_ms = clock.tick(framerate)
        current = statemanager.current()
        # events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # state pop
            elif event.type == STATEPOP:
                statemanager.pop()
            # state push
            elif event.type == STATEPUSH:
                statemanager.push(event.state)
            # grab special quit key
            elif (
                event.type == pygame.KEYDOWN
                and event.key in (pygame.K_ESCAPE,)
            ):
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif current:
                current.on_event(event)
        # update
        if current:
            current.update(elapsed_ms)
        statemanager.update(elapsed_ms)
        ## drawing ##
        # clear
        screen.blit(background, (0, 0))
        # render output
        image = output_renderer.render()
        screen.blit(image, (0, 0))
        # flip
        pygame.display.flip()

class BufferRenderer:

    def __init__(self, font, joinattrs=None):
        self.font = font
        if joinattrs is None:
            joinattrs = ('top', 'bottom')
        self.joinattrs = joinattrs

    def render(self, buffer, color=None):
        fromattr, toattr = self.joinattrs
        rect = pygame.Rect(0, 0, 0, 0)
        items = []
        for line in buffer:
            image = self.font.render(line, color)
            rect = image.get_rect(**{fromattr: toattr})
            items.append((image, rect))
        wrap = wraprects(rect for image, rect in items)
        result = pygame.Surface(wrap.size, flags=pygame.SRCALPHA)
        for image, rect in items:
            result.blit(image, rect)
        return result


def loop(**config):
    # config
    framerate = config.get('framerate')
    if framerate is None:
        framerate = 60
    screen_size = config.get('screen_size')
    if screen_size is None:
        screen_size = (800, 600)
    # outside loop init
    pygame.font.init()
    screen = pygame.display.set_mode(screen_size)
    background = screen.copy()
    window = screen.get_rect()
    clock = pygame.time.Clock()
    font = Font('/usr/share/fonts/TTF/DejaVuSansMono.ttf', 24)
    #
    running = True
    while running:
        # tick
        elapsed_ms = clock.tick(framerate)
        # events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        # draw
        screen.blit(background, (0,0))
        pygame.display.flip()
