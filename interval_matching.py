import datetime
import unittest

from operator import attrgetter

class TestIntervalMatch(unittest.TestCase):

    def check_match_time(self, from_, to, dt):
        from_ = datetime.time(*from_)
        to = datetime.time(*to)
        interval = Interval(from_, to)
        return interval.match(dt)

    def test_time_simple(self):
        self.assertTrue(
            self.check_match_time(
                (0,0),
                (2,0),
                datetime.datetime(2023, 1, 1, 0, 0)
            )
        )
        self.assertTrue(
            self.check_match_time(
                (0,0),
                (2,0),
                datetime.datetime(2023, 1, 1, 2, 0)
            )
        )
        self.assertFalse(
            self.check_match_time(
                (0,0),
                (2,0),
                datetime.datetime(2023, 1, 1, 2, 1)
            )
        )

    def test_time_cross_midnight(self):
        self.assertTrue(
            self.check_match_time(
                (22,0), # 10pm
                (2,0), # 2am
                datetime.datetime(2023, 1, 1, 1, 30), # 1:30 am
            )
        )

    def test_duration_simple(self):
        # ending interval is simple subtraction
        dt = datetime.datetime(2023,1,1,9,0)
        interval = Interval(datetime.time(7,0), datetime.time(13,0))
        self.assertEqual(interval.duration(dt), datetime.timedelta(hours=4))

    def test_duration_cross_midnight(self):
        # 9am to next 2am
        dt = datetime.datetime(2023,1,1,9,0)
        interval = Interval(datetime.time(2,0), datetime.time(9,0))
        self.assertEqual(interval.duration(dt), datetime.timedelta(hours=17))


class Interval:

    def __init__(self, from_dt, to_dt):
        self.from_dt = from_dt
        self.to_dt = to_dt

    def duration(self, dt):
        # timeout duration in timedelta to this interval's start
        assert isinstance(dt, datetime.datetime)

        # NOTES
        # maybe take the strategy of "fixing" to_dt < from_dt

        from_dt = self.ensure_datetime(self.from_dt, dt)
        to_dt = self.ensure_datetime(self.to_dt, dt)

        if from_dt <= dt <= to_dt:
            return to_dt - dt

        if dt <= other_dt:
            td = other_dt - dt
        else:
            other_dt += datetime.timedelta(days=1)
            next_midnight = datetime.datetime.combine(
                dt.date() + datetime.timedelta(days=1),
                datetime.time()
            )
            td = (next_midnight - dt) + (other_dt - next_midnight)
        return td

    def ensure_datetime(self, maybe_time, against):
        if isinstance(maybe_time, datetime.time):
            maybe_time = datetime.datetime.combine(against.date(), maybe_time)
        return maybe_time

    def from_dt_as_datetime(self, dt):
        return self.ensure_datetime(self.from_dt, dt)

    def to_dt_as_datetime(self, dt):
        return self.ensure_datetime(self.to_dt, dt)

    def match(self, dt):
        assert isinstance(dt, datetime.datetime)
        from_dt = self.ensure_datetime(self.from_dt, dt)
        to_dt = self.ensure_datetime(self.to_dt, dt)
        if from_dt < to_dt:
            return from_dt <= dt <= to_dt
        else:
            return dt >= from_dt or dt <= to_dt
