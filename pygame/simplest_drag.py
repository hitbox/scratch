import pygame

screen = pygame.display.set_mode((800,)*2)
rect = screen.get_rect().inflate((-600,)*2)

# 2024-03-04 Mon.
# - trying to think of the simplest possible way to drag
# - this works but also "pushes" the rect
# - maybe maintain a collection of draggables and which ones were initially
#   clicked and only those are considered dragging

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEMOTION:
            if event.buttons[0] and rect.collidepoint(event.pos):
                rect.topleft += pygame.Vector2(event.rel)
    screen.fill('black')
    pygame.draw.rect(screen, 'orange', rect, 0)
    pygame.display.flip()
