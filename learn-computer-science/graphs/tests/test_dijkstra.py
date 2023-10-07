import unittest

from graphs.adjacency_matrix import AdjacencyMatrix
from graphs.dijkstra import dijkstra

def graph1():
    # https://favtutor.com/blogs/dijkstras-algorithm-cpp
    graph = AdjacencyMatrix(5)
    graph.set_vertex(0, 'a')
    graph.set_vertex(1, 'b')
    graph.set_vertex(2, 'c')
    graph.set_vertex(3, 'd')
    graph.set_vertex(4, 'e')
    graph.set_edge('a', 'b', cost=10, directed=True)
    graph.set_edge('a', 'c', cost=3, directed=True)
    graph.set_edge('b', 'c', cost=1, directed=True)
    graph.set_edge('b', 'd', cost=2, directed=True)
    graph.set_edge('c', 'b', cost=4, directed=True)
    graph.set_edge('c', 'd', cost=8, directed=True)
    graph.set_edge('c', 'e', cost=2, directed=True)
    graph.set_edge('d', 'e', cost=7, directed=True)
    graph.set_edge('e', 'd', cost=9, directed=True)
    return graph

class TestDijkstra(unittest.TestCase):
    """
    """

    def setUp(self):
        """
        """
        self.graph = graph1()

    def test_dijkstra(self):
        dist, prev = dijkstra(self.graph, 'a')
        print(dist, prev)

        raise NotImplementedError


if __name__ == '__main__':
    unittest.main()
