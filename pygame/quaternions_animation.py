import math

import pygamelib

from pygamelib import pygame

# cube vertices
vertices = [
    [-50, -50, -50],
    [50, -50, -50],
    [50, 50, -50],
    [-50, 50, -50],
    [-50, -50, 50],
    [50, -50, 50],
    [50, 50, 50],
    [-50, 50, 50]
]

edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7)
]

class Quaternion:

    def __init__(self, w, x, y, z):
        self.w = w
        self.x = x
        self.y = y
        self.z = z

    @classmethod
    def from_euler_angles(cls, roll, pitch, yaw):
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)

        w = cr * cp * cy + sr * sp * sy
        x = sr * cp * cy - cr * sp * sy
        y = cr * sp * cy + sr * cp * sy
        z = cr * cp * sy - sr * sp * cy

        return cls(w, x, y, z)

    def __mul__(self, other):
        w = self.w * other.w - self.x * other.x - self.y * other.y - self.z * other.z
        x = self.w * other.x + self.x * other.w + self.y * other.z - self.z * other.y
        y = self.w * other.y - self.x * other.z + self.y * other.w + self.z * other.x
        z = self.w * other.z + self.x * other.y - self.y * other.x + self.z * other.w
        return Quaternion(w, x, y, z)


def run(display_size, framerate, background):

    def rotate_vertex(vertex, quaternion_rotation):
        """
        rotate a vertex using a quaternion
        """
        q_conj = Quaternion(
            quaternion_rotation.w,
            -quaternion_rotation.x,
            -quaternion_rotation.y,
            -quaternion_rotation.z
        )
        q = quaternion_rotation * Quaternion(0, *vertex) * q_conj
        return (q.x, q.y, q.z)

    window = pygame.Rect((0,0), display_size)
    clock = pygame.time.Clock()

    # Initial quaternion rotation (no rotation)
    rotation = Quaternion(1, 0, 0, 0)

    running = True
    screen = pygame.display.set_mode(display_size)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()

        screen.fill(background)

        # Rotate the cube
        rotation = Quaternion.from_euler_angles(0.01, 0.02, 0.03) * rotation

        # Project and draw vertices
        projected_vertices = []
        for vertex in vertices:
            rotated_vertex = rotate_vertex(vertex, rotation)
            z = 5 / (5 + rotated_vertex[2])
            x = rotated_vertex[0] * z + window.width / 2
            y = rotated_vertex[1] * z + window.height / 2
            projected_vertices.append((x, y))

        for index1, index2 in edges:
            p1 = projected_vertices[index1]
            p2 = projected_vertices[index2]
            pygame.draw.line(screen, 'white', p1, p2)

        pygame.display.flip()
        clock.tick(framerate)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    args = parser.parse_args(argv)

    run(args.display_size, args.framerate, args.background)

if __name__ == '__main__':
    main()
