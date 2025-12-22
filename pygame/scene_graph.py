import math
import contextlib
import os

# ChatGPT generated Node class for demonstrating a scene graph.

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

def rotate(v, angle):
    x, y = v
    c = math.cos(angle)
    s = math.sin(angle)
    return (x * c - y * s, x * s + y * c)

class Node:

    def __init__(self, pos=(0, 0), rot=0, parent=None):
        self.local_pos = pygame.Vector2(pos)
        self.local_rot = rot
        self.parent = parent
        self.children = []
        if parent:
            parent.children.append(self)

    def world_pos(self):
        if not self.parent:
            return self.local_pos
        p = rotate(self.local_pos, self.parent.world_rot())
        return self.parent.world_pos() + pygame.Vector2(p)

    def world_rot(self):
        if not self.parent:
            return self.local_rot
        return self.parent.world_rot() + self.local_rot

    def end_point(self):
        wp = self.world_pos()
        wr = self.world_rot()

        # Draw local X axis
        x_axis = rotate((30, 0), wr)
        return wp + pygame.Vector2(x_axis)

    def draw_axis(self, surf, wp, wr):
        x_axis = rotate((30, 0), wr)
        pygame.draw.line(
            surf, 'red', wp, wp + pygame.Vector2(x_axis), 2
        )

    def draw_parent_link(self, surf, wp, wr):
        pygame.draw.line(
            surf, 'gray',
            self.parent.world_pos(),
            wp,
            1
        )

    def draw(self, surf):
        wp = self.world_pos()
        wr = self.world_rot()

        # Draw node as circle
        pygame.draw.circle(surf, 'white', wp, 5)

        # Draw parent link
        if self.parent:
            self.draw_parent_link(surf, wp, wr)

        # Draw children
        for c in self.children:
            c.draw(surf)


class SpriteNode(Node):

    def __init__(self, *args, **kwargs):
        self.image = kwargs.pop('image', None)
        super().__init__(*args, **kwargs)

    def draw(self, surf):
        super().draw(surf)
        self.draw_image(surf)

    def draw_image(self, surf):
        image = self.image
        if image:
            wp = self.world_pos()
            wr = self.world_rot()
            if wr:
                wr_degrees = math.degrees(wr)
                image = pygame.transform.rotate(image, -wr_degrees)
            surf.blit(image, image.get_rect(center=wp))


screen = pygame.display.set_mode((800, 600))
window = screen.get_rect()
clock = pygame.time.Clock()
pygame.font.init()
font = pygame.font.SysFont(None, 24)

graph = [
    Node((400, 300)),
]
graph.append(Node((50, 0), parent=graph[-1]))
graph.append(SpriteNode((80, 0), parent=graph[-1]))

graph[-1].image = pygame.image.load(
    '/home/hitbox/Downloads/Kenney Game Assets/'
    'Kenney Game Assets All-in-1 3.3.0/2D assets/Shape Characters/'
    'PNG/Double/purple_hand_rock.png'
)

hand_samples = []

running = True
angle_rads = 0
while running:
    dt = clock.tick(60) / 1000.0
    angle_rads += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for mult, node in zip(range(2, len(graph)+2), graph, strict=True):
        node.local_rot = angle_rads * mult
    hand_samples.append(graph[-1].end_point())

    screen.fill('gray10')
    graph[0].draw(screen)
    # Draw sampled points, line.
    if len(hand_samples) > 1:
        pygame.draw.lines(screen, 'brown', False, hand_samples)

    image = font.render(f'{len(hand_samples)=}', True, 'grey')
    screen.blit(image, image.get_rect(topright=window.topright))

    pygame.display.flip()

pygame.quit()
