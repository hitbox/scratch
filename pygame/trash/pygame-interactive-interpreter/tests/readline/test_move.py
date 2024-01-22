import unittest

from lib.readline import move

class TestReadlineMoveBackward(unittest.TestCase):
    """
    Test backward movements
    """

    def test_backward_word_from_start(self):
        self.assertEqual(move.backward_word(0, 'abc'), 0)

    def test_backward_word_from_first_word(self):
        self.assertEqual(move.backward_word(2, 'abc def'), 0)


class TestReadlineMoveForward(unittest.TestCase):
    """
    Test forward movements
    """

    def test_forward_word_from_start(self):
        "Jumps to one past last index first and only word."
        self.assertEqual(move.forward_word(0, 'abc'), 3)

    def test_forward_word_from_end(self):
        "Jumps to one past last index."
        self.assertEqual(move.forward_word(2, 'abc'), 3)

    def test_forward_word_from_end_of_first_word(self):
        "Jumps to first whitespace after first word."
        self.assertEqual(move.forward_word(2, 'abc def'), 3)

    def test_forward_word_from_first_whitespace(self):
        "Jumps to first end of next word."
        self.assertEqual(move.forward_word(3, 'abc def'), 7)

    def test_forward_word_runs_whitespace(self):
        self.assertEqual(move.forward_word(2, 'abc  def'), 3)
        self.assertEqual(move.forward_word(3, 'abc  def'), 8)


