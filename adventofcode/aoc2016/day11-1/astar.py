import heapq
from .utils import indent

class PriorityQueue:

    def __init__(self, *elements):
        self.elements = []
        for element in elements:
            self.put(*element)

    def __bool__(self):
        return bool(self.elements)

    def __len__(self):
        return len(self.elements)

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        priority, item = heapq.heappop(self.elements)
        return item


class Heuristic(object):

    def __init__(self, goal):
        self.cache = {}
        for fn, floor in enumerate(goal.floors, start=1):
            for item in floor:
                self.cache[item] = fn
        self.goal = goal

    def __call__(self, from_):
        cost = 0
        cost = 1 + (from_.elevator - self.goal.elevator)

        for fn, floor in enumerate(from_.floors, start=1):
            for item in floor:
                cost += abs(fn - self.cache[item])

        return cost


def find(start, goal):
    heuristic = Heuristic(goal)

    frontier = PriorityQueue((start, 0))

    came_from = {start: None}
    cost_so_far = {start: 0}
    rank_key = lambda item: item[0]

    while frontier:
        current = frontier.get()

        if current is goal:
            break

        for neighbor in current.neighbors():
            cost = cost_so_far[current] + current.cost(neighbor)

            if neighbor not in cost_so_far or cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = cost
                rank = cost + heuristic(neighbor)
                frontier.put(neighbor, rank)
                came_from[neighbor] = current

    return came_from, cost_so_far

def draw(came_from, start, goal):
    print(goal)
    print()

    v = came_from[goal]
    if v is not None:
        print(v)
        print()

    steps = 2
    while True:
        v = came_from[v]
        print(v)
        if v == start:
            break
        steps += 1
        print()

    print('Solved in %s steps' % steps)
