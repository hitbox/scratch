import abc
import argparse
import contextlib
import itertools as it
import os
import random

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

class StateBase(abc.ABC):

    @abc.abstractmethod
    def start(self, engine):
        pass

    @abc.abstractmethod
    def update(self, engine):
        pass


class Engine:

    def __init__(self):
        self.running = False

    def run(self, state):
        state.start(engine=self)
        self.running = True
        while self.running:
            state.update(engine=self)


class BeginDrag:

    def __init__(self, sprite):
        self.sprite = sprite


class Dragging:

    def __init__(self, sprite):
        self.sprite = sprite


class CardImage:

    suit_colors = {
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
        color = self.suit_colors[card.suit]
        text_image = self.font.render(text, True, color)
        image.blit(text_image, text_image.get_rect(center=rect.center))
        return image


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


class CardLayout:

    def __init__(self, reference_rect, suits, tableaus):
        self.stock = reference_rect.copy()
        self.waste = reference_rect.copy()
        self.foundations = {suit: reference_rect.copy() for suit in suits}
        self.tableau = {tableau: reference_rect.copy() for tableau in tableaus}

    def reflow(self, playarea, margin):
        # top-left left and right
        stock_and_waste = [self.stock, self.waste]
        flow_right(stock_and_waste, margin)
        movegroup(stock_and_waste, topleft=playarea.topleft)

        # top-right four slots
        flow_right(self.foundations.values(), margin)
        movegroup(self.foundations.values(), topright=playarea.topright)

        # middle-bottom
        flow_right(self.tableau.values(), margin)
        movegroup(self.tableau.values(), center=playarea.center)

    def position_cards(
        self,
        solitaire,
        solitaire_rect,
        card_sprites,
        card_size,
    ):
        for pile_name in ['stock', 'waste']:
            pile = getattr(solitaire, pile_name)
            pile_rect = getattr(self, pile_name)
            for card in pile:
                sprite = card_sprites[card]
                sprite.rect.topleft = pile_rect.topleft

        for max_, pile in solitaire.tableau.items():
            ref_rect = self.tableau[max_]
            # flow_down
            for i, card in enumerate(pile):
                sprite = card_sprites[card]
                y = min(
                    ref_rect.y + card_size.y * i * 0.25,
                    solitaire_rect.bottom - card_size.y * 1.25
                )
                sprite.rect.topleft = (ref_rect.x, y)

    def rects_for_suit(self, suit):
        for other_suit, rect in self.foundations.items():
            if other_suit == suit:
                yield rect


class SolitaireState(StateBase):

    def __init__(self, solitaire):
        self.solitaire = solitaire

    def start(self, engine):
        pygame.font.init()
        self.font = pygame.font.SysFont('monospace', 24)
        self.screen = pygame.display.set_mode((800,)*2)
        self.window = self.screen.get_rect()
        self.clock = pygame.time.Clock()
        self.framerate = 60
        self.elapsed = None
        self.dragging = None

        self.solitaire_rect = make_rect(
            size = pygame.Vector2(self.window.size) * 0.75,
            center = self.window.center,
        )

        self.card_rect = pygame.Rect(
            (0,)*2,
            (self.window.width // 10, self.window.height // 6)
        )

        self.suit_images = {
            suit: suit_image(suit, self.font, self.card_rect.size)
            for suit in self.solitaire.suits
        }

        self.layout = CardLayout(
            self.card_rect,
            self.solitaire.suits,
            self.solitaire.tableaus,
        )
        self.layout.reflow(self.solitaire_rect, self.card_rect.width * 0.10)

        face_down_image = render_rect(self.card_rect.size, 'gray20', 'gray30')
        self.cards_group = pygame.sprite.Group()

        card_image_maker = CardImage(self.card_rect.size, self.font)

        def card_sprite(card):
            return CardSprite(
                card,
                face_down_image,
                card_image_maker(card),
            )

        self.card_sprites = {
            card: card_sprite(card) for card in self.solitaire.iter_cards()
        }
        self.cards_group.add(self.card_sprites.values())

        self.layout.position_cards(
            self.solitaire,
            self.solitaire_rect,
            self.card_sprites,
            pygame.Vector2(self.card_rect.size),
        )

    def update(self, engine):
        # tick clock
        self.elapsed = self.clock.tick(self.framerate)
        # events
        for event in pygame.event.get():
            methodname = event_methodname(event)
            method = getattr(self, methodname, None)
            if method is not None:
                method(engine, event)
        # update
        mouse_pos = pygame.mouse.get_pos()
        mouse_rel = pygame.mouse.get_rel()
        if self.dragging:
            self.dragging.sprite.rect.topleft += pygame.Vector2(mouse_rel)
        # draw
        self.draw(engine)

    def do_quit(self, engine, event):
        engine.running = False

    def do_keydown(self, engine, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def do_mousebuttondown(self, engine, event):

        rects = (sprite.rect for sprite in self.card_sprites.values())

        for card, sprite in self.card_sprites.items():
            if card.facing and sprite.rect.collidepoint(event.pos):
                self.dragging = BeginDrag(sprite)
                break
        else:
            self.dragging = None

    def do_mousemotion(self, engine, event):
        if isinstance(self.dragging, BeginDrag):
            self.dragging = Dragging(
                self.dragging.sprite,
            )
        else:
            # TODO
            # - hover highlight
            pass

    def candidate_rects_for_suit(self, suit):
        for suit, rect in self.layout.foundations.items():
            pass

    def do_mousebuttonup(self, engine, event):
        if isinstance(self.dragging, Dragging):
            drag_sprite = self.dragging.sprite

            # drop card or cards
            if self.layout.stock.colliderect(self.dragging.sprite.rect):
                self.dragging.sprite.rect.topleft = self.layout.stock.topleft
            elif self.layout.waste.colliderect(self.dragging.sprite.rect):
                self.dragging.sprite.rect.topleft = self.layout.waste.topleft
            else:
                # foundations
                rects = self.layout.rects_for_suit(drag_sprite.card.suit)
                rects = (
                    rect for rect in rects
                    if rect is not drag_sprite.rect
                    and rect.colliderect(drag_sprite.rect)
                )

                def overlap_area(rect):
                    return rect_area(drag_sprite.rect.clip(rect))

                rects = sorted(rects, key=overlap_area)
                if rects:
                    drag_sprite.rect.topleft = rects[-1].topleft
                else:
                    # tableau
                    rects = self.layout.tableau.values()
                    rects = (
                        rect for rect in rects
                        if rect is not drag_sprite.rect
                        and rect.colliderect(drag_sprite.rect)
                    )
                    rects = sorted(rects, key=overlap_area)
                    if rects:
                        drag_sprite.rect.topleft = rects[-1].topleft
        self.dragging = None

    def draw(self, engine):
        self.screen.fill('black')
        for suit, ref_rect in self.layout.foundations.items():
            image = self.suit_images[suit]
            self.screen.blit(image, image.get_rect(center=ref_rect.center))
        self.cards_group.draw(self.screen)

        rects = [self.solitaire_rect, self.layout.stock, self.layout.waste]
        rects.extend(self.layout.foundations.values())
        rects.extend(self.layout.tableau.values())
        colors = ['magenta', 'red', 'brown']
        colors.extend(it.repeat('yellow', len(self.layout.foundations)))
        colors.extend(it.repeat('coral', len(self.layout.tableau)))
        for rect, color in zip(rects, colors):
            pygame.draw.rect(self.screen, color, rect, 1)
        pygame.display.flip()

def render_rect(size, fill, border):
    surf = pygame.Surface(size)
    surf.fill(fill)
    pygame.draw.rect(surf, border, surf.get_rect(), 1)
    return surf

def unionall(rects):
    rect, *sequence = rects
    return rect.unionall(sequence)

def make_rect(rect=None, **kwargs):
    if rect is None:
        result = pygame.Rect((0,)*4)
    else:
        result = rect.copy()
    for key, val in kwargs.items():
        setattr(result, key, val)
    return result

def movegroup(rects, **kwargs):
    # in-place
    origin = unionall(rects)
    dest = make_rect(origin, **kwargs)
    delta = pygame.Vector2(dest.topleft) - origin.topleft
    for rect in rects:
        rect.topleft += delta

def flow_right(rects, margin=0):
    for rect1, rect2 in it.pairwise(rects):
        rect2.left = rect1.right + margin

def event_methodname(event, prefix='do_'):
    event_name = pygame.event.event_name(event.type).lower()
    return f'{prefix}{event_name}'

def rect_area(rect):
    return rect.width * rect.height

def suit_image(suit, font, size):
    result = pygame.Surface(size, pygame.SRCALPHA)
    result_rect = result.get_rect()
    text_image = font.render(str(suit), True, 'azure')
    result.blit(text_image, text_image.get_rect(center=result_rect.center))
    return result

def pygame_gui(solitaire):
    state = SolitaireState(solitaire)
    engine = Engine()
    engine.run(state)

    # TODO
    # - "depth" is just happening to work because the sprites are also created
    #   in pile order
    # - left off thinking if there was a better way to organize the piles in
    #   the Solitaire class.
