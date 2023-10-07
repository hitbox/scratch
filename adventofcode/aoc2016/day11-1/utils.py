import os

def indent(fac, n=1, char=' '):
    indent = char * n
    lines = str(fac).splitlines()
    lines = (indent + line for line in lines)
    return '\n'.join(lines)

def pprintstr(d, level=0):
    if not isinstance(d, dict):
        print(indent('-' * 17 + '\n' + str(d), level))
        return
    for k,v in d.items():
        print(indent('-' * 17 + '\n' + str(k), level))
        pprintstr(v, level+1)

def load():
    return open(os.path.join(os.path.dirname(__file__), 'input.txt')).read()

def make_goal(start):
    goal = start.copy()
    items = goal.items()
    goal.clear()
    goal.elevator = 3
    goal.floors[-1] = items
    return goal
