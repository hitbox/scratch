from . import move
from . import put
from .exception import ReadlineError

class Readline:
    """
    The state of and operations on reading a line of text and managing a cursor.
    """
    # TODO:
    # 1. insert/overwrite mode

    def __init__(self):
        self.reset()

    def reset(self):
        self.buffer = ''
        self.cursor = 1

    def putchar(self, char):
        __doc__ = put.insert.__doc__
        self.buffer = put.insert(self.cursor, self.buffer, char)
        self.cursor = move.right(self.cursor, self.buffer)

    def send(self, chars):
        """
        Send iterable of characters to `putchar`.
        """
        for char in chars:
            self.putchar(char)
        try:
            char
        except NameError:
            raise ReadlineError('Invalid iterable, nothing sent.')

    def cursor_split(self):
        "Return left-of and right-of cursor of the character buffer."
        # XXX:
        # * is this used? or just rendered in the demo?
        if self.cursor < len(self.buffer):
            left = self.buffer[:self.cursor]
            right = self.buffer[self.cursor:]
        else:
            left = self.buffer[:]
            right = []
        return left, right

    def backspace(self):
        "Remove character before cursor."
        if self.buffer:
            if 0 < self.cursor <= len(self.buffer):
                self.buffer.pop(self.cursor - 1)
            self.move_left()

    def delete(self):
        "Remove character under cursor."
        if self.cursor < len(self.buffer):
            self.buffer.pop(self.cursor)

    def move_left(self):
        "Try to move cursor left."
        self.cursor = move.left(self.cursor, self.buffer)

    def move_right(self):
        "Try to move cursor right."
        self.cursor = move.right(self.cursor, self.buffer)

    def move_end(self):
        "Move cursor to end of buffer."
        self.cursor = move.end(self.cursor, self.buffer)

    def move_start(self):
        "Move cursor to start of buffer."
        self.cursor = move.start(self.cursor, self.buffer)

    def move_forward_word(self, count=None):
        """
        Move `count` words forward.
        :param count: int if None defaults to 1
        """
        if count is None:
            count = 1
        while count > 0:
            self.cursor = move.forward_word(self.cursor, self.buffer)
            count -= 1

    def move_forward_line(self):
        "Move cursor to end of line."
        self.cursor = len(self.buffer)

    def move_backward_word(self, count=None):
        "Move cursor back until beginning of word."
        if count is None:
            count = 1
        while count:
            self.cursor = move.backward_word(self.cursor, self.buffer)
            # moved one word
            count -= 1

    def move_backward_line(self):
        "Move cursor to beginning of line."
        self.cursor = 0

    def get_words(self):
        return self.get_line().split()

    def get_line(self):
        "Return buffer as string."
        return ''.join(self.buffer)

    def _kill_slice(self, from_, to):
        # TODO:
        # * clipboard
        self.buffer = self.buffer[:from_] + self.buffer[to:]

    def kill_forward_word(self, count=1):
        to_cursor = move.forward_word(self.cursor, self.buffer) + 1
        if self.cursor != to_cursor:
            self._kill_slice(self.cursor, to_cursor)

    def kill_backward_word(self, count=1):
        from_cursor = move.backward_word(self.cursor, self.buffer)
        if self.cursor != from_cursor:
            self._kill_slice(from_cursor, self.cursor)
            self.cursor = from_cursor

    def kill_backward_line(self):
        if self.cursor == 0:
            return
        self._kill_slice(0, self.cursor)
        self.cursor = 0

    def kill_forward_line(self):
        if self.cursor >= len(self.buffer):
            return
        self._kill_slice(self.cursor, len(self.buffer))
