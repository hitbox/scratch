import time

from itertools import cycle

class Delayed:
    """
    Return same from next() until delay threshold has been met.
    """

    def __init__(self, iterable, delay_seconds: float):
        self.iterable = iterable
        self.delay_seconds = delay_seconds
        self.last_time = None
        self.result = None

    def __next__(self):
        if self.last_time is None:
            self.last_time = time.time()
            self.result = next(self.iterable)
        else:
            current = time.time()
            if current - self.last_time >= self.delay_seconds:
                self.result = next(self.iterable)
                self.last_time = current
        return self.result
