#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

echo draw
echo
python -m timeit \
    --setup "import pygame" \
    --setup "screen = pygame.display.set_mode((500,)*2)" \
    --setup "rect = pygame.Rect((0,)*2, (250,)*2)" \
    --setup "rect.center = screen.get_rect().center" \
    -- \
    "for _ in range(100):" \
    "    pygame.event.get()" \
    "    pygame.draw.rect(screen, 'white', rect)" \
    "    pygame.display.update()"

echo blit
echo
python -m timeit \
    --setup "import pygame" \
    --setup "screen = pygame.display.set_mode((500,)*2)" \
    --setup "image = pygame.Surface((250,)*2)" \
    --setup "image.fill('white')" \
    --setup "rect = image.get_rect(center=screen.get_rect().center)" \
    -- \
    "for _ in range(100):" \
    "    pygame.event.get()" \
    "    screen.blit(image, rect)" \
    "    pygame.display.update()"
