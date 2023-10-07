def limit(value, min, max):
    """
    Limit value to greater-than-or-equal to min, and less-than-or-equal to max.
    """
    if value < min:
        value = min
    elif value > max:
        value = max
    return value
