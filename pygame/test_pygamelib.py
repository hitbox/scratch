import unittest

from pygamelib import InputLine
from pygamelib import itertouching
from pygamelib import merge_all_rects
from pygamelib import merge_ranges
from pygamelib import merge_rects
from pygamelib import modo
from pygamelib import point_on_axisline
from pygamelib import snake_case

class TestSnakeCaseFunction(unittest.TestCase):

    def test_simple(self):
        self.assertEqual(snake_case('PascalCase'), 'pascal_case')

    def test_underscore_in_pascal(self):
        # not sure what to do if underscores are in pascal case
        with self.assertRaises(ValueError):
            snake_case('Pascal_Case')

    def test_weird(self):
        self.assertEqual(snake_case('PC'), 'pc')
        # leave runs of caps alone
        self.assertEqual(snake_case('XML'), 'xml')

    def test_todo_fix_loses_parts(self):
        # FIXME
        # - loses the XML part
        self.assertEqual(snake_case('XMLShapes'), 'shapes')


class TestPointOnAxisLine(unittest.TestCase):

    def test_horizontal_line(self):
        line = ((0,0), (10,0))
        self.assertTrue(point_on_axisline((0,0), line))
        self.assertTrue(point_on_axisline((5,0), line))
        self.assertTrue(point_on_axisline((10,0), line))

        self.assertFalse(point_on_axisline((-1,0), line))
        self.assertFalse(point_on_axisline((11,0), line))
        self.assertFalse(point_on_axisline((5,5), line))

    def test_vertical_line(self):
        line = ((0,0), (0,10))
        self.assertTrue(point_on_axisline((0,0), line))
        self.assertTrue(point_on_axisline((0,5), line))
        self.assertTrue(point_on_axisline((0,10), line))

        self.assertFalse(point_on_axisline((0,-1), line))
        self.assertFalse(point_on_axisline((0,11), line))
        self.assertFalse(point_on_axisline((5,5), line))

    def test_horizontal_line_reversed(self):
        # when the line is two points not in normal axis order
        line = ((10,0), (0,0))
        self.assertTrue(point_on_axisline((0,0), line))
        self.assertTrue(point_on_axisline((5,0), line))
        self.assertTrue(point_on_axisline((10,0), line))

    def test_vertical_line_reversed(self):
        line = ((0,10), (0,0))
        self.assertTrue(point_on_axisline((0,0), line))
        self.assertTrue(point_on_axisline((0,5), line))
        self.assertTrue(point_on_axisline((0,10), line))


class TestModOffset(unittest.TestCase):
    """
    Test modulo with offset.
    """

    def test_modulo_offset(self):
        c = 3
        n = 8
        self.assertEqual(modo(3, n, c), 3)
        self.assertEqual(modo(8, n, c), 3)
        self.assertEqual(modo(9, n, c), 4)
        self.assertEqual(modo(0, n, c), 5)


class TestGroupbyColumns(unittest.TestCase):

    def test_groupby_columns(self):
        pass


class TestMergeRanges(unittest.TestCase):

    def test_empty(self):
        self.assertEqual(merge_ranges([]), set())

    def test_sequence(self):
        expect = [(0,3)]
        test = list(merge_ranges([(0,1),(1,2),(2,3)]))
        self.assertEqual(test, expect)

    def test_identity(self):
        ranges = set([(0,1),(2,3),(4,5)])
        test = merge_ranges(ranges)
        self.assertEqual(test, ranges)

    def test_overlapping(self):
        test = merge_ranges([(0,3),(2,5),(3,10)])
        self.assertEqual(test, set([(0,10)]))
        test = merge_ranges([(0,10),(1,2),(3,5),(4,8)])
        self.assertEqual(test, set([(0,10)]))


class TestMergeRects(unittest.TestCase):

    def test_merge_rects_none(self):
        self.assertIsNone(
            merge_rects((0, 0, 10, 10), (15, 15, 10, 10))
        )

    def test_merge_rects_leftright(self):
        self.assertEqual(
            merge_rects((0, 0, 10, 10), (10, 0, 10, 10)),
            (0, 0, 20, 10),
        )
        self.assertEqual(
            merge_rects((10, 0, 10, 10), (0, 0, 10, 10)),
            (0, 0, 20, 10),
        )

    def test_merge_rects_topbottom(self):
        self.assertEqual(
            merge_rects((0, 0, 10, 10), (0, 10, 10, 10)),
            (0, 0, 10, 20),
        )

    def test_merge_rects_diagonal_is_none(self):
        # diagonals do not merge
        self.assertIsNone(
            merge_rects((0, 0, 10, 10), (10, 10, 10, 10)),
        )


class TestMergeAllRects(unittest.TestCase):

    def test_merge_all_none(self):
        no_merges_rects = [
            (0, 0, 10, 10),
            (20, 0, 10, 10),
            (0, 20, 10, 10),
        ]
        self.assertEqual(
            merge_all_rects(no_merges_rects),
            no_merges_rects,
        )

    def test_merge_all_square(self):
        square = [
            (0, 0, 10, 10),
            (10, 0, 10, 10),
            (0, 10, 10, 10),
            (10, 10, 10, 10),
        ]
        self.assertEqual(
            merge_all_rects(square),
            [(0, 0, 20, 20)],
        )

    def test_merge_all_four_to_two(self):
        rects = [
            (0, 0, 10, 10),
            (10, 0, 10, 10),
            (20, 20, 10, 10),
        ]
        # set to disregard order
        self.assertEqual(
            set(merge_all_rects(rects)),
            set([
                (0, 0, 20, 10),
                (20, 20, 10, 10),
            ]),
        )


class TestTouching(unittest.TestCase):

    def test_itertouching_none(self):
        self.assertEqual(
            set(itertouching((0,0,10,10), [(20,20,10,10)])),
            set(),
        )

    def test_itertouching_topbottom(self):
        self.assertEqual(
            set(itertouching((0,0,10,10), [(0,-10,10,10)])),
            {(0,-10,10,10)},
        )

    def test_itertouching_bottomtop(self):
        self.assertEqual(
            set(itertouching((0,0,10,10), [(0,10,10,10)])),
            {(0,10,10,10)},
        )

    def test_itertouching_leftright(self):
        self.assertEqual(
            set(itertouching((0,0,10,10), [(10,0,10,10)])),
            {(10,0,10,10)},
        )

    def test_itertouching_rightleft(self):
        self.assertEqual(
            set(itertouching((0,0,10,10), [(-10,0,10,10)])),
            {(-10,0,10,10)},
        )

    def test_itertouching_complex(self):
        self.assertEqual(
            set(itertouching(
                (0,0,10,10),
                [
                    (-5, 10, 10, 10), # below, right to mid
                    (5, 10, 10, 10), # below, left at mid
                    (10, -5, 10, 10), # above, to right, bottom mid height
                    (10, 5, 10, 10), # right of, top at mid height
                    (20, 20, 10, 10), # not touching
                ]
            )),
            {
                (-5, 10, 10, 10),
                (5, 10, 10, 10),
                (10, -5, 10, 10),
                (10, 5, 10, 10),
            },
        )


class TestFloodRectPair(unittest.TestCase):

    @unittest.expectedFailure
    def test_largest_visible_pair_right_to_left(self):
        self.assertEqual(
            largest_contiguous((0,0,10,10), (10,5,10,10)),
            (0,5,20,5),
        )

    @unittest.expectedFailure
    def test_largest_visible_pair_left_to_right(self):
        self.assertEqual(
            largest_contiguous((0,0,10,10), (-10,5,10,10)),
            (-10,5,20,5),
        )

    @unittest.expectedFailure
    def test_largest_visible_pair_top_to_bottom(self):
        self.assertEqual(
            largest_contiguous((0,0,10,10), (5,-10,10,10)),
            (5,-10,5,20),
        )

    @unittest.expectedFailure
    def test_largest_visible_pair_bottom_to_top(self):
        self.assertEqual(
            largest_contiguous((0,0,10,10), (5,10,10,10)),
            (5,0,5,20),
        )


class TestInputLine(unittest.TestCase):

    def setUp(self):
        self.input_line = InputLine()

    def test_addchar(self):
        self.input_line.addchar('a')
        self.assertEqual(self.input_line.line, 'a')

    def test_insert_after_left(self):
        self.input_line.addchar('b')
        self.input_line.caretleft()
        self.input_line.addchar('a')
        self.assertEqual(self.input_line.line, 'ab')

    def test_insert_after_right(self):
        self.input_line.addchar('a')
        self.input_line.addchar('c')
        self.input_line.caretleft()
        self.input_line.caretleft()
        self.input_line.caretright()
        self.input_line.addchar('b')
        self.assertEqual(self.input_line.line, 'abc')

    def test_backspace(self):
        self.input_line.addchar('a')
        self.input_line.addchar('b')
        self.input_line.backspace()
        self.assertEqual(self.input_line.line, 'a')
