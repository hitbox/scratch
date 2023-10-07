"""
Functions to move the cursor around.
"""
import string

from .exception import ReadlineError

alphanumeric = string.ascii_letters + string.digits

def _index_from_cursor(cursor, buffer):
    "Return the cursor constrained to the indexes of the buffer."
    return min(cursor, len(buffer)-1)

def _is_next_whitespace(index, char, nextchar):
    return nextchar in string.whitespace

def _is_whitespace(index, char, nextchar):
    return char in string.whitespace

def backward_word(cursor, buffer):
    # see: gnu/readline/text.c
    if not buffer or cursor == 0:
        return cursor

    if cursor >= len(buffer):
        cursor = len(buffer) - 1

    # If not in a word, move forward until in one. Then, move forward until
    # hits a alphanumeric character.
    if buffer[cursor] not in alphanumeric:
        while cursor > 0 and buffer[cursor] not in alphanumeric:
            cursor -= 1

    while cursor > 0 and buffer[cursor] in alphanumeric:
        cursor -= 1

    return cursor

def is_alphabet(index, char, nextchar):
    return char in string.ascii_letters

def end(cursor, buffer):
    return len(buffer)

def forward_word(cursor, buffer):
    """
    Return cursor position after moving forward one word.
    """
    if not buffer or cursor >= len(buffer):
        return cursor

    # If not in a word, move forward until in one. Then, move forward until
    # hits a alphanumeric character.
    if buffer[cursor] not in alphanumeric:
        while cursor < len(buffer) and buffer[cursor] not in alphanumeric:
            cursor += 1

    while cursor < len(buffer) and buffer[cursor] in alphanumeric:
        cursor += 1

    return cursor

def left(cursor, buffer):
    if cursor > 0:
        cursor -= 1
    return cursor

def right(cursor, buffer):
    if cursor < len(buffer):
        cursor += 1
    return cursor

def start(cursor, buffer):
    return 0

def until(cursor, buffer, delta, condition):
    """
    TODO: description

    :param delta: -1 or 1
    :param condition: callable taking a cursor position and character,
        returning truthy to break moving.
    """
    if delta not in (-1, 1):
        raise ReadlineError('Delta must be -1 or 1.')

    if delta == -1:
        def not_limit():
            return cursor > 0
    else:
        def not_limit():
            return cursor < len(buffer)

    # guarantee move
    if not_limit():
        cursor = cursor + delta
    while not_limit():
        # cursor could still be out of range
        try:
            char = buffer[cursor]
        except IndexError:
            # invalid index, keep moving
            cursor += delta
            continue
        try:
            nextchar = buffer[cursor + delta]
        except IndexError:
            nextchar = None
        else:
            if condition(cursor, char, nextchar):
                break
        cursor += delta
    return cursor
