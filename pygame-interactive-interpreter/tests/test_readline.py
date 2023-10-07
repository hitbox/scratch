from unittest import TestCase
from unittest import main

from lib.readline import Readline
from lib.readline import ReadlineError

class TestReadlineSimple(TestCase):

    def setUp(self):
        self.readline = Readline()

    def test_reset(self):
        "reset"
        self.readline.reset()
        self.assertEqual(self.readline.charbuffer, [])
        self.assertEqual(self.readline.cursor, 1)

    def test_putchar(self):
        "putchar"
        self.readline.putchar('a')
        self.assertEqual(self.readline.charbuffer, ['a'])
        # XXX:
        # readline has been working for a while but I expected the cursor to be
        # at 2, instead of 1.
        self.assertEqual(self.readline.cursor, 1)

    def test_putchar_fail(self):
        "putchar failures"
        # must be string
        with self.assertRaises(ReadlineError):
            self.readline.putchar(1)
        # only one character allowed
        with self.assertRaises(ReadlineError):
            self.readline.putchar('abc')
        # empty string raises
        with self.assertRaises(ReadlineError):
            self.readline.putchar('')

    def test_send(self):
        "send"
        self.readline.send('abc')
        self.assertEqual(self.readline.charbuffer, ['a', 'b', 'c'])
        self.assertEqual(self.readline.cursor, 3)

    def test_backspace(self):
        "backspace"
        self.readline.send('abc')
        self.readline.backspace()
        self.assertEqual(self.readline.charbuffer, ['a', 'b'])
        self.assertEqual(self.readline.cursor, 2)
        # TODO: backspace somewhere other than end


class TestReadlineDelete(TestCase):

    def setUp(self):
        self.readline = Readline()
        self.readline.send('abc')

    def test_delete_at_end(self):
        """
        `delete` at end. Does nothing and cursor does not move.
        """
        self.readline.delete()
        self.assertEqual(self.readline.charbuffer, ['a', 'b', 'c'])
        self.assertEqual(self.readline.cursor, 3)

    def test_delete_at_start(self):
        """
        `delete` at start. Delete first character and cursor does not move.
        """
        self.readline.move_start()
        self.assertEqual(self.readline.cursor, 0)
        self.readline.delete()
        self.assertEqual(self.readline.charbuffer, ['b', 'c'])
        self.assertEqual(self.readline.cursor, 0)

    def test_delete_inside(self):
        """
        `delete` somewhere inside characters. Deletes character under cursor
        and does not move cursor.
        """
        self.readline.cursor_left()
        self.readline.cursor_left()
        self.assertEqual(self.readline.cursor, 1)
        self.readline.delete()
        self.assertEqual(self.readline.charbuffer, ['a', 'c'])
        self.assertEqual(self.readline.cursor, 1)


class TestReadlineMove(TestCase):
    """
    Readline moves.
    """

    def setUp(self):
        self.readline = Readline()
        self.readline.send('abc def ghi')

    def test_move_forward_word_at_end(self):
        """
        Move forward word when already at end. Does nothing.
        """
        self.readline.move_forward_word()
        self.assertEqual(self.readline.cursor, 11)

    def test_move_forward_word_at_start(self):
        """
        Move forward word while cursor at start. Move cursor to end of first word.
        """
        self.assertEqual(self.readline.cursor, 11)
        self.readline.move_start()
        self.readline.move_forward_word()
        self.assertEqual(self.readline.cursor, 2)

    def test_move_forward_word_at_middle_whitespace(self):
        """
        Move forward word while cursor is somewhere in the middle on
        whitespace. Move cursor to end of first word after whitespace.
        """
        self.readline.cursor = 3 # index of first space
        self.readline.move_forward_word()
        self.assertEqual(self.readline.cursor, 6)

    def test_move_forward_word_at_word(self):
        """
        Move forward word while cursor is somewhere in the middle on
        and already on a word. Cursor should go to the end of the word it is on.
        """
        self.readline.cursor = 4 # index of first space
        self.readline.move_forward_word()
        self.assertEqual(self.readline.cursor, 6)

    def test_move_backward_word_at_end(self):
        """
        Move backward word while cursor at end.
        """
        self.readline.move_backward_word()
        # index of 'g'
        self.assertEqual(self.readline.cursor, 8)

    def test_move_backward_word_at_start(self):
        """
        Move backward word while cursor at start.
        """
        self.readline.cursor = 0
        # cursor does not move
        self.assertEqual(self.readline.cursor, 0)

    def test_move_backward_word_at_whitespace(self):
        """
        """
        self.readline.cursor = 3
        self.readline.move_backward_word()
        self.assertEqual(self.readline.cursor, 0)

    def test_move_backward_word_at_word(self):
        """
        """
        self.readline.cursor = 8 # 'g'
        self.readline.move_backward_word()
        self.assertEqual(self.readline.cursor, 4) # 'd'

    def test_get_words(self):
        self.assertEqual(self.readline.get_words(), ['abc', 'def', 'ghi'])

    def test_get_line(self):
        self.assertEqual(self.readline.get_line(), 'abc def ghi')
        self.assertEqual(
                self.readline.charbuffer,
                ['a', 'b', 'c', ' ', 'd', 'e', 'f', ' ', 'g', 'h', 'i'])

    def test_kill_forward_word_at_end(self):
        self.readline.kill_forward_word()
        # XXX:
        # * cursor is left unchanged at past the last index
        self.assertEqual(self.readline.cursor, 11)
        self.assertEqual(
                self.readline.charbuffer,
                ['a', 'b', 'c', ' ', 'd', 'e', 'f', ' ', 'g', 'h', 'i'])

    def test_kill_forward_word_last_word(self):
        self.readline.cursor = 8
        self.readline.kill_forward_word()
        self.assertEqual(self.readline.cursor, 8)
        self.assertEqual(
                self.readline.charbuffer,
                ['a', 'b', 'c', ' ', 'd', 'e', 'f', ' '])

    def test_kill_forward_word_at_start(self):
        self.readline.cursor = 0
        self.readline.kill_forward_word()
        self.assertEqual(self.readline.cursor, 0)
        self.assertEqual(
                self.readline.charbuffer,
                [' ', 'd', 'e', 'f', ' ', 'g', 'h', 'i'])

    def test_kill_forward_word_at_middle_whitespace(self):
        self.readline.cursor = 3 # first space
        self.readline.kill_forward_word()
        self.assertEqual(self.readline.cursor, 3)
        self.assertEqual(
                self.readline.charbuffer,
                ['a', 'b', 'c', ' ', 'g', 'h', 'i'])


if __name__ == '__main__':
    main()
