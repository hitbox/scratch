class ShorthandError(Exception):
    pass


class Shorthand:
    """
    Parse and hold shorthand properties like CSS.
    """
    # https://developer.mozilla.org/en-US/docs/Web/CSS/Shorthand_properties

    def __init__(self, top, right, bottom, left):
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left

    @classmethod
    def from_indexable(cls, args):
        """
        :param args: a flat indexable objects of at least one value.
        """
        if not args:
            raise ShorthandError('args cannot be empty')
        nargs = len(args)
        if nargs == 1:
            # 1 1 1 1
            args = (args[0], ) * 4
        elif nargs == 2:
            # 1 2 1 2
            args = args + args
        elif nargs == 3:
            # 1 2 3 2
            args = args + args[1]
        return cls(*args)
