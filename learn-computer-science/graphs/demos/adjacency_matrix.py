import argparse
import contextlib
import math
import os
import random

from itertools import chain
from itertools import repeat

with contextlib.redirect_stdout(open(os.devnull,'w')):
    import pygame

from ..adjacency_matrix import AdjacencyMatrix

def is_colorful(name):
    return ('gray' not in name and 'grey' not in name and not name[-1].isdigit())

colorful = [color for key, color in pygame.color.THECOLORS.items() if is_colorful(key)]

random_spread = [x for x in range(-5, 6) if x != 0]

class Animation:

    def __init__(self, duration, elapsed=0):
        self.duration = duration
        self.elapsed = elapsed


def make_vertex_sprite(font, label, *groups):
    sprite = pygame.sprite.Sprite(*groups)
    sprite.label = label
    text = f'{sprite.label}'
    size = font.size(text)
    sprite.radius = max(size)
    sprite.color = (10,)*3
    sprite.radius_border = sprite.radius * 4
    text_image = font.render(text, True, sprite.color)
    size = (int(sprite.radius*2),)*2
    sprite.image = pygame.Surface(size, flags=pygame.SRCALPHA)
    rect = sprite.image.get_rect()
    #
    pygame.draw.circle(sprite.image, (200,)*3, rect.center, sprite.radius)
    pygame.draw.circle(sprite.image, sprite.color, rect.center, sprite.radius, 1)
    sprite.image.blit(text_image, text_image.get_rect(center=rect.center))
    #
    sprite.rect = sprite.image.get_rect()
    sprite.center = pygame.Vector2(sprite.rect.center)
    return sprite

def render_matrix(
    font,
    graph,
    padding=0,
    font_color=(200,)*3,
    border_color=(200,)*3,
):
    """
    Render an image of the adjacency matrix.
    """
    table = [[None]*graph.nvertices for _ in range(graph.nvertices)]

    # compute sizes
    for ri, row in enumerate(graph.adjacency_matrix):
        for ci, col in enumerate(row):
            vertex1 = graph.vertices_list[ri]
            vertex2 = graph.vertices_list[ci]
            if col == AdjacencyMatrix.notset:
                size = (0, 0)
                text = None
            else:
                text = f'{vertex1}-{vertex2}'
                size = font.size(text)
            table[ri][ci] = (text, size)

    cell_width = padding + max(
        (max(width for (text, (width, height)) in row) for row in table), default=0)
    cell_height = padding + max(
        (height for row in table for (text, (width, height)) in row), default=0)
    cell_size = (cell_width, cell_height)

    table_image = pygame.Surface((cell_width*graph.nvertices, cell_height*graph.nvertices))
    empty_image = pygame.Surface(cell_size)
    pygame.draw.rect(empty_image, border_color, empty_image.get_rect(), 1)

    for ri, row in enumerate(table):
        for ci, (text, (width, height)) in enumerate(row):
            if text is None:
                image = empty_image
            else:
                image = pygame.Surface(cell_size)
                pygame.draw.rect(image, border_color, image.get_rect(), 1)
                text_image = font.render(text, True, font_color)
                image.blit(text_image, text_image.get_rect(center=image.get_rect().center))
            table_image.blit(image, (ri*cell_width,  ci*cell_height))
    return table_image

def loop(graph, commands):
    framerate = 60

    command_animation = Animation(duration=framerate * .50)
    command = None
    history = []
    last_vertices = graph.vertices.copy()

    pygame.font.init()
    screen = pygame.display.set_mode((800, 700))
    background = screen.copy()
    frame = screen.get_rect()
    font = pygame.font.Font(None, 40)
    small_font = pygame.font.Font(None, 40)
    clock = pygame.time.Clock()
    group = pygame.sprite.Group()
    sprites_by_label = {}

    dragging = None
    visited = None
    hovering = None
    running = True
    while running:
        # tick
        elapsed = clock.tick(framerate)
        # events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    dragging.rect.move_ip(event.rel)
                    dragging.center.x = dragging.rect.centerx
                    dragging.center.y = dragging.rect.centery
                else:
                    for sprite in group:
                        dist = math.dist(sprite.rect.center, event.pos)
                        if dist <= sprite.radius:
                            hovering = sprite
                            break
                    else:
                        hovering = None
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for sprite in group:
                    if sprite.rect.collidepoint(event.pos):
                        dragging = sprite
                        # set all sprites to a draggable-friendly boundary radius
                        for sprite in group:
                            sprite.radius_border = sprite.radius * 2
                        break
                else:
                    dragging = None
        # update
        if commands:
            command_animation.elapsed += 1
            if command_animation.elapsed == command_animation.duration:
                if command is not None:
                    history.append(command)
                command = next(commands)
                command_animation.elapsed = 0

        # execute commands
        if command is not None:
            f, *args = command
            # XXX: just assuming the ones that return something is the visitor
            rv = f(*args)
            if rv:
                visited = rv

        # examine changes to vertices
        if last_vertices != graph.vertices:
            change = set(graph.vertices).difference(last_vertices)
            for label in change:
                sprite = make_vertex_sprite(font, label, group)
                sprites_by_label[label] = sprite
                cx, cy = frame.center
                cx += random.choice(random_spread)
                cy += random.choice(random_spread)
                sprite.rect.center = (cx, cy)
                sprite.center = pygame.Vector2(sprite.rect.center)
            last_vertices = graph.vertices.copy()
        # update - detect collisions
        collisions = []
        _sprites = group.sprites()
        for sprite1 in _sprites:
            for sprite2 in _sprites:
                if sprite1 is sprite2:
                    continue
                dist = math.dist(sprite1.center, sprite2.center)
                if dist == 0 or dist <= (sprite1.radius_border + sprite2.radius_border):
                    collisions.append((sprite1, sprite2))
        # update - resolve collisions
        for sprite1, sprite2 in collisions:
            dy = sprite2.center.y - sprite1.center.y
            dx = sprite2.center.x - sprite1.center.x
            angle = math.atan2(dy, dx)
            dist = math.dist(sprite1.center, sprite2.center)
            radii = (sprite1.radius_border + sprite2.radius_border)
            move_step = (radii - dist) * 0.10
            sprite1.center.x -= math.cos(angle) * move_step
            sprite1.center.y -= math.sin(angle) * move_step
            sprite2.center.x += math.cos(angle) * move_step
            sprite2.center.y += math.sin(angle) * move_step

            sprite1.rect.center = sprite1.center
            sprite2.rect.center = sprite2.center
        # draw
        screen.blit(background, (0,0))

        # TODO: draw history of commands like scrollback like command line.

        # draw - matrix table
        table_image = render_matrix(
            small_font,
            graph,
            padding=40,
            font_color=(100,)*3,
            border_color=(100,)*3,
        )
        screen.blit(table_image, table_image.get_rect(center=frame.center))

        # draw - edge lines
        for label1, label2, _ in graph.get_edges():
            sprite1 = sprites_by_label[label1]
            sprite2 = sprites_by_label[label2]
            if visited and sprite1.label in visited and sprite2.label in visited:
                color = (200,200,10)
                width = 4
            else:
                color = (200,)*3
                width = 1
            pygame.draw.line(screen, color, sprite1.rect.center, sprite2.rect.center, width)

        # draw - sprites
        group.draw(screen)

        # draw - hovering cursor
        if hovering:
            pygame.draw.circle(screen, (200,30,30), hovering.rect.center, hovering.radius*1.5, 1)

        # draw - visited
        if visited is not None:
            for sprite in group:
                if sprite.label in visited:
                    if visited.index(sprite.label) == 0:
                        color = (200,10,10)
                    else:
                        color = (10,200,10)
                    pygame.draw.circle(screen, color, sprite.rect.center, sprite.radius*2, 4)

        pygame.display.flip()

class Visit:

    def __init__(self, graph, duration, callback=None):
        self.graph = graph
        self.duration = duration
        self.elapsed = 0
        self.i = self.j = 0

    def __call__(self):
        self.elapsed += 1
        if self.elapsed == self.duration:
            self.elapsed = 0
            #
            edge = None
            while edge is None:
                if self.graph.adjacency_matrix[self.i][self.j] != AdjacencyMatrix.notset:
                    vertex1 = self.graph.vertices_list[self.i]
                    vertex2 = self.graph.vertices_list[self.j]
                    edge = (vertex1, vertex2)
                self.j += 1
                if self.j == self.graph.nvertices:
                    self.j = 0
                    self.i += 1
                    if self.i == self.graph.nvertices:
                        self.i = 0
                        self.j = 0
            return edge


def edge_or_vertex(s):
    """
    string argument describing and edge or vertex.
    """
    # dash and dot chosen to avoid problems on command line, like having to
    # avoid redirection by quoting
    directed = False
    if '-' in s:
        sep = '-'
        directed = True
    elif '.' in s:
        sep = '.'
    else:
        # one vertex
        return (s.strip(),)
    v1, v2 = map(str.strip, s.split(sep))
    return (v1, v2, directed)

def make_graph_args(graph_strings):
    # keep actual edges
    edges = [edge for edge in graph_strings if len(edge) > 1]
    # flatten edges list into unique vertices
    vertices = set(v for edge in edges for v in edge[:2])
    return (vertices, edges)

def main(argv=None):
    """
    Demonstrate adjacency matrix graph representation.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('graph', nargs='+', type=edge_or_vertex)
    args = parser.parse_args(argv)

    # create commands to build the graph in an animated fashion
    vertices, edges = make_graph_args(args.graph)

    graph = AdjacencyMatrix(len(vertices))
    commands = []
    # commands to make vertices
    for index, vertex in enumerate(sorted(vertices)):
        commands.append((graph.set_vertex, index, vertex))
    # commands to make edges
    for edge in edges:
        v1, v2, directed = edge
        commands.append((graph.set_edge, v1, v2, directed))
    #
    visit = Visit(graph, 60)
    commands = chain(commands, repeat((visit,)))
    loop(graph, commands)

if __name__ == '__main__':
    main()
