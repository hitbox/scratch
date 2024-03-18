class MenuItem:

    def __init__(self, text):
        self.text = text


def choosedict(iterable, case_sensitive=False):
    keys = set()
    for index, obj in enumerate(iterable):
        if not obj or not isinstance(obj, str):
            raise ValueError
        for first_letter in obj:
            if first_letter not in keys:
                break
        else:
            raise ValueError('Unable to find unique key')


print(choosedict(['Play', 'Options', 'Credits', 'Exit']))

# - looked at old jaccuse code
# - want to work out good menuing system
