import argparse
import unittest

class TestHoursMinutesSeconds(unittest.TestCase):

    # NOTE
    # - using total_seconds calculated from hours-minutes-seconds tuple because
    #   large integers of seconds is painful.

    def assert_seconds(self, hours_minutes_seconds, tup):
        hours, minutes, seconds = hours_minutes_seconds
        hours *= 60 * 60
        minutes *= 60
        total_seconds = hours + minutes + seconds
        self.assertEqual(hms(total_seconds), tup)

    def assert_same(self, hours_minutes_seconds):
        # assert same tuple in, same tuple out
        self.assert_seconds(hours_minutes_seconds, hours_minutes_seconds)

    def test_zero(self):
        self.assert_seconds((0,0,0), (0,0,0))

    def test_no_rollover(self):
        self.assert_same((0,0,1))
        self.assert_same((0,1,0))
        self.assert_same((1,0,0))
        self.assert_same((0,0,59))
        self.assert_same((0,59,59))

    def test_rollover(self):
        self.assert_seconds((0,0,60), (0,1,0))
        self.assert_seconds((0,0,120), (0,2,0))
        self.assert_seconds((0,0,125), (0,2,5))

        self.assert_seconds((0,60,0), (1,0,0))
        self.assert_seconds((0,120,0), (2,0,0))
        self.assert_seconds((0,125,0), (2,5,0))

        self.assert_seconds((0,60,60), (1,1,0))
        self.assert_seconds((0,59,60), (1,0,0))

        self.assert_seconds((0,60,5), (1,0,5))
        self.assert_seconds((60,60,5), (61,0,5))


# TODO
# - days?
# - and if days where to stop?
# - I think I see a map(divmod, zip(...)_) down there
#   - continuously divmod-ing the leading div part
#   - or maybe it's recursive?

def hms(seconds):
    """
    seconds -> hours, minutes, seconds
    """
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return (hours, minutes, seconds)

def main(argv=None):
    """
    Print the hours, minutes, and seconds of given seconds.
    """
    parser = argparse.ArgumentParser(
        description = main.__doc__,
    )
    parser.add_argument('s', type=int, help='Seconds')
    args = parser.parse_args(argv)
    print(hms(args.s))

if __name__ == '__main__':
    main()
