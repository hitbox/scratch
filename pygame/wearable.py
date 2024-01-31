import argparse
import math

from pprint import pprint

class Error(Exception):
    pass


class Object:

    def __init__(self, burden=None):
        if burden is None:
            burden = 0
        self.burden = burden


class Entity(Object):

    def __init__(self, wearing=None):
        # TODO
        # - the parts of an entity should be what wears things
        # - humans have arms, legs, shoulders, heads, etc. those are what wear things
        # - mannequins have similar and can wear things
        # - a simple robot might have shoulders and a head
        # - a couch could have a bunch of wearables draped across it (wearing them)
        if wearing is None:
            wearing = []
        self.wearing = WearableContainer(wearing)


class Wearable(Object):
    pass


class Shirt(Wearable):
    pass


class Pants(Wearable):
    pass


class Shoe(Wearable):
    pass


class Ornament(Wearable):
    # necklaces
    # jewelry
    # christmas tree ornaments
    pass


class Container(list, Object):

    def __init__(self, iterable, burden_limit=math.inf):
        self.burden_limit = burden_limit
        super().__init__(iterable)
        for object_ in self:
            self.validate_object(object_)

    def validate_object(self, object_):
        # raise to validate
        pass

    def append(self, object_):
        self.validate_object(object_)
        super().append(object_)

    def total_burden(self):
        return sum(obj.burden for obj in self)


class WearableContainer(Container):

    def validate_object(self, object_):
        # validate for append/inclusion
        assert isinstance(object_, Wearable)
        assert object_.burden + self.total_burden() < self.burden_limit


class Slot(Container):
    # a slot is a container limited to one object?

    def validate_object(self, object_):
        assert len(self) == 0


class ShoeSlot(Slot):
    # a slot that only allows shoes inside it
    pass


def devel1():
    white_tshirt = Shirt(burden=1)
    bluejeans = Pants(burden=3)
    trainers = Shoe(burden=2)
    baseball = Object(burden=1)
    objects = dict(
        white_tshirt = white_tshirt,
        bluejeans = bluejeans,
        trainers = trainers,
        baseball = baseball,
    )
    player = Entity(
        wearing = WearableContainer(
            [
                white_tshirt,
                bluejeans,
                trainers,
            ],
            burden_limit = 9,
        )
    )
    objects.update(player=player)
    pprint(objects)

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('func')
    args = parser.parse_args(argv)
    eval(args.func)()

if __name__ == '__main__':
    main()

# 2024-01-30 Tue.
# 1. system of wearing things
# 2. rendering system to show appearance
# These are two huge things so better get started.
#
# Thoughts:
# - capture in namedtuple every instance of characters during each turn
# - wearables should have the "inventory" for characters
# - wearing something means it stays on something with little to no effort
# - wearables have some burden to wearing them
# - hands or similar, maybe a tentacle, hold things
# - some other system determines things like appearance
# - it might tell npcs that your appearance is ridiculous because you're
#   wearing five pairs of socks
# - a separate system does it so that anything that can have an appearance can
#   be queried

