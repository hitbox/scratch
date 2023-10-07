# source:
# https://techprodezza.code.blog/2021/01/23/representation-of-binary-tree-array/
# TODO:
# * some kind of treatment like adjacency_matrix.py
# * how to add beyond length?
# * they use 1-indexed list?

# This code represents Fig 2.
# depth of the tree=3
# Total nodes = 2^3 - 1 = 7

tree = ['A', 'B', 'C', 'D', None, None, 'F']

#'None' is used to indicate that there exists no children or nodes.

def get_right_child(i):
    # node is not null
    # and the result must lie within the number of nodes for a full binary tree
    if tree[i] is not None and ((2*i)+1) <= len(tree):
        return (2*i)+1
    # if right child doesn't exist
    return -1

def get_left_child(i):
    # node is not null
    # and the result must lie within the number of nodes for a full binary tree
    if tree[i] is not None and (2*i)<=len(tree):
        return 2*i
    # if left child doesn't exist
    return -1

def get_parent(i):
    if tree[i] is not None and tree[i//2] is not None:
        return tree[i//2]
    # if root
    return -1

class BinaryTree:
    # TODO
    # * generalize to n-children?

    def __init__(self, *level_order_elements):
        self._tree = list(level_order_elements)

    def _check_index(self, index):
        if (index <= len(self._tree)
                and self._tree[index] is not None):
            return index

    def left_child_index(self, parent):
        child = parent * 2 + 1
        return self._check_index(child)

    def right_child_index(self, parent):
        child = parent * 2 + 2
        return self._check_index(child)

    def value(self, index):
        return self._tree[index]

    def depth(self):
        d = 0
        t = self.count(d)
        while t < len(self._tree):
            d += 1
            t += self.count(d)
        return d

    def insert(self, node):
        raise NotImplementedError

    def count(self, level):
        # number of elements at level
        return 2 ** level

    def level_indices(self, level):
        c = self.count(level)
        i = c - 1
        j = c * 2 - 1
        return (i, j)

    def testfunc(self):
        i = 0
        d = 1
        print(f'{d=} {self.value(i)}')
        while i <= len(self._tree):
            d += 1
            print()
            child = self.left_child_index(i)
            if child is None:
                value = '_'
            else:
                value = self.value(child)
            print(f'{d=} {value}')
            #
            child = self.right_child_index(i)
            if child is None:
                value = '_'
            else:
                value = self.value(child)
            print(f'{d=} {value}')
            #
            i = (i + 1) * 2
