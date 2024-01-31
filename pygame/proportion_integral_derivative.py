import argparse
import enum

import pygamelib

from pygamelib import pygame

class DerivativeMeasurement(enum.Enum):

    VELOCITY = enum.auto()
    ERROR_RATE = enum.auto()


class PID:

    def __init__(
        self,
        target,
        proportional_gain,
        integral_gain,
        derivative_gain,
        derivative_measurement,
        integration_store = None,
        integral_saturation = None,
        output_min = -1,
        output_max = +1,
    ):
        self.target = target
        self.proportional_gain = proportional_gain
        self.integral_gain = integral_gain
        self.derivative_gain = derivative_gain
        self.integration_store = integration_store
        self.integral_saturation = integral_saturation
        self.derivative_measurement = derivative_measurement
        self.output_min = output_min
        self.output_max = output_max
        self.error_last = None
        self.value_last = None
        self.derivative_initialized = False

    def update(self, dt, current):
        error = self.target - current

        proportion = self.proportional_gain * error

        self.integration_store = clamp(
            self.integration_store + (error * dt),
            -self.integral_saturation,
            +self.integral_saturation,
        )
        integral = integral_gain * self.integration_store

        error_rate = (error - self.error_last) / dt
        self.error_last = error

        self.value_rate = (current - self.value_last) / dt

        derive_measure = 0

        if not self.derivative_initialized:
            self.derivative_initialized = True
        else:
            if self.derivative_measurement == DerivativeMeasurement.VELOCITY:
                derive_measure = -self.value_rate
            else:
                derive_measure = error_rate

        derivative = self.derivative_gain * derive_measure

        result = proportion + integral + derivative
        return clamp(result, self.output_min, self.output_max)


class PIDState(pygamelib.DemoBase):

    def __init__(self, pid):
        self.pid = pid

    def do_quit(self, event):
        self.engine.stop()

    def do_keydown(self, event):
        pygamelib.post_quit()

    def update(self):
        super().update()
        new = self.pid.update(self.elapsed)


def clamp(x, a, b):
    if x < a:
        return a
    elif x > b:
        return b
    return x

def run(screen_size):
    pygame.font.init()

    pid = PID(
        target = 0,
        proportional_gain = 0.02,
        integral_gain = 0.1,
        derivative_gain = 0.001,
        derivative_measurement = DerivativeMeasurement.VELOCITY,
    )
    state = PIDState(pid)
    engine = pygamelib.Engine()
    pygame.display.set_mode(screen_size)
    engine.run(state)

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--screen-size',
        type = pygamelib.sizetype(),
        default = '800',
    )
    args = parser.parse_args(argv)
    run(args.screen_size)

if __name__ == '__main__':
    main()

# 2024-01-30 Tue.
# Trying to understand this
# https://azeemba.com/posts/pids-creating-stable-control-in-games.html
