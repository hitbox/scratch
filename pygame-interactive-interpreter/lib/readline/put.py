def insert(cursor, buffer, char):
    """
    Put character into buffer and handle cursor.

    :param char: a single character.
    """
    if not isinstance(char, str):
        raise ReadlineError('Only strings are allowed.')
    elif len(char) > 1:
        raise ReadlineError('Only single character strings are allowed.')
    elif not char:
        raise ReadlineError('Empty string is not allowed.')
    return buffer[:cursor] + char + buffer[cursor:]

def overwrite(cursor, buffer, char):
    raise NotImplementedError
