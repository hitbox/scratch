import enum
import unittest

class TestLineMovement(unittest.TestCase):

    def test_next_move(self):
        raise ValueError


class PencilStates(enum.Enum):
    STOPPED = enum.auto() # can start tracing or, possibly, drawing
    TRACING = enum.auto() # can stop, reverse
    DRAWING = enum.auto() # can't stop until collision


# next valid states
PencilStates.STOPPED.next_ = [
    PencilStates.TRACING,
    PencilStates.DRAWING,
]

PencilStates.TRACING.next_ = [
    PencilStates.STOPPED,
    PencilStates.TRACING, # continue tracing
    PencilStates.DRAWING,
]

PencilStates.DRAWING.next_ = [
    PencilStates.DRAWING, # continue drawing
    PencilStates.STOPPED, # must be on a line, ie tracing
]

# don't need STOPPED?

# idea from ChatGPT:
# - some parts of the line are "slippery" or something
# - when your pencil hits them, the game zooms into a balancing game where you
#   try to stay on the line.
# - enemies could bounce around and coat your lines with grease or something
# - if you complete the minigame the enemy who made your line dangerous, dies
# - if not, you lose a life or turn or whatever
# - maybe slippery lines cannot be used to complete a drawing line

# boost powerup
# - a powerup on the starting lines that gives you a one-time boost to shoot
#   across and complete a line.
# - start player across from powerup
# - too many enemies for your normal movement speed to complete
# - trace lines to get powerup
# - shoot across and complete otherwise impossible puzzle

def is_valid_line_move(current, next_, lines, drawing_points, walls):

    # is drawing if current is on a line

    # if not drawing, then tracing:
    #     if next_ is on same line: valid and can reverse direction
    #     if next_ is not on any line: valid--starts drawing new line
    #
    # if is drawing:
    #     if next position goes back on drawing line, invalid and prevent
    #     if next position goes through own drawing line, invalid and kill
    #     movement path goes through a line in lines, stop on intersection
    #     movement path goes into a wall, stop at border of wall
    pass
