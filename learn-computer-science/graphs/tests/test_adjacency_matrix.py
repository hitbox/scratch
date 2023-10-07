import unittest

from graphs.adjacency_matrix import AdjacencyMatrix

class TestAdjacencyMatrixSample(unittest.TestCase):
    """
    Expected values scraped from run on their web site.
    """

    def setUp(self):
        self.graph = AdjacencyMatrix(6)
        self.graph.set_vertex(0, 'a')
        self.graph.set_vertex(1, 'b')
        self.graph.set_vertex(2, 'c')
        self.graph.set_vertex(3, 'd')
        self.graph.set_vertex(4, 'e')
        self.graph.set_vertex(5, 'f')
        self.graph.set_edge('a', 'e', 10)
        self.graph.set_edge('a', 'c', 20)
        self.graph.set_edge('c', 'b', 30)
        self.graph.set_edge('b', 'e', 40)
        self.graph.set_edge('e', 'd', 50)
        self.graph.set_edge('f', 'e', 60)

    def test_sample_vertices(self):
        vertices = self.graph.get_vertices()
        expect = ['a', 'b', 'c', 'd', 'e', 'f']
        self.assertEqual(vertices, expect)

    def test_sample_edges(self):
        edges = self.graph.get_edges()
        expect = [
            ('a', 'c', 20), ('a', 'e', 10), ('b', 'c', 30), ('b', 'e', 40),
            ('c', 'a', 20), ('c', 'b', 30), ('d', 'e', 50), ('e', 'a', 10),
            ('e', 'b', 40), ('e', 'd', 50), ('e', 'f', 60), ('f', 'e', 60)]
        self.assertEqual(edges, expect)

    def test_sample_matrix(self):
        matrix = self.graph.get_matrix()
        expect = [
            [-1, -1, 20, -1, 10, -1], [-1, -1, 30, -1, 40, -1],
            [20, 30, -1, -1, -1, -1], [-1, -1, -1, -1, 50, -1],
            [10, 40, -1, 50, -1, 60], [-1, -1, -1, -1, 60, -1]]
        self.assertEqual(matrix, expect)

    def test_sample_remove_vertex(self):
        self.graph.remove_vertex('a')
        self.assertEqual(self.graph.get_vertices(), ['b', 'c', 'd', 'e', 'f'])
        # TODO:
        # remove edges involved with vertex

    def test_sample_remove_edge(self):
        """
        Remove an edge and test list of edges returned.
        """
        self.graph.remove_edge('a', 'e')
        result = self.graph.get_edges()
        expect = [
            ('a', 'c', 20), ('b', 'c', 30), ('b', 'e', 40), ('c', 'a', 20),
            ('c', 'b', 30), ('d', 'e', 50), ('e', 'b', 40), ('e', 'd', 50),
            ('e', 'f', 60), ('f', 'e', 60)]
        self.assertEqual(result, expect)
        # TODO:
        # see test_sample_remove_vertex


class TestAdjacencyMatrixClaw(unittest.TestCase):
    """
    A claw graph (only one vertex is connected to all others) test.
    """

    def setUp(self):
        self.graph = AdjacencyMatrix(4)
        vertices = list('abcd')
        for index, label in enumerate(vertices):
            self.graph.set_vertex(index, label)
        self.graph.set_edge('a', 'd')
        self.graph.set_edge('b', 'd')
        self.graph.set_edge('c', 'd')

    def test_claw_matrix(self):
        n = AdjacencyMatrix.notset
        c = AdjacencyMatrix.default_cost
        # right side and bottom set, except bottom-right.
        expect = [[n,n,n,c],
                  [n,n,n,c],
                  [n,n,n,c],
                  [c,c,c,n]]
        self.assertEqual(self.graph.adjacency_matrix, expect)


class TestAdjacencyMatrixCycle(unittest.TestCase):

    def setUp(self):
        self.graph = AdjacencyMatrix(4)
        vertices = list('abcd')
        for index, label in enumerate(vertices):
            self.graph.set_vertex(index, label)
        self.graph.set_edge('a', 'b')
        self.graph.set_edge('b', 'c')
        self.graph.set_edge('c', 'd')
        self.graph.set_edge('d', 'a')

    def test_cycle_matrix(self):
        # NOTE: vertices are connected in a cycle a -> b -> c -> d -> a
        n = AdjacencyMatrix.notset
        c = AdjacencyMatrix.default_cost
        expect = [[n,c,n,c],
                  [c,n,c,n],
                  [n,c,n,c],
                  [c,n,c,n]]
        self.assertEqual(self.graph.adjacency_matrix, expect)


class TestAdjacencyMatrixComplete(unittest.TestCase):
    """
    A complete graph (all vertices connected with edges to all others) test.
    """

    def setUp(self):
        self.graph = AdjacencyMatrix(4)
        vertices = list('abcd')
        for index, label in enumerate(vertices):
            self.graph.set_vertex(index, label)
        # connect all to all
        for label in vertices:
            for other in vertices:
                if label != other:
                    self.graph.set_edge(label, other)

    def test_complete_matrix(self):
        # NOTE:
        # * They use -1 as the not-set value and 0 as exists with a cost of
        #   zero, from geeksforgeeks.
        # * Most others use zero (0) for unset and one (1) for set.
        n = AdjacencyMatrix.notset
        c = AdjacencyMatrix.default_cost
        # NOTE: all set except along the diagonal
        expect = [[n,c,c,c],
                  [c,n,c,c],
                  [c,c,n,c],
                  [c,c,c,n]]
        self.assertEqual(self.graph.adjacency_matrix, expect)


if __name__ == '__main__':
    unittest.main()
