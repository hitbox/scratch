import argparse
import math
import time as timelib

from fractions import Fraction
from itertools import count
from time import time

class steps:

    def __init__(self, step, current=0):
        self.step = step
        self.current = current

    def __iter__(self):
        return self

    def __next__(self):
        current = self.current
        self.current += self.step
        return current


class sinusoidal:

    def __init__(self, frequency, amplitude=1):
        self.frequency = frequency
        self.amplitude = amplitude

    def __call__(self, time):
        return self.amplitude * math.sin(self.frequency * time)


def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

    sinewave = sinusoidal(frequency=3, amplitude=9)

    start = timelib.time()
    for _ in range(10):
        t = timelib.time() - start
        value = sinewave(t)
        print(f'{t:0.8f}, {value}')

if __name__ == '__main__':
    main()
