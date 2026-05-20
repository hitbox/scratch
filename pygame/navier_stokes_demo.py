import argparse
import math
import os
import time
from contextlib import redirect_stdout

with redirect_stdout(open(os.devnull, 'w')):
    import pygame

class FluidSimulation:

    def __init__(self, width, height, viscosity=0.1, dt=0.1):
        self.width = width
        self.height = height
        self.viscosity = viscosity
        self.dt = dt
        # velocity fields
        self.u = [[0.0 for _ in range(self.width)] for _ in range(self.height)]
        self.v = [[0.0 for _ in range(self.width)] for _ in range(self.height)]

        # density field (what we render)
        self.rho = [[0.0 for _ in range(self.width)] for _ in range(self.height)]

    def step(self):
        # add forcing
        self.add_source()

        # velocity diffusion
        self.u = self.diffuse(self.u)
        self.v = self.diffuse(self.v)

        # advect velocity (self-movement)
        self.u = self.advect(self.u, self.u, self.v)
        self.u = self.advect(self.v, self.u, self.v)

        # advect density
        self.rho = self.advect(self.rho, self.u, self.v)

    def add_source(self):
        # inject “ink” + upward force in center
        cx, cy = self.width // 2, self.height // 2
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                self.rho[cy + dy][cx + dx] = 5.0
                self.u[cy + dy][cx + dx] += 0.0
                self.v[cy + dy][cx + dx] -= 5.0  # upward burst

    def diffuse(self, field):
        # very crude smoothing (viscosity approximation)
        new = [[0.0 for _ in range(self.width)] for _ in range(self.height)]

        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                avg = (
                    field[y][x] +
                    field[y+1][x] +
                    field[y-1][x] +
                    field[y][x+1] +
                    field[y][x-1]
                ) / 5.0
                new[y][x] = field[y][x] + self.viscosity * (avg - field[y][x])

        return new

    def advect(self, field, u, v):
        new = [[0.0 for _ in range(self.width)] for _ in range(self.height)]
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                # trace backwards (semi-Lagrangian step)
                x0 = int(x - u[y][x] * self.dt)
                y0 = int(y - v[y][x] * self.dt)
                x0 = clamp(x0, 1, self.width - 2)
                y0 = clamp(y0, 1, self.height - 2)
                new[y][x] = field[y0][x0]
        return new

    def render(self):
        os.system("clear")
        chars = " .:-=+*#%@"
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                c = int(clamp(self.rho[y][x], 0, 9))
                row += chars[c]
            print(row)


class PrintRenderer:

    def __call__(self, sim):
        os.system("clear")
        chars = " .:-=+*#%@"
        for y in range(sim.height):
            row = ""
            for x in range(sim.width):
                c = int(clamp(sim.rho[y][x], 0, 9))
                row += chars[c]
            print(row)


class PygameRenderer:

    def __init__(self, screen_size):
        width, height = screen_size
        self.width = width
        self.height = height
        pygame.display.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode(screen_size)
        self.font = pygame.font.SysFont(None, 24)

    def __call__(self, sim):
        self.screen.fill('black')
        chars = " .:-=+*#%@"
        height = None
        # TODO
        # - Look for regex matching line in logs, parse datetime and provide
        #   check for watcher.
        # - Suppliment data available to condition expression with regex.
        # - Mainly for CLP logs to check that it has seen a new file recently.
        # - Think it's logging that it's running so it's always recent--the log
        #   file time.
        for y in range(sim.height):
            row = ""
            for x in range(sim.width):
                c = int(clamp(sim.rho[y][x], 0, 9))
                row += chars[c]
            image = self.font.render(row, True, 'azure')
            height = image.get_height()
            self.screen.blit(image, (x, y + height))
        pygame.display.update()


def clamp(x, a, b):
    return max(a, min(b, x))

def run(sim, renderer):
    while True:
        sim.step()
        renderer(sim)
        time.sleep(0.05)

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

    sim = FluidSimulation(60, 30, 0.1)
    renderer = PygameRenderer((800, 600))
    try:
        run(sim, renderer)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
