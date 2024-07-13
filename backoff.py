import argparse
import os
import random
import time
import unittest

# quick and dirty explaination:
# - never backoff if no file
# - read times from file
# - calculate last duration between backoffs, defaulting to first_duration if
#   only one is available
# - multiply the last duration by number of lines to get a kind of exponential
#   backoff

class TestLimiter(unittest.TestCase):

    def setUp(self):
        self.limiter = Limiter('nonexistant')

    def test_default(self):
        self.assertFalse(self.limiter._backoff(1, [0]))
        self.assertTrue(self.limiter._backoff(1, [1]))
        self.assertTrue(self.limiter._backoff(1, [0,1]))


class Limiter:

    def __init__(self, filename, first_duration=1):
        self.filename = filename
        self.first_duration = first_duration
        # TODO
        # - want a limit on exponentiation

    def read_times(self):
        with open(self.filename, 'r') as backoff_file:
            exception_times = [float(line) for line in backoff_file]
            return exception_times

    def _backoff(self, current_time, exception_times):
        if len(exception_times) > 1:
            last_duration = exception_times[-1] - exception_times[-2]
        else:
            last_duration = self.first_duration
        duration = current_time - exception_times[-1]
        next_duration = last_duration * len(exception_times)
        if duration < next_duration:
            return True

    def backoff(self, current_time):
        if not os.path.exists(self.filename):
            return
        exception_times = self.read_times()
        return self._backoff(current_time, exception_times)

    def save(self, current_time):
        with open(self.filename, 'a') as backoff_file:
            backoff_file.write(f'{current_time}\n')

    def reset(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--backoff', help='Backoff on exception using a file.')
    args = parser.parse_args(argv)

    current_time = time.time()

    limiter = Limiter(args.backoff)

    if limiter.backoff(current_time):
        print('too fast')
        return

    print('running')
    try:
        1 / 0
    except Exception as e:
        limiter.save(current_time)
    else:
        limiter.reset()

if __name__ == '__main__':
    main()
