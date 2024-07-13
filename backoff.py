import argparse
import os
import random
import subprocess
import time
import unittest

class TestLimiter(unittest.TestCase):

    def setUp(self):
        self.limiter = Limiter('ignored_filename')

    def test_default(self):
        self.assertFalse(self.limiter._backoff(1, []))
        self.assertFalse(self.limiter._backoff(1, [0]))
        self.assertTrue(self.limiter._backoff(1, [1]))
        self.assertTrue(self.limiter._backoff(1, [0,1]))


class Limiter:
    """
    File-based exponential backoff limiter.
    """

    def __init__(self, filename, first_duration=1, duration_limit=None):
        self.filename = filename
        self.first_duration = first_duration
        self.duration_limit = duration_limit

    def load(self):
        with open(self.filename, 'r') as backoff_file:
            # float allows trailing newline
            exception_times = [float(line) for line in backoff_file]
            return exception_times

    def _backoff(self, current_time, times):
        """
        :param current_time:
        :param times:
            Ordered list of previous times of backoff. The last time is the
            last current_time we backed off.
        """
        ntimes = len(times)
        if ntimes == 0:
            return
        if ntimes > 1:
            last_duration = times[-1] - times[-2]
        else:
            last_duration = self.first_duration
        next_duration = last_duration * ntimes
        duration = current_time - times[-1]
        if (
            self.duration_limit is not None
            and next_duration > self.duration_limit
        ):
            # clamp duration to limit
            next_duration = self.duration_limit
        if duration < next_duration:
            return True

    def backoff(self, current_time):
        if not os.path.exists(self.filename):
            return
        times = self.load()
        return self._backoff(current_time, times)

    def save(self, current_time):
        with open(self.filename, 'a') as backoff_file:
            backoff_file.write(f'{current_time}\n')

    def reset(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)


def main(argv=None):
    """
    File-based exponential backoff wrapper for discrete runs.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'backoff',
        help = 'File to use for exponential backoff.',
    )
    args, runargs = parser.parse_known_args(argv)
    # TODO
    # - parser help should show that remaining arguments are taken as the
    #   program and arguments to run.

    current_time = time.time()
    limiter = Limiter(args.backoff)
    if limiter.backoff(current_time):
        return

    try:
        subprocess.run(runargs, check=True)
    except Exception as e:
        limiter.save(current_time)

if __name__ == '__main__':
    main()
