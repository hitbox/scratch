# Copied from:
# https://ide.geeksforgeeks.org/9je5j6jJ13
# and seasoned to taste.

class AdjacencyMatrix:
    """
    Adjacency Matrix is a 2D array of size V x V where V is the number of
    vertices in a graph. Let the 2D array be adj[][], a slot adj[i][j] = 1
    indicates that there is an edge from vertex i to vertex j. Adjacency matrix
    for undirected graph is always symmetric. Adjacency Matrix is also used to
    represent weighted graphs. If adj[i][j] = w, then there is an edge from
    vertex i to vertex j with weight w.

    Pros: Representation is easier to implement and follow. Removing an edge
          takes O(1) time. Queries like whether there is an edge from vertex
          ‘u’ to vertex ‘v’ are efficient and can be done O(1).

    Cons: Consumes more space O(V^2). Even if the graph is sparse(contains less
          number of edges), it consumes the same space. Adding a vertex is
          O(V^2) time.
    """
    notset = -1
    default_cost = 0

    def __init__(self, nvertices):
        """
        :param nvertices: the number of vertices.
        """
        self.nvertices = nvertices
        self.adjacency_matrix = [[self.notset]*self.nvertices for _ in range(self.nvertices)]
        self.vertices = {}
        self.vertices_list = [0]*self.nvertices

    def set_vertex(self, vertex, id):
        """
        :param vertex: index of vertex.
        :param id: name of vertex.
        """
        # TODO: let this raise IndexError?
        if 0 <= vertex <= self.nvertices:
            self.vertices[id] = vertex
            self.vertices_list[vertex] = id

    def set_edge(self, vertex1, vertex2, directed=False, cost=None):
        """
        :param vertex1: id of first vertex.
        :param vertex2: id of second vertex.
        :param cost: Optional cost of edge.
        :param directed: Optional boolean if edge is directed. Default: False.
        """
        if cost is None:
            cost = self.default_cost
        vertex1 = self.vertices[vertex1]
        vertex2 = self.vertices[vertex2]
        self.adjacency_matrix[vertex1][vertex2] = cost
        if not directed:
            self.adjacency_matrix[vertex2][vertex1] = cost

    def remove_vertex(self, id):
        self.vertices_list.remove(id)
        self.vertices.pop(id)

    def remove_edge(self, vertex1, vertex2):
        i = self.vertices_list.index(vertex1)
        j = self.vertices_list.index(vertex2)
        self.adjacency_matrix[i][j] = self.notset
        # ensure undirected edge is removed too
        self.adjacency_matrix[j][i] = self.notset

    def get_edge(self, vertex1, vertex2):
        i = self.vertices_list.index(vertex1)
        j = self.vertices_list.index(vertex2)
        return self.adjacency_matrix[i][j]

    def get_vertices(self):
        return self.vertices_list

    def get_edges(self):
        edges = []
        for i in range(self.nvertices):
            for j in range(self.nvertices):
                if (self.adjacency_matrix[i][j] != self.notset):
                    vertex1 = self.vertices_list[i]
                    vertex2 = self.vertices_list[j]
                    cost = self.adjacency_matrix[i][j]
                    edge = (vertex1, vertex2, cost)
                    edges.append(edge)
        return edges

    def get_matrix(self):
        return self.adjacency_matrix

    def get_neighbors(self, vertex):
        for v1, v2, cost in self.get_edges():
            if vertex in (v1, v2):
                yield (v1, v2, cost)
