from pprint import pprint as pp
import logging

from . import UP, DOWN, astar
from .facility import Facility
from .utils import make_goal

TEXT = ("The first floor contains a hydrogen-compatible microchip and a"
        " lithium-compatible microchip.\n"
        "The second floor contains a hydrogen generator.\n"
        "The third floor contains a lithium generator.\n"
        "The fourth floor contains nothing relevant.\n")

LINESEP = '-' * 17

def test1():
    log = logging.getLogger('test1')
    p = log.debug
    #p = print
    facility = Facility(TEXT)
    assert facility.safe()
    moves = [(UP,   ('HM', )),
             (UP,   ('HG', 'HM')),
             (DOWN, ('HM', )),
             (DOWN, ('HM', )),
             (UP,   ('HM', 'LM')),
             (UP,   ('HM', 'LM')),
             (UP,   ('HM', 'LM')),
             (DOWN, ('HM', )),
             (UP,   ('HG', 'LG')),
             (DOWN, ('LM', )),
             (UP,   ('HM', 'LM'))]
    for move in moves:
        p(LINESEP)
        p(facility)
        assert not facility.solved()
        facility = facility.move(*move)
        assert facility.safe()

    assert facility.directions() == (DOWN, )
    assert facility.solved()
    p(LINESEP)
    p(facility)

def test_safe():
    f = Facility("hydrogen-compatible microchip, lithium generator\nhydrogen generator\nlithium microchip\n")
    assert not f.safe()

def test2():
    start = Facility(TEXT)
    goal = make_goal(start)

    came_from, cost = astar.find(start, goal)

    if came_from and cost:
        astar.draw(came_from, start, goal)

def run():
    test_safe()
    test1()
    test2()
