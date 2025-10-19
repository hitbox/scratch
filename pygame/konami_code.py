import os
import argparse

from enum import Enum
from contextlib import redirect_stdout

from statemachine import State
from statemachine import StateMachine
from statemachine.exceptions import TransitionNotAllowed

with redirect_stdout(open(os.devnull, 'w')):
    import pygame

class Flash(pygame.Color):

    def __init__(self, *args, second_color, time=0, total=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.second_color = second_color
        self.time = time
        self.total = total

    def flash(self):
        self.time = self.total

    def final(self):
        if self.time > 0:
            return self.lerp(self.second_color, self.time / self.total)
        else:
            return self

    def update(self, elapsed):
        self.time -= elapsed


class KonamiCodeMachine(StateMachine):
    # Define all states
    start = State("Start", initial=True)
    up1 = State("Up 1")
    up2 = State("Up 2")
    down1 = State("Down 1")
    down2 = State("Down 2")
    left1 = State("Left 1")
    right1 = State("Right 1")
    left2 = State("Left 2")
    right2 = State("Right 2")
    b_press = State("B")
    a_press = State("A")
    success = State("Success")

    # Internal transitions (not called directly)
    _first_up = start.to(up1)
    _second_up = up1.to(up2)
    _first_down = up2.to(down1)
    _second_down = down1.to(down2)
    _first_left = down2.to(left1)
    _first_right = left1.to(right1)
    _second_left = right1.to(left2)
    _second_right = left2.to(right2)
    _press_b = right2.to(b_press)
    _press_a = b_press.to(a_press)
    _complete = a_press.to(success)

    # Reset from any non-start state back to start
    _reset = (
        up1.to(start) | up2.to(start) | 
        down1.to(start) | down2.to(start) |
        left1.to(start) | right1.to(start) | 
        left2.to(start) | right2.to(start) |
        b_press.to(start) | a_press.to(start)
    )
    
    _restart = success.to(start)

    def __init__(self, lives):
        super().__init__()
        self.lives = lives
        self.last_accepted = False
        # Map input to list of transitions to try
        self._input_map = {
            'UP': [self._first_up, self._second_up],
            'DOWN': [self._first_down, self._second_down],
            'LEFT': [self._first_left, self._second_left],
            'RIGHT': [self._first_right, self._second_right],
            'B': [self._press_b],
            'A': [self._press_a],
            'START': [self._complete],
            'RESTART': [self._restart],
        }

    def input(self, button):
        """
        Process a button input. Returns True if accepted, False if rejected.
        """
        if button not in self._input_map:
            return False

        # Try each possible transition for this input
        for transition in self._input_map[button]:
            try:
                transition()
                self.last_accepted = True
                return True
            except TransitionNotAllowed:
                continue

        # No valid transition - reset if not at start
        if self.current_state != self.start:
            self._reset()

        self.last_accepted = False
        return False

    def on_enter_success(self):
        """
        Called automatically when entering success state
        """
        print('🎮 Konami Code Accepted! Extra lives unlocked!')
        self.lives = 99


def argument_parser():
    parser = argparse.ArgumentParser()
    return parser

def main(argv=None):
    parser = argument_parser()
    args = parser.parse_args(argv)

    screen = pygame.display.set_mode((1500, 920))
    frame = screen.get_rect()
    clock = pygame.time.Clock()
    pygame.font.init()
    font = pygame.font.SysFont(None, 32)
    framerate = 60

    machine = KonamiCodeMachine(3)

    key2buttons = {
        pygame.K_UP: 'UP',
        pygame.K_DOWN: 'DOWN',
        pygame.K_LEFT: 'LEFT',
        pygame.K_RIGHT: 'RIGHT',
        pygame.K_b: 'B',
        pygame.K_a: 'A',
        pygame.K_RETURN: 'START',
        pygame.K_SPACE: 'RESTART',
    }

    step_flash = Flash('black', second_color='white', total=1000)

    elapsed = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in key2buttons:
                    try:
                        machine.input(key2buttons[event.key])
                        step_flash.flash()
                    except TransitionNotAllowed:
                        pass

        step_flash.update(elapsed)
        bgcolor = step_flash.final()

        screen.fill(bgcolor)
        image = font.render(str(machine), True, 'white')
        rect = image.get_rect(center=frame.center)
        screen.blit(image, rect)

        image = font.render(f'{machine.lives=}', True, 'white')
        screen.blit(image, image.get_rect(midtop=rect.midbottom))

        pygame.display.update()
        elapsed = clock.tick(framerate)

if __name__ == '__main__':
    main()
