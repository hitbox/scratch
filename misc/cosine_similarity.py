import argparse
import math
import unittest

class TestMagnitude(unittest.TestCase):

    def test_vector2d(self):
        self.assertEqual(magnitude((3,4)), 5)

    def test_vector3d(self):
        self.assertEqual(magnitude((1,2,3)), math.sqrt(14))


class TestTheta(unittest.TestCase):

    def test_theta2d(self):
        # 2d only
        # orthogonal
        self.assertEqual(theta2d((1,0), (0,1)), math.pi/2)
        # parallel
        self.assertEqual(theta2d((2,3), (4,6)), 0)

    def test_theta(self):
        # any dimensions
        # orthogonal
        self.assertEqual(theta((1,0), (0,1)), math.pi/2)
        # parallel
        self.assertEqual(theta((2,3), (4,6)), 0)
        self.assertEqual(theta((1,0,0,0), (0,1,0,0)), math.pi/2)


def magnitude(vector):
    return math.sqrt(sum(component*component for component in vector))

def dot_product(a_vector, b_vector):
    return sum(a * b for a, b in zip(a_vector, b_vector))

def theta(a_vector, b_vector):
    # angle between vectors
    # from the text book but throws domain errors for 0 > cos_theta > 1
    dot_p = dot_product(a_vector, b_vector)
    a_magnitude = magnitude(a_vector)
    b_magnitude = magnitude(b_vector)
    cos_theta = dot_p / (a_magnitude * b_magnitude)
    cos_theta = max(-1, min(1, cos_theta))
    return math.acos(cos_theta)

def theta2d(a_vector, b_vector):
    # stolen from pygame for 2d vectors
    assert len(a_vector) == len(b_vector) == 2
    ax, ay = a_vector
    bx, by = b_vector
    return math.atan2(by, bx) - math.atan2(ay, ax)

def cosine_similarity(a, b):
    # TODO
    # - ran out of time/interest before getting to the impetus here
    pass

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

if __name__ == '__main__':
    main()

# 2023-12-27
# https://montyanderson.net/writing/embeddings
# https://www.geeksforgeeks.org/cosine-similarity/
