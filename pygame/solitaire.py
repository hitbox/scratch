import argparse
import contextlib
import itertools as it
import os
import random

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

SUITS = 'HSDC'
RANKS = list(range(1,14))

class Card:

    def __init__(self, suit, rank, facing=False):
        self.suit = suit
        self.rank = rank
        self.facing = facing

    def face_text(self):
        return f'{self.suit}{self.rank}'


class Solitaire:

    def __init__(self):
        self.stock = []
        self.waste = []
        self.foundations = {suit: [] for suit in SUITS}
        self.tableau = {max_: [] for max_ in range(1,8)}

    def setup(self, deck):
        for max_, pile in self.tableau.items():
            for i in range(max_):
                card = deck.pop()
                is_last = i == max_ - 1
                if is_last:
                    card.facing = True
                pile.append(card)
        self.stock = deck

    def reveal_stock(self, n=1):
        card = self.stock.pop()
        card.facing = True
        self.waste.append(card)


class CardSprite(pygame.sprite.Sprite):

    def __init__(self, card, face_down, face_up, *groups):
        super().__init__(*groups)
        self.card = card
        self.face_up = face_up
        self.face_down = face_down
        self.rect = self.image.get_rect()

    @property
    def image(self):
        if self.card.facing:
            return self.face_up
        else:
            return self.face_down


class CardImage:

    colors = {
        'H': 'red',
        'D': 'red',
        'C': 'black',
        'S': 'black',
    }

    def __init__(self, size, font):
        self.size = size
        self.font = font

    def __call__(self, card):
        image = render_rect(self.size, 'gray', 'azure')
        rect = image.get_rect()
        text = card.face_text()
        color = self.colors[card.suit]
        text_image = self.font.render(text, True, color)
        image.blit(text_image, text_image.get_rect(center=rect.center))
        return image


def make_deck():
    return [Card(suit, rank) for suit, rank in it.product(SUITS, RANKS)]

def render_rect(size, fill, border):
    surf = pygame.Surface(size)
    surf.fill(fill)
    pygame.draw.rect(surf, border, surf.get_rect(), 1)
    return surf

def unionall(rects):
    rect, *sequence = rects
    return rect.unionall(sequence)

def copyrect(rect, **kwargs):
    result = rect.copy()
    for key, val in kwargs.items():
        setattr(result, key, val)
    return result

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

    solitaire = Solitaire()
    deck = make_deck()
    assert len(deck) == 52
    random.shuffle(deck)
    solitaire.setup(deck)
    solitaire.reveal_stock()

    pygame.font.init()
    font = pygame.font.SysFont('monospace', 24)
    screen = pygame.display.set_mode((800,)*2)
    window = screen.get_rect()
    solitaire_rect = window.inflate((-min(window.size)/6,)*2)
    clock = pygame.time.Clock()
    framerate = 60

    card_size = pygame.Vector2(window.width//18, window.height//12)
    card_rect = pygame.Rect((0,0), card_size)

    stock_rect = pygame.Rect((solitaire_rect.x, solitaire_rect.y), card_size)
    waste_rect = pygame.Rect(stock_rect.topright, card_size)

    foundations_rects = {
        suit: pygame.Rect(
            (
                solitaire_rect.right - i * card_size.x - card_size.x,
                solitaire_rect.y,
            ),
            card_size
        )
        for i, suit in enumerate(SUITS)
    }

    tableau_rects = {
        i + 1: pygame.Rect(
            (
                solitaire_rect.left + i * card_size.x,
                solitaire_rect.y + card_size.y * 1.25,
            ),
            card_size
        )
        for i, max_ in enumerate(sorted(solitaire.tableau))
    }

    origin = unionall(tableau_rects.values())
    dest = copyrect(origin, centerx = solitaire_rect.centerx)
    delta = pygame.Vector2(dest.topleft) - origin.topleft
    for rect in tableau_rects.values():
        rect.topleft += delta

    piles_rects = {
        'stock': stock_rect,
        'waste': waste_rect,
        'foundations': foundations_rects,
        'tableau': tableau_rects,
    }

    face_down_image = render_rect(card_size, 'gray20', 'gray30')

    card_image_maker = CardImage(card_size, font)

    cards_group = pygame.sprite.Group()
    cards_sprites = {}

    for pile_name in ['stock', 'waste']:
        pile = getattr(solitaire, pile_name)
        pile_rect = piles_rects[pile_name]
        for card in pile:
            card_image = card_image_maker(card)
            sprite = CardSprite(card, face_down_image, card_image, cards_group)
            sprite.rect.topleft = pile_rect.topleft
            cards_sprites[card] = sprite

    for max_, pile in solitaire.tableau.items():
        refrect = tableau_rects[max_]
        for i, card in enumerate(pile):
            card_image = card_image_maker(card)
            sprite = CardSprite(card, face_down_image, card_image, cards_group)
            y = min(
                refrect.y + card_size[1] * i * .25,
                solitaire_rect.bottom - card_size[1] * 1.25
            )
            sprite.rect.topleft = (refrect.x, y)

    running = True
    while running:
        elapsed = clock.tick(framerate)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
        screen.fill('black')
        cards_group.draw(screen)
        pygame.draw.rect(screen, 'magenta', solitaire_rect, 1)
        pygame.draw.rect(screen, 'red', stock_rect, 1)
        pygame.draw.rect(screen, 'brown', waste_rect, 1)

        dicts = [foundations_rects, tableau_rects]
        colors = ['yellow', 'coral']
        for rectsdict, color in zip(dicts, colors):
            for rect in rectsdict.values():
                pygame.draw.rect(screen, color, rect, 1)

        pygame.display.flip()

if __name__ == '__main__':
    main()

# https://cardgames.io/solitaire/
