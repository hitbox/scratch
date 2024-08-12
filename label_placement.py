import unittest

class TestPlacement(unittest.TestCase):

    def test_already_separated(self):
        self.assertEqual([0], place([0], 10))
        self.assertEqual([0, 10], place([0, 10], 10))
        self.assertEqual([-10, 0, 10], place([-10, 0, 10], 10))

    def test_already_separated_but_outside_limits(self):
        self.assertEqual([-10], place_with_limits([-20], 10, -10, 10));
        self.assertEqual([10], place_with_limits([20], 10, -10, 10));
        self.assertEqual([-10, 10], place_with_limits([-20, 20], 10, -10, 10));


class Cluster:

    def __init__(self, position):
        self.start = position
        self.end = position
        self.min_offset = 0
        self.max_offset = 0

    def merge(self, first, second, separation):
        first.shift(second.start - first.end - separation)
        self.start = first.start
        self.end = second.end
        self.min_offset = min(first.min_offset, second.min_offset)
        self.max_offset = max(first.max_offset, second.max_offset)
        self.balance()
        return self

    def shift(self, offset):
        self.start += offset
        self.end += offset
        self.min_offset += offset
        self.min_offset += offset

    def balance(self):
        imbalance = (self.min_offset + self.max_offset) / 2
        if imbalance != 0:
            self.shift(-imbalance)

    def limit(self, min, max):
        if self.start < min:
            self.shift(min - self.start)

        if self.end > max:
            self.shift(max - self.end)


class ClusterList:

    def __init__(self, separation, capacity):
        self.vec = []
        self.separation = separation
        self.capacity = capacity

    def pop_if_not_separate(self, cluster):
        if self.vec:
            previous = self.vec[-1]
            if previous and previous.end + self.separation > cluster.start:
                return self.vec.pop()

    def push(self, cluster):
        self.vec.append(cluster)

    def positions(self):
        positions = []

        for cluster in self.vec:
            position = cluster.start
            while position <= cluster.end:
                positions.append(position)
                position += self.separation

        return positions


def place(positions, separation):
    clusters = ClusterList(separation, len(positions))

    for position in positions:
        cluster = Cluster(position)

        while (previous := clusters.pop_if_not_separate(cluster)):
            cluster = Cluster.merge(previous, cluster, separation)

        clusters.push(cluster)

    return clusters.positions()

def place_with_limits(positions, separation, min, max):
    clusters = ClusterList(separation, len(positions))

    for position in positions:
        cluster = Cluster(position).limit(min, max)

        while cluster and (previous := cluster.pop_if_not_separate(cluster)):
            cluster = Cluster.merge(previous, cluster, separation)

        clusters.push(cluster)

    return clusters.positions()

# https://github.com/KateMorley/vertical_label_placement/blob/main/src/lib.rs
