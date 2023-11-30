import itertools as it

from collections import defaultdict

deltas = set(tuple(x - 1 for x in divmod(i, 3)) for i in range(9))
deltas.remove((0,0))

def is_alive(state, other, count):
    return (
        (count in {2, 3} and other in state)
        or
        (count == 3 and other not in state)
    )

def neighbor_counts(state):
    counts = defaultdict(int)
    for row, col in state:
        for drow, dcol in deltas:
            other = (row + drow, col + dcol)
            counts[other] += 1
    return counts

def evolve(state):
    neighbors = neighbor_counts(state)
    container = type(state)
    return container(
        other for other, count in neighbors.items()
        if is_alive(state, other, count)
    )

def evolve_generator(state):
    """
    Generate evolving states with their indexes. After a duplicate is detected
    states are taken from a list with repeating indexes.
    """
    yield (state, 0)

    states = [state]
    for index in it.count(1):
        state = evolve(state)
        if state in states:
            start_index = states.index(state)
            break
        else:
            states.append(state)
            yield (state, index)

    repeating_indexes = it.cycle(range(start_index, len(states)))
    for index in repeating_indexes:
        yield (states[index], index)

# 2023-11-23
# - https://realpython.com/conway-game-of-life-python/
