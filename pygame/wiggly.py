import abc
import argparse

import pygamelib

from pygamelib import pygame

class EventMethodDispatchMixin:
    """
    Dispatch events to their lowercased names with a "do_" prefix.
    """

    def dispatch_event(self, event):
        event_name = pygame.event.event_name(event.type).lower()
        method_name = f'do_{event_name}'
        method = getattr(self, method_name, None)
        if method is not None:
            return method(event)


class StateABC(abc.ABC):

    @abc.abstractmethod
    def start(self, engine):
        pass

    @abc.abstractmethod
    def update(self):
        pass


class Engine:
    """
    Run a state until stopped.
    """

    def __init__(self):
        self.stop()

    def stop(self):
        self.running = False

    def run(self, state):
        state.start(engine=self)
        self.running = True
        while self.running:
            state.update()


class Timer:

    def __init__(self, duration):
        self.duration = duration
        self.elapsed = 0
        self.active = False

    def update(self, elapsed):
        next_ = self.elapsed + elapsed
        if next_ >= self.duration:
            self.elapsed = next_ % self.duration
            self.active = True
        else:
            self.elapsed = next_
            self.active = False


class Circle:

    def __init__(self, radius, position=None):
        if position is None:
            position = pygame.Vector2()
        assert isinstance(position, pygame.Vector2)
        self.position = position
        self.radius = radius

    def distance(self, other):
        return (other.position - self.position) - (other.radius + self.radius)


class Player:

    def __init__(self, radius, *sprite_groups):
        self.sprite = pygame.sprite.Sprite(*sprite_groups)
        self.sprite.image = pygame.Surface((radius*2,)*2, pygame.SRCALPHA)
        pygame.draw.circle(self.sprite.image, 'red', (radius,)*2, radius)
        self.sprite.rect = self.sprite.image.get_rect()
        self.body = Circle(radius)
        self.body.position.update(self.sprite.rect.center)

    def update(self, elapsed):
        self.sprite.rect.center = self.body.position


class Asteroid:

    def __init__(self, radius, velocity, *sprite_groups):
        self.body = Circle(radius)
        self.velocity = velocity
        self.sprite = pygame.sprite.Sprite(*sprite_groups)
        self.sprite.image = pygamelib.circle_surface(radius, 'grey')
        self.sprite.rect = self.sprite.image.get_rect()
        self.sprite.rect.center = self.body.position

    def update(self, elapsed):
        self.body.position.update(self.body.position + self.velocity)
        self.sprite.rect.center = self.body.position


class WigglyState(pygamelib.DemoBase):

    def start(self, engine):
        super().start(engine)
        self.mouse_pos = None
        self.mouse_pressed = None
        self.drawgroup = pygame.sprite.Group()
        self.player = Player(30, self.drawgroup)
        self.asteroids = []
        self.asteroid_spawn = self.window.copy()
        self.asteroid_spawn.midbottom = self.window.midtop
        self.asteroid_timer = Timer(1000)

    def update(self):
        super().update()
        # update
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_pressed = pygame.mouse.get_pressed()

        # remove below screen asteroid
        self.asteroids = [
            asteroid for asteroid in self.asteroids
            if (asteroid.body.position.y - asteroid.body.radius) < self.window.bottom
        ]

        for asteroid in self.asteroids:
            asteroid.update(self.elapsed)

        self.player.body.position.update(self.mouse_pos)
        self.player.sprite.rect.center = self.player.body.position

        self.asteroid_timer.update(self.elapsed)
        if self.asteroid_timer.active:
            asteroid_diameter = 100
            asteroid_radius = asteroid_diameter // 2
            asteroid = Asteroid(
                asteroid_radius,
                pygame.Vector2(0, 5),
                self.drawgroup,
            )
            asteroid.body.position.update(self.asteroid_spawn.midtop)
            self.asteroids.append(asteroid)

        # XXX
        # - left off getting flashing asteroids in the upper left

        # draw
        self.screen.fill('black')
        self.drawgroup.draw(self.screen)
        pygame.draw.circle(
            self.screen,
            'magenta',
            self.player.body.position,
            self.player.body.radius,
            1
        )
        pygame.display.flip()

    def do_quit(self, event):
        self.engine.stop()

    def do_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            pygame.event.post(pygame.event.Event(pygame.QUIT))


def run(display_size):
    engine = Engine()
    state = WigglyState()
    pygame.display.set_mode(display_size)
    engine.run(state)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    args = parser.parse_args(argv)
    run(args.display_size)

if __name__ == '__main__':
    main()

# 2023-12-30
# - https://www.reddit.com/r/pygame/comments/18ui5rp/i_made_a_game_download_it_on_itchio_source_code/
# - motivated to make a game where you control a shape and try to get as close
#   as possible without touching other moving shapes.
