import argparse

from collections import deque

def find_path_backtracking(graph, start, end, path=None):
    if path is None:
        path = [start]
    if start == end:
        return path
    for node in graph.get(start, []):
        if node not in path:  # Avoid cycles
            new_path = find_path_backtracking(graph, node, end, path + [node])
            if new_path:
                return new_path
    return None

def find_path_functional(graph, start, end):
    def helper(current, path):
        if current == end:
            return path
        for node in graph.get(current, []):
            if node not in path:  # Avoid cycles
                result = helper(node, path + [node])
                if result:
                    return result
        return None

    return helper(start, [start])

def find_path_dfs(graph, start, end):
    stack = [(start, [start])]
    while stack:
        (current, path) = stack.pop()
        if current == end:
            return path
        for node in graph.get(current, []):
            if node not in path:
                stack.append((node, path + [node]))
    return None

def find_path_bfs(graph, start, end):
    queue = deque([(start, [start])])
    while queue:
        (current, path) = queue.popleft()
        if current == end:
            return path
        for node in graph.get(current, []):
            if node not in path:
                queue.append((node, path + [node]))
    return None

def demo_all_functions():
    graph = {
        'A': ['B', 'C'],
        'B': ['D'],
        'C': ['D'],
        'D': ['E'],
        'E': []
    }

    path = find_path_backtracking(graph, 'A', 'E')
    print("Path found (backtracking):", path)

    path_functional = find_path_functional(graph, 'A', 'E')
    print("Path found (functional):", path_functional)

    path_dfs = find_path_dfs(graph, 'A', 'E')
    path_bfs = find_path_bfs(graph, 'A', 'E')

    print("Path found (DFS):", path_dfs)
    print("Path found (BFS):", path_bfs)

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

    demo_all_functions()

if __name__ == '__main__':
    main()

# 2024-10-13 Sun.
# - "Can Logic Programming Be Liberated from Predicates and Backtracking?"
#   https://www-ps.informatik.uni-kiel.de/~mh/papers/WLP24.pdf
# - Paper analysed and digested into Python by chatgpt.
