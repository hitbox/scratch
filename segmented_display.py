import argparse

#   -- A --
#  |       |
#  F       B
#  |       |
#   -- G --
#  |       |
#  E       C
#  |       |
#   -- D --

segment_labels = 'ABCDEFG'

segments_for_digits = [
    {0, 2, 3, 5, 6, 7, 8, 9},
    {0, 1, 2, 3, 4, 7, 8, 9},
    {0, 1, 3, 4, 5, 6, 7, 8, 9},
    {0, 2, 3, 5, 6, 8, 9},
    {0, 2, 6, 8},
    {0, 4, 5, 6, 8, 9},
    {2, 3, 4, 5, 6, 8, 9},
]

class SegmentDisplay:

    def __init__(
        self,
        length = 1,
        horizontal = '-',
        vertical = '|',
        corner = ' ',
        blank = ' ',
    ):
        self.length = length
        self.horizontal = horizontal
        self.vertical = vertical
        self.corner = corner
        self.blank = blank

    def get_lines(self, segments):
        _lines = []
        center = self.blank * self.length

        char = self.horizontal if segments['A'] else self.blank
        _lines.append(self.corner + char * self.length + self.corner)

        right = self.vertical if segments['B'] else self.blank
        left = self.vertical if segments['F'] else self.blank
        for _ in range(self.length):
            _lines.append(left + center + right)

        char = self.horizontal if segments['G'] else self.blank
        _lines.append(self.corner + char * self.length + self.corner)

        right = self.vertical if segments['C'] else self.blank
        left = self.vertical if segments['E'] else self.blank
        for _ in range(self.length):
            _lines.append(left + center + right)

        char = self.horizontal if segments['D'] else self.blank
        _lines.append(self.corner + char * self.length + self.corner)

        return _lines


def segments(d):
    A = d in {0, 2, 3, 5, 6, 7, 8, 9}
    B = d in {0, 1, 2, 3, 4, 7, 8, 9}
    C = d in {0, 1, 3, 4, 5, 6, 7, 8, 9}
    D = d in {0, 2, 3, 5, 6, 8, 9}
    E = d in {0, 2, 6, 8}
    F = d in {0, 4, 5, 6, 8, 9}
    G = d in {2, 3, 4, 5, 6, 8, 9}
    return [A, B, C, D, E, F, G]

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--length', type=int, default=1)
    args = parser.parse_args(argv)

    segment_display = SegmentDisplay(length=args.length)

    lines_lines = []
    for d in range(10):
        data = dict(zip(segment_labels, segments(d)))
        lines = segment_display.get_lines(data)
        lines_lines.append(lines)

    for thingy in zip(*lines_lines):
        print((' ' * 5).join(thingy))

if __name__ == '__main__':
    main()
