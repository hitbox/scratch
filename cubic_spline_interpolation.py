import argparse
import contextlib
import math
import os

from itertools import pairwise
from itertools import repeat

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

# spline.js
# Cubic spline interpolation. Given a set of points, this code generates the
# system of linear equations that needs to be solved to find the coefficients
# of the cubic polynomials that interpolate the points. It uses the natural
# boundary conditions to complete the set of equations.

def build_spline_equations(xs, ys):
    """
    :param xs: xs is an array of x coordinates (sorted from left to right)
    :param ys is an array of corresponding y coordinates.

    For N points, returns a pair [A, b] where Ax = b represents the system of
    linear equations to solve to determine the coefficients of the cubic
    polynomials that interpolate the points. There are N-1 polynomials, so A is
    NxN and b is an array of N values.
    """
    # n_points is the number of points.
    n_points = len(xs)
    # n_polys is the number of (cubic) polynomials we interpolate between the
    # given points.
    n_polys = n_points - 1
    # n_coeffs is the number of coefficients they all have together (4 per
    # poly: ax^3 + bx^2 + cx + d).
    n_coeffs = 4 * n_polys

    # The matrix A is the coefficient matrix for the system of linear equations
    # we need to solve to find the coefficients of the polynomials.
    # It has n_coeffs rows and columns.
    # for each poly i, A[4*i][0..3] are the 4 coefficients of this poly.
    A = [[0 for _ in range(n_coeffs)] for _ in range(n_coeffs)]

    # The vector b is the right-hand side of the system of linear equations.
    # It has n_coeffs values.
    b = [0 for _ in range(n_coeffs)]

    # Now we start filling in the matrix A and vector b.
    # First, we fill in the constraints that the polynomials must pass through
    # the given points. This populates the first 2*n_polys rows.
    nrow = 0
    for i in range(n_polys):
        # Poly i passes through points i and i+1.
        A[nrow][4 * i] = xs[i] ** 3
        A[nrow][4 * i + 1] = xs[i] ** 2
        A[nrow][4 * i + 2] = xs[i]
        A[nrow][4 * i + 3] = 1
        b[nrow] = ys[i]

        A[nrow + 1][4 * i] = xs[i + 1] ** 3
        A[nrow + 1][4 * i + 1] = xs[i + 1] ** 2
        A[nrow + 1][4 * i + 2] = xs[i + 1]
        A[nrow + 1][4 * i + 3] = 1
        b[nrow + 1] = ys[i + 1]
        nrow += 2

    # Constraints for the first derivatives. This works on non-boundary points,
    # so it gives us (n_polys - 1) equations.
    for i in range(n_polys - 1):
        # Poly i and poly i+1 must have the same first derivative at point i+1.
        A[nrow][4 * i] = 3 * xs[i + 1] ** 2
        A[nrow][4 * i + 1] = 2 * xs[i + 1]
        A[nrow][4 * i + 2] = 1
        A[nrow][4 * (i + 1)] = -3 * xs[i + 1] ** 2
        A[nrow][4 * (i + 1) + 1] = -2 * xs[i + 1]
        A[nrow][4 * (i + 1) + 2] = -1
        nrow += 1

    # Constraints for the second derivatives. This also gives us (n_polys - 1)
    # equations.
    for i in range(n_polys - 1):
        # Poly i and poly i+1 must have the same second derivative at point i+1.
        A[nrow][4 * i] = 6 * xs[i + 1]
        A[nrow][4 * i + 1] = 2
        A[nrow][4 * (i + 1)] = -6 * xs[i + 1]
        A[nrow][4 * (i + 1) + 1] = -2
        nrow += 1

    # The final two equations come from the "natural" boundary conditions; the
    # first and last polys must have zero second derivative at the endpoints.
    A[nrow][0] = 6 * xs[0]
    A[nrow][1] = 2
    A[nrow + 1][4 * (n_polys - 1)] = 6 * xs[n_polys]
    A[nrow + 1][4 * (n_polys - 1) + 1] = 2

    return (A, b)

# eqsolve.js
# Code to solve a system of linear equations using Gauss-Jordan elimination.
# The main entry point is the solve() function.

# This code uses an array-of-arrays representation of 2D matrices, e.g.:
#
# let mat = [
#     [-1, 4, -2, -15],
#     [-4, 6, 1, -5],
#     [-6, -6, -2, -10],
# ];

def solve(A, b):
    """
    solve solves the system of linear equations Ax = b, where A is a matrix and
    b is an array representing a column vector. The solution x is returned as
    an array. solve throws an exception if the system doesn't have a unique
    solution.

    A is modified in place - it should be cloned outside this function if you
    want to preserve the original.
    """
    # Step 1: create the augmented matrix [A|b], while making sure all
    # dimensions match. The resulting matrix has R rows and R+1 columns.
    R = len(A)

    if R != len(b):
        raise RuntimeError('A and b must have the same number of rows')

    for i in range(R):
        if len(A[i]) != R:
            raise RuntimeError('A must be square')
        A[i].append(b[i])

    # Step 2: perform Gaussian elimination on the augmented matrix. This
    # modifies A to be in row echelon form.
    gauss_eliminate(A)

    # Step 3: back-substitution. This modifies A to be in reduced row echelon
    # form (Gauss-Jordan elimination).
    for i in range(R - 1, -1, -1):
        # For each row, take its pivot and divide the last column by it, then
        # eliminate the pivot from all rows above.
        pivot = A[i][i]
        if pivot == 0:
            raise RuntimeError('System has no unique solution')
        for j in range(i - 1, -1, -1):
            f = A[j][i] / pivot
            A[j][i] = 0
            A[j][R] -= A[i][R] * f
        A[i][i] = 1
        A[i][R] /= pivot

    # Step 4: extract the solution vector from the last column of A.
    x = []
    for i in range(R):
        x.append(A[i][R])

    return x

def find_pivot_row(arr, start_row, col):
    """
    findPivotRow finds the "pivot" row in arr, for column col and beginning
    with start_row. The pivot row is the row with the largest (in absolute
    value) element in column col among rows [start_row:arr.length). The index of
    the pivot row is returned.
    """
    maxidx = start_row
    for i in range(start_row, len(arr)):
        if abs(arr[i][col]) > abs(arr[maxidx][col]):
            maxidx = i
    return maxidx

def swap_rows(arr, i, j):
    """
    swapRows swaps rows i and j in arr, in place.
    """
    if i != j:
        tmp = arr[i]
        arr[i] = arr[j]
        arr[j] = tmp

def gauss_eliminate(arr):
    """
    gaussEliminate performs Gaussian elimination on arr, in place. After
    running, arr will be in row echelon form. It operates on arbitraryly sized
    matrices. This code follows the pseudocode from Wikipedia, with partial
    pivoting (https://en.wikipedia.org/wiki/Gaussian_elimination). It selects
    the largest possible absolute value for each column to improve numerical
    stability.
    """
    nrows = len(arr)
    ncols = len(arr[0])

    h = 0
    k = 0

    while (h < nrows and k < ncols):
        # Find the pivot row for column k.
        pivot_row = find_pivot_row(arr, h, k)
        if arr[pivot_row][k] == 0:
            # No pivot in this column; move on to the next one.
            k += 1
        else:
            # Swap current row with the pivot row, so we can use the pivot's
            # leading element to eliminate below.
            swap_rows(arr, h, pivot_row)

            for i in range(h + 1, nrows):
                f = arr[i][k] / arr[h][k]
                arr[i][k] = 0
                for j in range(k + 1, ncols):
                    arr[i][j] -= arr[h][j] * f
            h += 1
            k += 1

def linspace(start, end, numpoints):
    """
    linspace returns an array of numPoints values distributed linearly in the
    (inclusive) range [start,end], just like Numpy's linspace.
    """
    if numpoints < 2:
        return (start, end)

    step = (end - start) / (numpoints - 1)
    rv = [start + i * step for i in range(numpoints)]
    return rv

def nsinc(x):
    """
    calculates the normalized sinc(x) function and returns a y value.
    https://en.wikipedia.org/wiki/Sinc_function
    """
    if x == 0:
        return 1
    else:
        return math.sin(math.pi * x) / (math.pi * x)

def _cubic_spline_interpolate(xs, ys, N):
    # this was part of the next func before trying to python-ify it.
    for i in range(N):
        px = pxs[i]
        # Find the number of the curve for px, based on which points from xs
        # it's between. Can be done more efficiently with binary search, but
        # this is good enough for a demo.
        curve_index = -1
        for j in range(len(xs)):
            # is px between xs[j] and xs[j+1]? If yes, we found the curve!
            if px >= xs[j] and px <= xs[j + 1]:
                curve_index = j
                break
        if curve_index < 0:
            raise RuntimeError('curve index not found')

        # With the curve index in hand, we can calculate py based on the
        # relevant curve coefficients from coeffs.
        a, b, c, d = coeffs[curve_index * 4: curve_index * 4 + 4]
        pys[i] = a * px ** 3 + b * px ** 2 + c * px + d

def cubic_spline_interpolate(xs, ys, N):
    """
    doInterpolate uses cubic spline interpolation to create N new points
    between xs and calculates their ys, returning [pxs, pys] - the (x,y) coords
    of the interpolated points.
    """
    # Perform interpolation on xs, ys to get the coefficients of the splines.
    A, b = build_spline_equations(xs, ys)
    coeffs = solve(A, b)

    # Create N points linearly spaced between the min and max of xs, and
    # calculate the corresponding py for each px using the appropriate curve.
    pxs = linspace(min(xs), max(xs), N)

    def find_curve_index(px):
        for curve_index, (xs1, xs2) in enumerate(pairwise(xs)):
            if xs1 <= px <= xs2:
                return curve_index
        else:
            raise RuntimeError('curve index not found')

    def py_i(px, a, b, c, d):
        return a * px ** 3 + b * px ** 2 + c * px + d

    pys = list(repeat(0, N))
    for i, px in enumerate(pxs):
        curve_index = find_curve_index(px)
        a, b, c, d = coeffs[curve_index * 4: curve_index * 4 + 4]
        pys[i] = a * px ** 3 + b * px ** 2 + c * px + d

    return (pxs, pys)

def demo_data():
    # origXs, origYs is the original set of points we're going to be
    # interpolating between. They can be any length, as long as
    # origXs.length == origYs.length

    # const origXs = [0, 1, 2];
    # const origYs = [1, 3, 2];

    # const origXs = [0, 1, 2, 3, 4];
    # const origYs = [21, 24, 24, 18, 16];

    # nsinc function sampled on a few uniformly-spaced points.
    origXs = linspace(-10, 10, 7)
    origYs = list(map(nsinc, origXs))

    # Interpolate 200 points between the original points, using cubic spline
    # interpolation.
    pxs, pys = cubic_spline_interpolate(origXs, origYs, 200)

    return list(zip(pxs, pys))

def run():
    screen = pygame.display.set_mode((512,)*2)
    window = screen.get_rect()

    points = demo_data()
    points = [point*20 for point in map(pygame.Vector2, points)]
    for point in points:
        point.x += 250
        point.y += 200
        pygame.draw.circle(screen, 'darkblue', point, 5, 1)

    for p1, p2 in zip(points, points[1:]):
        pygame.draw.line(screen, 'azure', p1, p2)
    pygame.display.flip()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

def main(argv=None):
    """
    """
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)
    run()

if __name__ == '__main__':
    main()

# 2023-10-13
# Another interesting project to turn into Python.
# /home/hitbox/repos/reference/eliben/code-for-blog/2023/js-gauss-spline
# https://eli.thegreenplace.net/2023/cubic-spline-interpolation/
