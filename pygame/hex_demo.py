import argparse
import os
import contextlib

import math

with contextlib.redirect_stdout(open(os.devnull, 'w')): 
    import pygame

pointy_top_hex_angles = [math.pi / 180 * (60 * i - 30) for i in range(6)]

class HexGrid:

    def __init__(self, hex_size):
        self.hex_size = hex_size

    def to_pixel(self, q, r, camera, screen):
        """
        Convert axial to pixel
        """
        x = self.hex_size * math.sqrt(3) * (q + r/2) - camera.x
        y = self.hex_size * 3/2 * r - camera.y
        return x + screen.centerx, y + screen.centery

    def to_hex(self, x, y, camera, screen):
        """
        Convert pixel to axial
        """
        x = x - screen.centerx + camera.x
        y = y - screen.centery + camera.y
        q = (math.sqrt(3)/3 * x - y/3) / self.hex_size
        r = (2/3 * y) / self.hex_size
        return self.nearest_hex(q, r)

    def nearest_hex(self, q, r):
        """
        Round fractional axial coords to nearest hex
        """
        x = q
        z = r
        y = -x - z
        rx = round(x)
        ry = round(y)
        rz = round(z)

        x_diff = abs(rx - x)
        y_diff = abs(ry - y)
        z_diff = abs(rz - z)

        if x_diff > y_diff and x_diff > z_diff:
            rx = -ry - rz
        elif y_diff > z_diff:
            ry = -rx - rz
        else:
            rz = -rx - ry
        return int(rx), int(rz)

    def draw_hex(self, surface, x, y, color):
        """
        Draw hex at pixel
        """
        points = []
        for angle in pointy_top_hex_angles:
            px = x + self.hex_size * math.cos(angle)
            py = y + self.hex_size * math.sin(angle)
            points.append((px, py))
        pygame.draw.polygon(surface, color, points, 2)


def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    frame = screen.get_rect()

    # Hex size
    HEX_SIZE = 40
    hex_grid = HexGrid(40)

    # Camera offset
    camera = pygame.Vector2()

    # Directions for hex neighbors (pointy-top axial)
    directions = [
        (1, 0), (1, -1), (0, -1),
        (-1, 0), (-1, 1), (0, 1)
    ]

    clicked = []

    # Main loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == pygame.BUTTON_LEFT:
                    # left-button click up
                    mx, my = event.pos
                    hex_cell = hex_grid.to_hex(mx, my, camera, frame)
                    if hex_cell in clicked:
                        clicked.remove(hex_cell)
                    else:
                        clicked.append(hex_cell)
            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[1]:
                    # middle-click dragging
                    camera -= event.rel

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: camera.y -= 10
        if keys[pygame.K_s]: camera.y += 10
        if keys[pygame.K_a]: camera.x -= 10
        if keys[pygame.K_d]: camera.x += 10

        screen.fill('black')

        # Draw hex grid around camera
        radius = 10
        cam_q, cam_r = hex_grid.to_hex(frame.centerx, frame.centery, camera, frame)
        for r in range(cam_r - radius, cam_r + radius + 1):
            for q in range(cam_q - radius, cam_q + radius + 1):
                if (q, r) in clicked:
                    color = 'brown'
                else:
                    color = 'azure'
                px, py = hex_grid.to_pixel(q, r, camera, frame)
                hex_grid.draw_hex(screen, px, py, color=color)

        # Highlight hex under mouse
        mx, my = pygame.mouse.get_pos()
        hq, hr = hex_grid.to_hex(mx, my, camera, frame)
        px, py = hex_grid.to_pixel(hq, hr, camera, frame)
        hex_grid.draw_hex(screen, px, py, color='yellow')

        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()
