# https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
import math

def dijkstra(graph, source):
    """
    :param graph:
    :param source: starting vertex.
    """
    unvisited = set(v for v in graph.get_vertices())
    dist = {vertex: math.inf for vertex in unvisited}
    dist[source] = 0
    prev = {vertex: None for vertex in unvisited}

    # assume undirected
    weights = {(v1, v2): cost for v1, v2, cost in graph.get_edges()}
    print(weights)

    # good graphics
    # https://favtutor.com/blogs/dijkstras-algorithm-cpp

    def least_weight(node):
        key = (current, node)
        return weights[key]

    while unvisited:
        print(unvisited)
        adjacents = [adjacent for adjacent in graph.get_neighbors(current) if adjacent in unvisited]
        if unvisited and not adjacents:
            current = next(iter(unvisited))
        else:
            current = min(adjacents, key=least_weight, default=None)
        unvisited.remove(current)
        print(current)
        continue
        neighbors = graph.get_neighbors(current)
        print(current, neighbors)
        for v in graph.get_neighbors(current):
            if v not in unvisited:
                continue
            alt = dist[current] + graph.get_edge(current, v)
            if alt < dist[v]:
                dist[v] = alt
                prev[v] = current

    return dist, prev
