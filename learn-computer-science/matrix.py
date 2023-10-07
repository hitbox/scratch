import operator
import unittest

from itertools import starmap
from itertools import tee
from operator import mul

class TestMatrix(unittest.TestCase):
    """
    Test matrix operations.
    """
    # data taken from:
    # https://www.mathsisfun.com/algebra/matrix-multiplying.html

    def test_add(self):
        A = [[3,8],
             [4,6]]
        B = [[4, 0],
             [1,-9]]
        C = [[7, 8],
             [5,-3]]
        self.assertEqual(add(A, B), C)

    def test_dotproduct_1(self):
        A = [[1,2,3],
             [4,5,6]]
        B = [[ 7, 8],
             [ 9,10],
             [11,12]]
        C = [[ 58, 64],
             [139,154]]
        self.assertEqual(dotproduct(A,B), C)

    def test_dotproduct_2(self):
        # pies sold - example only show first row/col result
        A = [[3,4,2]]
        B = [[13],
             [ 8],
             [ 6]]
        C = dotproduct(A,B)
        self.assertEqual(C[0][0], 83)


def add(A, B):
    """
    Add matrices A and B.
    """
    return [[sum(vals) for vals in zip(*rows)] for rows in zip(A, B)]

def dotproduct(A, B):
    """
    The dot product of matrices A and B.
    """
    # NOTE: This idea of saving positions as we go and figuring out the
    #       dimensions late was my first idea for resizing after the operation.
    #       Could have taken the minimum row/column size of the matrices.
    # TODO: performance test of this vs. that.
    return [ [sum(starmap(mul, zip(A_row, B_col))) for B_col in zip(*B)] for A_row in A]

# TODO:
# determinant of matrix
# https://www.mathsisfun.com/algebra/matrix-determinant.html

if __name__ == '__main__':
    unittest.main()
