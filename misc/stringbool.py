import unittest

class TestStringBoolean(unittest.TestCase):

    def test_true(self):
        # non-zero is true
        self.assertTrue(boolstring('1'))
        self.assertTrue(boolstring('-1'))
        self.assertTrue(boolstring('100'))
        # common true words
        self.assertTrue(boolstring('True'))
        self.assertTrue(boolstring('true'))
        self.assertTrue(boolstring('yes'))

    def test_false(self):
        # empty string is false
        self.assertFalse(boolstring(''))
        # zero is the only false integer string
        self.assertFalse(boolstring('0'))
        # common false words
        self.assertFalse(boolstring('False'))
        self.assertFalse(boolstring('false'))
        self.assertFalse(boolstring('F'))
        self.assertFalse(boolstring('f'))
        self.assertFalse(boolstring('no'))

    def test_unknown(self):
        self.assertIsNone(boolstring('night'))
        self.assertIsNone(boolstring('friday'))


def boolstring(s):
    # NOTES
    # - working out a function to take query arguments as booleans
    # - avoid return true for things the are obviously something else
    # try for integer-like boolean
    try:
        n = int(s)
    except ValueError:
        pass
    else:
        return bool(n)
    # try common words' first letters
    if s.lower() in ('false', 'no', 'true', 'yes') or len(s) == 1:
        return bool(s.lower()[0:1] in 'ty')
