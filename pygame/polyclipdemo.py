import pygame
import sys

from pygame.locals import *

# Define the clipping window
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400
CLIP_WINDOW = [(100, 100), (500, 100), (500, 300), (100, 300)]

# Define the polygon to be clipped
POLYGON = [(200, 200), (400, 50), (500, 250), (400, 350), (300, 300), (250, 400), (150, 250)]

def clip_polygon(subject_polygon, clip_window):
    def inside(p, clip_window):
        x, y = p
        # Check if the point is inside the clip window
        return clip_window[0][0] <= x <= clip_window[2][0] and clip_window[0][1] <= y <= clip_window[2][1]

    def compute_intersection(p1, p2, p3, p4):
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        x4, y4 = p4
        denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denominator == 0:
            return None
        intersect_x = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denominator
        intersect_y = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denominator
        return intersect_x, intersect_y

    output_list = subject_polygon
    for edge in clip_window:
        input_list = output_list
        output_list = []
        S = input_list[-1]
        for E in input_list:
            if inside(E, clip_window):
                if not inside(S, clip_window):
                    intersect = compute_intersection(S, E, clip_window[0], clip_window[1])
                    if intersect:
                        output_list.append(intersect)
                output_list.append(E)
            elif inside(S, clip_window):
                intersect = compute_intersection(S, E, clip_window[0], clip_window[1])
                if intersect:
                    output_list.append(intersect)
            S = E
        if not output_list:
            break
    return output_list

def draw_thick_line(screen, color, start_pos, end_pos, thickness):
    # Draw thick line using multiple thin lines
    pygame.draw.line(screen, color, start_pos, end_pos, thickness)

def draw_polygon(screen, color_name, vertices, thickness):
    # Draw thick lines for polygon edges
    for i in range(len(vertices)):
        start_point = vertices[i]
        end_point = vertices[(i + 1) % len(vertices)]
        draw_thick_line(screen, pygame.color.THECOLORS[color_name], start_point, end_point, thickness)

def draw_point(screen, color_name, point, size=5):
    pygame.draw.circle(screen, pygame.color.THECOLORS[color_name], point, size)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Polygon Clipping')
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        screen.fill('black')  # Set background color to black

        # Draw clipping window
        draw_polygon(screen, 'green', CLIP_WINDOW, 2)

        # Draw original polygon with thicker lines
        draw_polygon(screen, 'red', POLYGON, 3)

        # Draw vertices of original polygon
        for vertex in POLYGON:
            draw_point(screen, 'red', vertex)

        # Clip polygon
        clipped_polygon = clip_polygon(POLYGON, CLIP_WINDOW)

        # Draw clipped polygon with thinner lines
        draw_polygon(screen, 'green', clipped_polygon, 1)

        # Draw vertices of clipped polygon
        for vertex in clipped_polygon:
            draw_point(screen, 'green', vertex)

        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()
