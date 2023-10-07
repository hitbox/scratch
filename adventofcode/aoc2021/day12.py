from collections import defaultdict

from util import input_filename

_day12_example_small = """\
start-A
start-b
A-c
A-b
b-d
A-end
b-end"""

_day12_example_larger = """\
dc-end
HN-start
start-kj
dc-start
dc-HN
LN-dc
HN-end
kj-sa
kj-HN
kj-dc"""

def parse_cavemap(string):
    graph = defaultdict(list)
    for line in string.splitlines():
        key, value = line.split('-')
        graph[key].append(value)
    return graph

def traverse(graph, v, visit):
    q = [v]
    marked = []

    def mark(v):
        visit(v)
        marked.append(v)

    mark(v)
    while q:
        w = q.pop()
        for x in graph[w]:
            if x not in marked:
                mark(x)
                q.append(x)

def day12_part1():
    """
    """
    # small example
    cavemap = parse_cavemap(_day12_example_small)
    for key in cavemap:
        print(key, ','.join(map(str, cavemap[key])))
    print()

    traverse(cavemap, 'start', print)
    return
    print()
    # larger example
    cavemap = parse_cavemap(_day12_example_larger)
    for path in iter_cavemap(cavemap, 'start'):
        print(path)
    print()


def day12_part2():
    """
    """

