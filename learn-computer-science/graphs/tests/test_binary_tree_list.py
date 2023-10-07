import unittest

from graphs.binary_tree_list import BinaryTree

class TestBinaryTreeList(unittest.TestCase):

    def setUp(self):
        """
        0            A
        1      B          C
        2   D     Z     Y   F
        3  X W   G H   I J

        len() == 13

        level/depth
        |
        |   number of elements at level
        |   |
        |   |       index slice at level
        |   |       |
        |   |       |
        0   1    0:1               0
        1   2    1:3        1             2
        2   4    3:7     3     4       5     6
        3   8    7:15   7 8   9 10   11 12

        4   16  15:33
        bottom row is my guess
        """
        self.tree = BinaryTree(
            'A', 'B', 'C', 'D', 'Z', 'Y', 'F', 'X', 'W', 'G', 'H', 'I', 'J')

    def test_left_child(self):
        "Testing returning the index of the left child of a given node."
        # right child of root
        child = self.tree.left_child_index(0)
        value = self.tree._tree[child]
        self.assertEqual(value, 'B')

    def test_right_child(self):
        "Testing returning the index of the right child of a given node."
        # right child of root
        child_index = self.tree.right_child_index(0)
        value = self.tree._tree[child_index]
        self.assertEqual(value, 'C')

    def test_count(self):
        "Test counting the number of nodes at a given level."
        # better name than "count"
        n = self.tree.count(0)
        self.assertEqual(n, 1)
        #
        n = self.tree.count(3)
        self.assertEqual(n, 8)

    def test_level_indices(self):
        "Test returning start, length tuple for given level."
        i, j = self.tree.level_indices(3)
        self.assertEqual(self.tree._tree[i:j], ['X', 'W', 'G', 'H', 'I', 'J'])

    def test_depth(self):
        "Test depth calculation."
        self.assertEqual(self.tree.depth(), 3)
        # empty trees?
        self.assertEqual(BinaryTree().depth(), 0)
        self.assertEqual(BinaryTree('A').depth(), 0)

    def test_insert(self):
        raise NotImplementedError


if __name__ == '__main__':
    unittest.main()
