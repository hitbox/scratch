import heapq
import os

def puzzle(number):
    return open(os.path.join('data', 'input%s.txt' % number))

def isint(s):
    try:
        int(s)
    except ValueError:
        return False
    else:
        return True

def path(previous, goal):
    return [] if goal is None else path(previous, previous[goal]) + [goal]

def astar(start, heuristic, moves):
    frontier = [(heuristic(start), start)]

    previous = {start: None}
    costs = {start: 0}

    while frontier:
        _, current = heapq.heappop(frontier)

        if heuristic(current) == 0:
            return path(previous, current)

        for neighbor in moves(current):
            cost = costs[current] + 1
            if neighbor not in costs or cost < costs[neighbor]:
                heapq.heappush(frontier, (cost + heuristic(neighbor), neighbor))
                costs[neighbor] = cost
                previous[neighbor] = current
