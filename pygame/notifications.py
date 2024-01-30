import argparse
import contextlib
import enum
import itertools as it
import math
import os
import time

from operator import attrgetter

with open(os.devnull, 'w') as devnull:
    with contextlib.redirect_stdout(devnull):
        import pygame

del devnull

class EventHandlerMixin:
    """
    Mixin event handling. Dispatch events to methods named
    `on_{lowercase_event_type_name}`. Like `on_keydown`.
    """

    def on_event(self, event):
        attrname = event_attrname(event)
        attr = getattr(self, attrname, None)
        if attr:
            attr(event)


class Engine:
    """
    Run a state until the quit event.
    """

    def __init__(self):
        self.running = False

    def get_event_handler(self, state):
        def on_event(event):
            "No operation callable."
        if hasattr(state, 'on_event'):
            on_event = state.on_event
        return on_event

    def run(self, state):
        on_event = self.get_event_handler(state)
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                else:
                    on_event(event)
            else:
                # normal frame
                state.update()
                state.draw()


class Lerp:
    """
    Calculate a value at time/percent between a and b.
    """

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def at(self, percent):
        return lerp(self.a, self.b, percent)


class Timer:
    """
    Track elapsed time.
    """

    def __init__(
        self,
        duration,
        elapsed = 0,
        tick_callback = None,
        end_callback = None,
    ):
        assert elapsed >= 0
        assert duration >= 0
        self.duration = duration
        self.elapsed = elapsed
        self.tick_callback = tick_callback
        self.end_callback = end_callback

    @property
    def percent(self):
        return self.elapsed / self.duration

    @property
    def is_end(self):
        return self.elapsed >= self.duration

    def update(self, elapsed):
        if self.elapsed < self.duration:
            self.elapsed += elapsed
            if self.tick_callback:
                self.tick_callback()


class NotifyState(enum.Enum):

    ARRIVING = enum.auto()
    NORMAL = enum.auto()
    LEAVING = enum.auto()

    def next(self):
        return self.__class__(self.value + 1)


class NotificationSprite(pygame.sprite.Sprite):

    def next_state(self):
        self.state = self.state.next()

    @classmethod
    def from_string(
        cls,
        string,
        font,
        color,
        antialias = True,
        state = NotifyState.ARRIVING,
        **rect_kwargs,
    ):
        inst = cls()
        inst.image = font.render(string, antialias, color)
        inst.rect = inst.image.get_rect(**rect_kwargs)
        inst.state = NotifyState.ARRIVING
        return inst


class AnimationManager:
    """
    Animation Manager
    """

    def __init__(self):
        self.timers = []

    def _update_and_generate_timers(self, elapsed):
        """
        Update all timers, yielding if still active.
        """
        for timer in self.timers:
            timer.update(elapsed)
            if timer.is_end:
                if timer.end_callback:
                    timer.end_callback()
            else:
                yield timer

    def update(self, elapsed):
        self.timers = list(self._update_and_generate_timers(elapsed))


class NotificationAnimationManager(AnimationManager):

    reveal_duration = 750
    show_duration = 5000
    dismiss_duration = 1000

    # Sketching:
    # - event listener called for event
    # - simple function to `notify("the event")`
    # - simple function begins animation that goes from reveal, show, dismiss
    #   and responds to clicks to manually dismiss it.

    def reveal(self, notification_sprite):
        """
        Begin timer to reveal a notification.
        """
        timer = lerp_attribute_timer(
            obj = notification_sprite.rect,
            attr = 'size',
            a = pygame.Vector2(),
            b = pygame.Vector2(
                notification_sprite.image.get_size()
            ),
            duration = self.reveal_duration,
            end_callback = self.end_reveal_callback(
                notification_sprite,
            ),
        )
        self.timers.append(timer)

    def end_reveal_callback(self, notification_sprite):
        """
        Callback at end of reveal timer, starts timer to show text image.
        """
        def end_callback():
            notification_sprite.rect.size = notification_sprite.image.get_size()
            notification_sprite.next_state()
            timer = Timer(
                self.show_duration,
                end_callback = self.dismiss_notification_callback(
                    notification_sprite
                ),
            )
            self.timers.append(timer)
        return end_callback

    def dismiss_notification_callback(self, sprite):
        """
        End of show text image timer, begins dismiss animation.
        """
        def dismiss_callback():
            self.dismiss_notification(sprite)
        return dismiss_callback

    def dismiss_notification(self, sprite):
        """
        Begin timer to dismiss notification.
        """
        sprite.state = NotifyState.LEAVING
        timer = lerp_attribute_timer(
            obj = sprite.rect,
            attr = 'size',
            a = pygame.Vector2(
                sprite.image.get_size()
            ),
            b = pygame.Vector2(),
            duration = self.dismiss_duration,
            end_callback = sprite.kill,
        )
        self.timers.append(timer)


class NotificationRenderer:
    """
    Render Notifications
    """

    def draw(self, screen, sprites):
        for sprite in sprites:
            if sprite.state is NotifyState.NORMAL:
                screen.blit(sprite.image, sprite.rect)
            else:
                if sprite.state is NotifyState.ARRIVING:
                    background_color = 'darkgreen'
                    border_color = 'white'
                elif sprite.state is NotifyState.LEAVING:
                    background_color = 'grey20'
                    border_color = 'grey30'
                pygame.draw.rect(screen, background_color, sprite.rect)
                pygame.draw.rect(screen, border_color, sprite.rect, 1)


class NotificationDemo(
    EventHandlerMixin,
):
    """
    Stacking notification demo.
    """

    def __init__(
        self,
        screen,
        frames_per_second = 60,
    ):
        self.screen = screen
        self.window = self.screen.get_rect()
        self.font = pygame.font.SysFont('monospace', 20)
        self.clock = pygame.time.Clock()
        self.frames_per_second = frames_per_second
        self.sprites = pygame.sprite.Group()
        self.animation_manager = NotificationAnimationManager()
        self.sprites_renderer = NotificationRenderer()

    def on_keydown(self, event):
        notification = NotificationSprite.from_string(
            str(event),
            self.font,
            'white',
            height = 0,
        )
        self.sprites.add(notification)
        self.animation_manager.reveal(notification)

    def on_mousebuttondown(self, event):
        for sprite in self.sprites:
            if (
                sprite.state is NotifyState.NORMAL
                and
                sprite.rect.collidepoint(event.pos)
            ):
                self.animation_manager.dismiss_notification(sprite)

    def update_notification_stack(self):
        """
        Align notifications in relation to each other.
        """
        if self.sprites:
            sprites = self.sprites.sprites()
            sprites[-1].rect.midbottom = self.window.midbottom
        midbottom_midtop(map(get_rect, reversed(self.sprites.sprites())))

    def update(self):
        elapsed = self.clock.tick(self.frames_per_second)
        self.update_notification_stack()
        self.sprites.update(elapsed)
        self.animation_manager.update(elapsed)

    def draw(self):
        self.screen.fill('black')
        self.sprites_renderer.draw(self.screen, self.sprites)
        pygame.display.flip()


class pairwise_setattr:

    def __init__(self, nextattr, prevattr):
        self.nextattr = nextattr
        self.prevattr = prevattr

    def __call__(self, iterable):
        for a, b in it.pairwise(iterable):
            setattr(b, self.nextattr, getattr(a, self.prevattr))


get_rect = attrgetter('rect')

topleft_bottomleft = pairwise_setattr('topleft', 'bottomleft')
bottomleft_topleft = pairwise_setattr('bottomleft', 'topleft')
midbottom_midtop = pairwise_setattr('midbottom', 'midtop')

def event_attrname(event):
    name = pygame.event.event_name(event.type)
    attrname = f'on_{ name.lower() }'
    return attrname

def lerp(a, b, t):
    return a * (1 - t) + b * t

def lerp_attribute_timer(obj, attr, a, b, duration, end_callback=None):
    """
    Create a timer that lerps an object's attribute.
    """
    lerp = Lerp(a, b)

    def tick_callback():
        setattr(obj, attr, lerp.at(timer.percent))

    timer = Timer(
        duration,
        tick_callback = tick_callback,
        end_callback = end_callback,
    )
    return timer

def demo_notifications():
    pygame.font.init()
    screen = pygame.display.set_mode((800,)*2)
    state = NotificationDemo(screen)
    engine = Engine()
    engine.run(state)

def main(argv=None):
    """
    Notifications
    """
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)
    demo_notifications()

if __name__ == '__main__':
    main()
