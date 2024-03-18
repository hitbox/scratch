# Was looking at this:
# https://lpython.org/blog/2023/07/lpython-novel-fast-retargetable-python-compiler/#ahead-of-time-aot-compilation-1
# Wanted to rewrite their algorithm in plain python and without lpython
import argparse

from math import inf
from itertools import product
from itertools import repeat

def dijkstra_shortest_path(n, source):
    #i: i32; j: i32; v: i32; u: i32; mindist: i32; alt: i32; dummy: i32; uidx: i32
    #dist_sum: i32;
    graph = {}
    dist = {}
    prev = {}
    visited = {}
    Q = []

    for i in range(n):
        for j in range(n):
            graph[n * i + j] = abs(i - j)

    for v in range(n):
        dist[v] = 2147483647
        prev[v] = -1
        Q.append(v)
        visited[v] = False
    dist[source] = 0

    while len(Q) > 0:
        u = -1
        mindist = 2147483647
        for i in range(len(Q)):
            if mindist > dist[Q[i]]:
                mindist = dist[Q[i]]
                u = Q[i]
                uidx = i
        dummy = Q.pop(uidx)
        visited[u] = True

        for v in range(n):
            if v != u and not visited[v]:
                alt = dist[u] + graph[n * u + v]

                if alt < dist[v]:
                    dist[v] = alt
                    prev[v] = u

    dist_sum = 0
    for i in range(n):
        dist_sum += dist[i]
    return dist_sum

def dijkstra2(n, source):
    dist = [0 if i == source else inf for i in range(n)]
    visited = set()
    index_queue = list(range(n))

    graph = [None for _ in range(n*n)]
    for i, j in product(*repeat(range(n),2)):
        graph[n * i + j] = abs(i - j)

    assert None not in graph

    while index_queue:
        mindist = inf
        for qindex, qvalue in enumerate(index_queue):
            if mindist > dist[qvalue]:
                mindist = dist[qvalue]
                u = qvalue
                uidx = qindex
                assert uidx != len(index_queue) - 1

        # XXX
        # Wow this is so goofy. I bet it has nothing to do with Dijkstra's algorithm.
        index_queue.pop(uidx)
        visited.add(u)

        #u = index_queue.pop()
        #visited.add(u)

        for v in set(range(n)).difference(visited):
            alt = dist[u] + graph[n * u + v]
            if alt < dist[v]:
                dist[v] = alt
    return sum(dist)

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('name', choices=['dijkstra_shortest_path', 'dijkstra2'])
    args = parser.parse_args(argv)

    func = globals()[args.name]

    n = 4000
    # this is what I got running their code without changing anything but the
    # typehints
    answer = 7998000

    result = func(n, 0)
    assert result == answer, f'{result} != {answer}'

if __name__ == '__main__':
    main()
