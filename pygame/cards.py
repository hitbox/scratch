import argparse
import random
import unittest

from itertools import cycle
from itertools import product
from pprint import pprint

import pygamelib

from pygamelib import pygame

ranks = ['Ace'] + list(map(str, range(2,11))) + ['Jack', 'Queen', 'King']
suits = ['Spades', 'Hearts', 'Clubs', 'Diamonds']

basic_suits_colors = ['grey13', 'brown'] * 2

SIGNAL = pygame.event.custom_type()

class TestDeck(unittest.TestCase):

    def test_deck_all_possible_cards(self):
        deck = make_standard_deck_indexed0()
        detailed_deck = set(map(card_detail, deck))
        for rank_and_suit in product(ranks, suits):
            self.assertIn(rank_and_suit, detailed_deck)


class Animation:

    def __init__(self, obj, attr, a, b, duration, elapsed):
        self.obj = obj
        self.attr = attr
        self.a = a
        self.b = b
        self.duration = duration
        self.elapsed = elapsed

    def is_remove(self):
        return self.elapsed > self.duration

    def update(self, elapsed):
        self.elapsed += elapsed
        if self.elapsed <= self.duration:
            t = pygamelib.remap(
                self.elapsed,
                0, self.duration,
                0, 1,
            )
            setattr(
                self.obj,
                self.attr,
                pygamelib.lerp(
                    t,
                    self.a,
                    self.b,
                )
            )


class Countdown:

    def __init__(self, duration):
        self.duration = duration

    def is_remove(self):
        return not self.duration

    def update(self, elapsed):
        if self.duration:
            self.duration -= elapsed
            if self.duration < 0:
                self.duration = 0


class Deal:

    def __init__(
        self,
        deck,
        hands,
        to_positions,
        every_ms,
        move_duration,
    ):
        self.deck = deck
        self.hands = hands
        self.every_ms = every_ms
        self.move_duration = move_duration
        self.elapsed = 0
        self.deal_cycle_indexes = cycle(range(len(hands)))

    def is_remove(self):
        return not self.deck

    def update(self, elapsed):
        if self.deck:
            self.elapsed += elapsed
            if self.elapsed > self.every_ms:
                self.elapsed = 0
                deal_to = next(self.deal_cycle_indexes)
                hand = self.hands[deal_to]
                hand.append(self.deck.pop())
                # maybe want to emit a signal and generate an animation from that?


def make_piles(n):
    return [[] for _ in range(n)]

def card_detail(card_index):
    rank_index = card_index % len(ranks)
    suit_index = card_index % len(suits)
    rank = ranks[rank_index]
    suit = suits[suit_index]
    return (rank, suit)

def card_detail_format(card, indent=''):
    rank, suit = card_detail(card)
    return indent + f'{card}: {rank} of {suit}'

def deal(from_, to, n):
    for _ in range(n):
        to.append(from_.pop())

def game_format(game):
    lines = []
    indent = ' ' * 4
    for name, piles in game.items():
        lines.append(f'{name}')
        for pile_index, pile in enumerate(piles):
            if not pile:
                lines.append(indent + f'{pile_index} {name} empty')
            else:
                lines.append(indent + f'{pile_index} {name} {len(pile)}')
                for card in pile:
                    lines.append(card_detail_format(card, indent + indent))
    return lines

def clear_highest(values):
    max_value = max(values)
    if values.count(max_value) == 1:
        return max_value

def make_standard_deck_indexed0():
    return list(range(52))

def play_speed():
    n_players = 2

    deck = list(range(52))
    game = {
        'central_piles': make_piles(n_players),
        'side_piles': make_piles(n_players),
        'draw_piles': make_piles(n_players),
        'hands': make_piles(n_players),
    }

    random.shuffle(deck)

    # twenty cards to each player's draw piles
    for draw_pile in game['draw_piles']:
        deal(deck, draw_pile, 10)

    # five cards from draw piles to each player's hand
    for hand, draw_pile in zip(game['hands'], game['draw_piles']):
        deal(draw_pile, hand, 5)

    # five cards from deck to each side pile
    for side_pile in game['side_piles']:
        deal(deck, side_pile, 5)

def play_war():
    """
    War

    Players: 2
    Objective: Win all the cards.
    Gameplay:
        - The deck is divided equally between two players.
        - Each player reveals the top card of their deck at the same time.
        - The player with the higher card wins both cards and places them at
          the bottom of their deck.
        - If the cards are the same rank (a tie), a "war" happens: players draw
          three face-down cards, then a fourth card face-up, and the highest of
          the new cards wins all the cards.
        - Play continues until one player collects all the cards.
    """
    n_players = 2
    n_cards = 52

    deck = list(range(n_cards))
    random.shuffle(deck)

    game = {'hands': make_piles(n_players)}

    # deal to each player
    for hand in game['hands']:
        deal(deck, hand, n_cards//n_players)

    assert set(game['hands'][0]).isdisjoint(game['hands'][1])

    # n_players of empty reveals lists
    reveals = [[] for _ in range(n_players)]

    while all(game['hands']):
        # each player draws one from their hand
        for hand, reveal in zip(game['hands'], reveals):
            reveal.append(hand.pop())

        assert all(len(reveal) == 1 for reveal in reveals), game['hands']

        other = []
        winner_hand = None
        while not winner_hand and any(reveals):
            # top card of each player's reveal
            top_reveals = [reveal.pop() for reveal in reveals]

            # check winner
            top_reveals_details = list(map(card_detail, top_reveals))

            top_reveals_rank_values = [
                ranks.index(rank) for rank, suit in top_reveals_details
            ]
            highest_value = clear_highest(top_reveals_rank_values)
            if highest_value:
                winner_index = top_reveals_rank_values.index(highest_value)
                winner_hand = game['hands'][winner_index]
                break
            elif not any(reveals):
                # reveal piles are all empty so this is the first draw, now go
                # to war

                # avoid losing the top reveals that we consider
                while top_reveals:
                    other.append(top_reveals.pop())

                # each players draws four
                for hand, reveal in zip(game['hands'], reveals):
                    # take four cards or whole hand
                    for _ in range(4):
                        reveal.append(hand.pop())
                        if not hand:
                            break

        # give cards to winner
        while top_reveals:
            winner_hand.insert(0, top_reveals.pop())
        assert not top_reveals

        for reveal in reveals:
            while reveal:
                winner_hand.insert(0, reveal.pop())
            assert not reveal
        assert not any(reveals)

        while other:
            winner_hand.insert(0, other.pop())
        assert not other

        print(f'{winner_index} wins round {len(winner_hand)=} with {highest_value}')
        for player_index, hand in enumerate(game['hands']):
            if player_index != winner_index:
                print(f'{player_index} has {len(hand)=} left.')

    player_indexes_with_cards = [index for index, hand in enumerate(game['hands']) if hand]
    if len(player_indexes_with_cards) != 1:
        raise ValueError

    winner_index = player_indexes_with_cards[0]
    print(f'{winner_index} wins!')

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

    random.seed(0)
    game = {'hands': [[], []]}

    deal_cycle_indexes = cycle(i for i, _ in enumerate(game['hands']))

    display_size = (900,) * 2
    card_size = (40, 100)

    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(display_size)
    background = screen.copy()
    window = screen.get_rect()

    window_halves = [
        pygame.Rect(window.topleft, window.midbottom),
        pygame.Rect(window.midtop, window.midbottom), # remember second arg is size
    ]

    player_halves = [
        pygamelib.make_rect(
            rect,
            size = (300, 300),
            center = rect.center,
        )
        for rect in window_halves
    ]

    font = pygamelib.monospace_font(20)
    printer = pygamelib.FontPrinter(font, 'azure')

    image = printer(['WAR'])
    background.blit(image, image.get_rect(midtop=window.midtop))

    deck = make_standard_deck_indexed0()
    facing = [False for card in deck]
    random.shuffle(deck)

    back_image = pygame.Surface(card_size)
    back_image.fill('tomato')
    pygame.draw.rect(back_image, 'azure', back_image.get_rect(), 1)

    face_images = {}
    for card_index in deck:
        rank, suit = card_detail(card_index)
        if len(rank) > 1 and not rank.isdigit():
            rank = rank[0]

        background_color = basic_suits_colors[suits.index(suit)]
        image = pygame.Surface(card_size)
        image.fill(background_color)
        text = printer([f'{rank}', f'{suit[0]}'])
        pygame.draw.rect(image, 'azure', image.get_rect(), 1)
        image.blit(text, text.get_rect(center=image.get_rect().center))
        face_images[card_index] = image

    # image to represent a stack of cards
    stack_offset = 4
    stack_image = pygame.Surface((card_size[0] + stack_offset * 3, card_size[1]))
    for i in range(3):
        stack_image.blit(back_image, (stack_offset * i, 0))

    deck_origin = window.center

    begin_deal_countdown = 1000
    # time to move card
    deal_to_duration = 100
    # deal every ms
    deck_deal = 50
    deck_deal_elapsed = 0

    begin_deal_countdown = Countdown(1000)

    updaters = [
        begin_deal_countdown,
    ]
    animations = {}
    blits = []

    elapsed = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()

        # updates
        for updater in updaters:
            updater.update(elapsed)
            if updater.is_remove():
                updaters.remove(updater)

        for image, rect in blits:
            has_ref = (
                updater.obj is rect for updater in updaters
                if isinstance(updater, Animation)
            )
            if not any(has_ref):
                # no rects referenced by animation
                blits.remove((image, rect))

        # update dealing deck
        if deck and not begin_deal_countdown.duration:
            deck_deal_elapsed += elapsed
            if deck_deal_elapsed >= deck_deal:
                deck_deal_elapsed = 0
                deal_to = next(deal_cycle_indexes)
                game['hands'][deal_to].append(deck.pop())
                player_rect = window_halves[deal_to]

                rect = pygamelib.make_rect(size=card_size, center=deck_origin)
                animation = Animation(
                    obj = rect,
                    attr = 'center',
                    a = pygame.Vector2(deck_origin),
                    b = pygame.Vector2(player_rect.center),
                    duration = deal_to_duration,
                    elapsed = 0,
                )
                updaters.append(animation)
                blits.append((back_image, animation.obj))

        # draw
        screen.blit(background, (0,0))

        if deck:
            screen.blit(stack_image, stack_image.get_rect(center=deck_origin))
            image = printer([str(len(deck))])
            screen.blit(image, image.get_rect(center=deck_origin))

        items = enumerate(zip(game['hands'], player_halves))
        for player_index, (hand, player_rect) in items:
            image = printer([f'player: {player_index}'])
            rect = image.get_rect(midbottom=player_rect.midtop)
            screen.blit(image, rect)
            if hand:
                screen.blit(stack_image, stack_image.get_rect(center=player_rect.center))
                image = printer([str(len(hand))])
                screen.blit(image, image.get_rect(center=player_rect.center))

        screen.blits(blits)

        # draw debug
        image = printer([
            f'FPS: {clock.get_fps():.0f}',
            f'{len(animations)=}',
            f'{len(blits)=}',
        ])
        screen.blit(image, (0,0))

        pygame.display.flip()
        elapsed = clock.tick()

    #play_war()

if __name__ == '__main__':
    main()
