import random

from abc import ABC
from abc import abstractmethod

from engine.engine import Engine
from engine.engine import stopengine
from lib.cli import simple_parser
from lib.external import pygame
from lib.font import PygameFont
from lib.rect import wraprects
from lib.screen import Screen
from scenes.base import BaseScene

SPAWNRECT = pygame.event.custom_type()
KILLRECT = pygame.event.custom_type()
MISSRECT = pygame.event.custom_type()
SWITCHSTATE = pygame.event.custom_type()

def emit_missrect():
    event = pygame.event.Event(MISSRECT)
    pygame.event.post(event)

def emit_killrect():
    event = pygame.event.Event(KILLRECT)
    pygame.event.post(event)

class Countdown:
    """
    Post pygame event when countdown reaches zero or below.
    """

    def __init__(self, start_ms, event_type, event_data=None):
        self.start_ms = start_ms
        self.event_type = event_type
        if event_data is None:
            event_data = {}
        self.event_data = event_data
        self.reset()

    def reset(self):
        self.value = self.start_ms

    def send_event(self):
        event = pygame.event.Event(self.event_type, self.event_data)
        pygame.event.post(event)

    def update(self, elapsed):
        if self.value > 0:
            self.value -= elapsed
            if self.value <= 0:
                self.send_event()


class EventDispatcherError(Exception):
    pass


class BaseEventDispatcher(ABC):

    @abstractmethod
    def dispatch_events(self, event):
        pass


class AttributeEventDispatcher(BaseEventDispatcher):

    def __init__(
        self,
        obj,
        handler_prefix = 'on_',
        custom_events = None,
    ):
        self.obj = obj
        self.handler_prefix = handler_prefix
        self.handlers = {}
        self.notfound = set()
        if custom_events is None:
            custom_events = {}
        # XXX: 2021-10-16
        # LEFT OFF HERE
        # * want to be able to hook up custom events
        # * need a custom type integer to name lookup
        # * should be given to this
        # * fallback on find_handler to custom event handler lookup
        self.custom_events = custom_events

    def is_event_handler(self, event_name, attrname):
        has_prefix = attrname.startswith(self.handler_prefix)
        after_prefix = len(self.handler_prefix)
        has_event_name = event_name == attrname[after_prefix:]
        return (has_prefix and has_event_name)

    def is_custom_event_handler(self, event_name, attrname):
        pass

    def dispatch_events(self, events):
        "Dispatch all events"
        for event in events:
            self.dispatch_event(event)

    def dispatch_event(self, event):
        "Dispatch a single event or try to find a handler."
        if event.type in self.handlers:
            self.handlers[event.type](event)
        elif event.type not in self.notfound:
            handler = self.find_handler(event.type)
            if handler is not None:
                handler(event)

    def get_event_name(self, event_type):
        event_name = pygame.event.event_name(event_type)
        return event_name.lower()

    def find_handler(self, event_type):
        event_name = self.get_event_name(event_type)
        for attrname in dir(self.obj):
            if attrname.startswith('_'):
                continue
            if self.is_event_handler(event_name, attrname):
                if event_type in self.handlers:
                    raise EventDispatcherError('Overwrite handler')
                handler = getattr(self.obj, attrname)
                self.handlers[event_type] = handler
                return handler
        else:
            self.notfound.add(event_type)


class BaseState(ABC):

    @abstractmethod
    def on_event(self, event):
        pass

    @abstractmethod
    def update(self, events, elapsed):
        pass


class SpawnState(BaseState):
    """
    Wait and spawn rect
    """

    def __init__(self, first_countdown):
        self.countdown = Countdown(first_countdown, SPAWNRECT)

    def reset(self):
        time = random.choice([250, 500, 750, 1000])
        self.countdown = Countdown(time, SPAWNRECT)

    def update(self, elapsed, events):
        self.countdown.update(elapsed)
        for event in events:
            self.on_event(event)

    def on_event(self, event):
        if event.type == SPAWNRECT:
            event = pygame.event.Event(SWITCHSTATE)
            pygame.event.post(event)


class ClickState(BaseState):
    """
    Player tries to click the rect before it disappears.
    """

    def __init__(self):
        self.target_rect = None

    def update(self, elapsed, events):
        for event in events:
            self.on_event(event)

    def on_event(self, event):
        if event.type == KILLRECT:
            emit_missrect()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.target_rect.collidepoint(event.pos):
                emit_killrect()
            else:
                emit_missrect()


class ClickGame:

    def  __init__(self):
        self.points = 0

    def miss(self):
        self.points -= 100

    def hit(self):
        self.points += 100


class ClickMinigameScene(BaseScene):
    """
    Simple click when rects align mini game thing.
    """

    def enter(self):
        pass

    def exit(self):
        pass

    def __init__(self, screen_size):
        #
        self.game = ClickGame()
        self.event_dispatcher = AttributeEventDispatcher(self)
        # pygame setup
        if screen_size is None:
            screen_size = (800, 600)
        self.screen = Screen(screen_size)
        self.ui_frame = self.screen.rect.inflate(*(-50,)*2)
        self.clock = pygame.time.Clock()
        pygame.font.init()
        self.font = pygame.font.SysFont('monospace', 30)
        #
        self.states = {
            'spawnrect': SpawnState(first_countdown=1000),
            'clickrect': ClickState(),
        }
        #
        self.reset()

    def reset(self):
        self.state = self.states['spawnrect']
        self.click_rect = None

    def spawn_clickrect(self):
        self.click_rect = pygame.Rect(0,0,50,50)
        self.click_rect.center = self.screen.rect.center

    def kill_clickrect(self):
        self.click_rect = None

    def update(self, events):
        # tick
        elapsed = self.clock.tick(60)
        self.event_dispatcher.dispatch_events(events)
        # update
        self.state.update(elapsed, events)
        # draw
        self.draw()

    def on_quit(self, event):
        stopengine()

    def on_userevent(self, event):
        breakpoint()

    def on_switchstate(self, event):
        if self.state is self.states['spawnrect']:
            self.spawn_clickrect()
            self.states['clickrect'].target_rect = self.click_rect
            self.state = self.states['clickrect']

    def on_killrect(self, event):
        if self.state is self.states['clickrect']:
            self.game.hit()
            self.kill_clickrect()
            self.states['spawnrect'].reset()
            self.state = self.states['spawnrect']

    def on_missrect(self, event):
        self.game.miss()

    def draw(self):
        # draw
        self.screen.clear()
        if self.click_rect is not None:
            pygame.draw.rect(self.screen.surface, (200,10,10), self.click_rect)
        image = self.font.render(f'{self.game.points}', True, (200,)*3)
        self.screen.blit(image, image.get_rect(topright=self.ui_frame.topright))
        pygame.display.flip()


def main(argv=None):
    parser = simple_parser(description=ClickMinigameScene.__doc__)
    args = parser.parse_args(argv)

    engine = Engine()
    scene = ClickMinigameScene(args.screen_size)
    engine.run(scene)

if __name__ == '__main__':
    main()
