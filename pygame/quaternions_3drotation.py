import argparse
import math

import pygamelib

from pygamelib import pygame
from quaternions import Quaternion

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

CUBE_SIZE = 50
FPS = 60

def rotate_vector(vector, quaternion):
    # rotate a vector by a quaternion
    rotated_vector = pygame.math.Vector3(0, 0, 0)

    roll, pitch, yaw = quaternion.as_euler()

    rotated_vector.rotate_ip(roll, pygame.math.Vector3(1, 0, 0))
    rotated_vector.rotate_ip(pitch, pygame.math.Vector3(0, 1, 0))
    rotated_vector.rotate_ip(yaw, pygame.math.Vector3(0, 0, 1))
    return rotated_vector

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # Create cube vertices
    cube_vertices = [
        pygame.math.Vector3(-CUBE_SIZE/2, -CUBE_SIZE/2, -CUBE_SIZE/2),
        pygame.math.Vector3(+CUBE_SIZE/2, -CUBE_SIZE/2, -CUBE_SIZE/2),
        pygame.math.Vector3(+CUBE_SIZE/2, +CUBE_SIZE/2, -CUBE_SIZE/2),
        pygame.math.Vector3(-CUBE_SIZE/2, +CUBE_SIZE/2, -CUBE_SIZE/2),
        pygame.math.Vector3(-CUBE_SIZE/2, -CUBE_SIZE/2, +CUBE_SIZE/2),
        pygame.math.Vector3(+CUBE_SIZE/2, -CUBE_SIZE/2, +CUBE_SIZE/2),
        pygame.math.Vector3(+CUBE_SIZE/2, +CUBE_SIZE/2, +CUBE_SIZE/2),
        pygame.math.Vector3(-CUBE_SIZE/2, +CUBE_SIZE/2, +CUBE_SIZE/2)
    ]

    cube_vertices = [v + pygame.Vector3(500, 500, 0) for v in cube_vertices]

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
    time = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()

        screen.fill('black')
        interpolated_orientation = initial_orientation.slerp_to(final_orientation, time)

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

        pygame.display.flip()

        time += 0.005
        if time > 1:
            time = 0
        clock.tick(FPS)

if __name__ == '__main__':
    main()
