import math

import pygamelib

from pygamelib import pygame

class Segment:

    def __init__(self, x, y, length, angle=0):
        self.x = x
        self.y = y
        self.length = length
        self.angle = angle
        self.calculate_end()

    def calculate_end(self):
        self.end_x = self.x + self.length * math.cos(self.angle)
        self.end_y = self.y + self.length * math.sin(self.angle)

    def follow(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        self.angle = math.atan2(dy, dx)
        self.x = target_x - self.length * math.cos(self.angle)
        self.y = target_y - self.length * math.sin(self.angle)
        self.calculate_end()

    def set_start(self, x, y):
        self.x = x
        self.y = y
        self.calculate_end()

    def draw(self, screen):
        pygame.draw.line(screen, 'white', (self.x, self.y), (self.end_x, self.end_y), 5)
        pygame.draw.circle(screen, 'white', (int(self.x), int(self.y)), 5)


def run(args):
    clock = pygame.time.Clock()

    # Create a chain of segments
    width, height = 800, 600
    num_segments = 5
    segment_length = 50
    segments = [Segment(width // 2, height // 2, segment_length) for _ in range(num_segments)]

    # "truck"
    segments = [
        Segment(0,0, 100),
        Segment(0,0, 20),
    ]

    screen = pygame.display.set_mode(args.display_size)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Update segments to follow the mouse
        segments[-1].follow(mouse_x, mouse_y)
        for i in range(len(segments) - 2, -1, -1):
            segments[i].follow(segments[i + 1].x, segments[i + 1].y)

        for i in range(1, len(segments)):
            segments[i].set_start(segments[i - 1].end_x, segments[i - 1].end_y)

        # Clear screen
        screen.fill('black')

        # Draw segments
        for segment in segments:
            segment.draw(screen)

        # Update display
        pygame.display.flip()

def main(argv=None):
    parser = pygamelib.command_line_parser()
    args = parser.parse_args(argv)
    run(args)


if __name__ == '__main__':
    main()
