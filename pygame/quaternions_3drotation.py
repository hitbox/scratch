import argparse
import math

from pygamelib import pygame
from quaternions import Quaternion

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

CUBE_SIZE = 100
FPS = 60

def slerp(q1, q2, t):
    # quaternion interpolation function
    return Quaternion.slerp(q1, q2, t)

def rotate_vector(vector, quaternion):
    # rotate a vector by a quaternion
    rotated_vector = pygame.math.Vector3(0, 0, 0)
    rotated_vector.rotate_ip(pygame.math.Vector3(1, 0, 0), quaternion.as_euler()[0])
    rotated_vector.rotate_ip(pygame.math.Vector3(0, 1, 0), quaternion.as_euler()[1])
    rotated_vector.rotate_ip(pygame.math.Vector3(0, 0, 1), quaternion.as_euler()[2])
    return rotated_vector

def main():
    # Create screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Quaternion Interpolation Demo")
    clock = pygame.time.Clock()

    # Create cube vertices
    cube_vertices = [
        pygame.math.Vector3(-CUBE_SIZE/2, -CUBE_SIZE/2, -CUBE_SIZE/2),
        pygame.math.Vector3(CUBE_SIZE/2, -CUBE_SIZE/2, -CUBE_SIZE/2),
        pygame.math.Vector3(CUBE_SIZE/2, CUBE_SIZE/2, -CUBE_SIZE/2),
        pygame.math.Vector3(-CUBE_SIZE/2, CUBE_SIZE/2, -CUBE_SIZE/2),
        pygame.math.Vector3(-CUBE_SIZE/2, -CUBE_SIZE/2, CUBE_SIZE/2),
        pygame.math.Vector3(CUBE_SIZE/2, -CUBE_SIZE/2, CUBE_SIZE/2),
        pygame.math.Vector3(CUBE_SIZE/2, CUBE_SIZE/2, CUBE_SIZE/2),
        pygame.math.Vector3(-CUBE_SIZE/2, CUBE_SIZE/2, CUBE_SIZE/2)
    ]

    # Create cube edges
    cube_edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]

    # Define initial and final orientations as quaternions
    initial_orientation = Quaternion.from_euler((0, 0, 0))
    final_orientation = Quaternion.from_euler((math.pi/2, 0, math.pi/4))

    running = True
    t = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Clear screen
        screen.fill('black')

        # Interpolate orientation using slerp
        interpolated_orientation = slerp(initial_orientation, final_orientation, t)

        # Rotate cube vertices using interpolated orientation
        rotated_cube_vertices = [
            rotate_vector(vertex, interpolated_orientation)
            for vertex in cube_vertices
        ]

        # Project and draw edges of rotated cube
        for edge in cube_edges:
            start = rotated_cube_vertices[edge[0]]
            end = rotated_cube_vertices[edge[1]]
            pygame.draw.line(
                screen,
                'white',
                (start.x + SCREEN_WIDTH/2, start.y + SCREEN_HEIGHT/2),
                (end.x + SCREEN_WIDTH/2, end.y + SCREEN_HEIGHT/2),
                2
            )

        t += 0.005
        if t > 1:
            t = 0

        # Update display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)

if __name__ == '__main__':
    main()
