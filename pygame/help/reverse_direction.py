import itertools as it
import random

import pygame

class RectSprite(pygame.sprite.Sprite):

    def __init__(self, rect, image, velocity=None, *groups):
        super().__init__(*groups)
        self.rect = rect
        self.image = image
        self.position = pygame.Vector2(self.rect.center)
        if velocity is None:
            velocity = ()
        self.velocity = pygame.Vector2(*velocity)

    def update(self, elapsed):
        self.position += self.velocity
        self.rect.center = self.position


def random_sprite(rect_size, color, maxvel):
    left = random.randint(0, window_size[0] - rect_size[0])
    top = random.randint(0, window_size[1] - rect_size[1])
    rect = pygame.Rect(left, top, *rect_size)

    image = pygame.Surface(rect.size)
    image.fill(color)

    position = pygame.Vector2(rect.center)
    vx = random.choice([-maxvel, +maxvel]) * random.random()
    vy = random.choice([-maxvel, +maxvel]) * random.random()
    velocity = pygame.Vector2(vx, vy)

    sprite = RectSprite(rect, image, velocity=velocity)

    return sprite

clock = pygame.time.Clock()

pygame.display.init()

desktop_size = pygame.display.get_desktop_sizes()[0]

# window 80% of desktop
window_size = tuple(map(int, map(lambda d: d * 0.80, desktop_size)))
window = pygame.Rect((0,0), window_size)

# rects' size % of window

denom = 25
rect_size = (desktop_size[0] // denom, desktop_size[1] // denom)

maxvel = 0.5
nsprites = 20
sprites = pygame.sprite.Group([random_sprite(rect_size, 'brown', maxvel) for _ in range(nsprites)])

debug = []

screen = pygame.display.set_mode(window.size)
running = True
elapsed = 0
while running:
    # events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    # update
    sprites.update(elapsed)
    # bounce and clamp to window
    for sprite in sprites:
        if sprite.rect.left < 0 or sprite.rect.right > window_size[0]:
            sprite.velocity.x *= -1
            sprite.rect.clamp_ip(window)
            sprite.position.x = sprite.rect.centerx
        if sprite.rect.top < 0 or sprite.rect.bottom > window_size[1]:
            sprite.velocity.y *= -1
            sprite.rect.clamp_ip(window)
            sprite.position.y = sprite.rect.centery
    # rect-rect collisions
    debug.clear()
    for sprite1, sprite2 in it.combinations(sprites, 2):
        if sprite1.rect.colliderect(sprite2.rect):
            overlap = sprite1.rect.clip(sprite2.rect)
            debug.append(overlap)
    # draw
    screen.fill('black')
    sprites.draw(screen)
    for rect in debug:
        pygame.draw.rect(screen, 'magenta', rect)
    pygame.display.flip()
    elapsed = clock.tick()

# 2024-06-28 Fri.
# https://www.reddit.com/r/pygame/comments/1doioxy/how_to_reverse_directs_of_all_rects_in_a_list/
