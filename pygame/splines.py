import pygamelib

from pygamelib import pygame

class CubicSpline:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.n = len(x)
        self.a, self.b, self.c, self.d = self._calculate_coefficients()

    def _calculate_coefficients(self):
        h = [self.x[i + 1] - self.x[i] for i in range(self.n - 1)]

        def _alpha(i):
            return (
                (3 / h[i])
                * (self.y[i + 1] - self.y[i])
                - (3 / h[i - 1])
                * (self.y[i] - self.y[i - 1])
            )

        alpha = [_alpha(i) for i in range(1, self.n - 1)]

        l = [1] * self.n
        mu = [0] * self.n
        z = [0] * self.n
        c = [0] * self.n

        for i in range(1, self.n - 1):
            l[i] = 2 * (self.x[i + 1] - self.x[i - 1]) - h[i - 1] * mu[i - 1]
            mu[i] = h[i] / l[i]
            z[i] = (alpha[i - 1] - h[i - 1] * z[i - 1]) / l[i]

        l[-1] = 1
        z[-1] = 0
        c[-1] = 0

        for j in range(self.n - 2, -1, -1):
            c[j] = z[j] - mu[j] * c[j + 1]

            def _b(i):
                return (
                    (self.y[i + 1] - self.y[i])
                    / h[i] - h[i] * (c[i + 1] + 2 * c[i]) / 3
                )

            b = [_b(i) for i in range(self.n - 1)]
            d = [(c[i + 1] - c[i]) / (3 * h[i]) for i in range(self.n - 1)]
            return self.y[:-1], b, c[:-1], d

    def _find_segment(self, xi):
        for i in range(self.n - 1):
            if self.x[i] <= xi <= self.x[i + 1]:
                return i
        raise ValueError("x value is out of range")

    def evaluate(self, xi):
        i = self._find_segment(xi)
        dx = xi - self.x[i]
        return self.a[i] + self.b[i] * dx + self.c[i] * dx**2 + self.d[i] * dx**3


def main(argv=None):
    """
    Demo splines with pygame
    """
    parser = pygamelib.command_line_parser()
    args = parser.parse_args(argv)

    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    # Example data
    x = [0, 1, 2, 3, 4]
    y = [0, 1, 0, 1, 0]
    spline = CubicSpline(x, y)

    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Clear the screen
        screen.fill('black')

        # Draw the interpolated curve
        step = 0.01
        for i in range(len(x) - 1):
            for j in range(int((x[i + 1] - x[i]) / step)):
                xi = x[i] + j * step
                p = (int(xi * 100), int(spline.evaluate(xi) * 100))
                pygame.draw.circle(screen, 'red', p, 2)

        # Draw the control points
        for i in range(len(x)):
            p = (int(x[i] * 100), int(y[i] * 100))
            pygame.draw.circle(screen, 'green', p, 5)

        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()

# 2024-04-17 Wed.
# - started reading:
#   https://eli.thegreenplace.net/2024/method-of-differences-and-newton-polynomials/
# - asked chatgpt about polynomial sequences
#   https://chat.openai.com/c/bd457469-1931-4c72-b985-d8c54920b006
# - asked for spline demo (this with cleanup)
