import itertools as it

SUITS = 'HSDC'
RANK_NAME = {
    1: 'A',
    11: 'J',
    12: 'Q',
    13: 'K',
}
RANKS = list(range(1,14))
RANKS = [RANK_NAME.get(rank, rank) for rank in range(1,14)]

# number of starting card in each pile
TABLEAUS = list(range(1,8))

class ValidationError(Exception):
    pass


class Card:

    def __init__(self, suit, rank, facing=False):
        self.suit = suit
        self.rank = rank
        self.facing = facing

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                other.suit == self.suit
                and
                other.rank == self.rank
            )
        suit, rank = other
        rank = int(rank)
        return suit == self.suit and rank == self.rank

    def __hash__(self):
        return hash((self.suit, self.rank))

    def face_text(self):
        return f'{self.suit}{self.rank}'


class Pile:

    def __init__(self, cards=None, validators=None):
        if cards is None:
            cards = []
        self.cards = cards
        if validators is None:
            validators = []
        self.validators = validators

    def validate_card(self, card, game):
        # validate card is allowed on pile
        for validator in self.validators:
            validator(card, self, game)


class Solitaire:

    def __init__(self):
        self.suits = list(SUITS)
        self.tableaus = list(TABLEAUS)
        self.piles = dict(
            stock = Pile(
                validators = [
                    validate_draw_only,
                ],
            ),
            waste = Pile(),
            foundations = [
                Pile(
                    validators = [
                        validate_suit(
                            suits = [suit],
                        ),
                    ],
                )
                for suit in self.suits
            ],
            tableau = [
                Pile(
                    validators = [
                        validate_rank,
                    ],
                )
                for _ in self.tableaus
            ]
        )

    def setup(self, deck):
        # TODO
        # - aces up on the foundations?
        for max_, pile in enumerate(self.piles['tableau'], start=1):
            for i in range(max_):
                card = deck.pop()
                is_last = i == max_ - 1
                if is_last:
                    card.facing = True
                pile.cards.append(card)
        self.piles['stock'].cards = deck

    def iter_piles(self):
        for pile in [self.stock, self.waste]:
            yield pile
        for piledict in [self.foundations, self.tableau]:
            yield from piledict.values()

    def iter_cards(self):
        for pile in self.iter_piles():
            yield from pile

    def iter_cards_with_pilename(self):
        for pile_name in ['stock', 'waste']:
            pile = getattr(self, pile_name)
            for card in pile:
                yield (card, pile_name)
        for piledict_name in ['foundations', 'tableau']:
            piledict = getattr(self, piledict_name)
            for pile in piledict.values():
                for card in pile:
                    yield (card, piledict_name)

    def find_pile(self, card):
        for other, pile_name in self.iter_cards_with_pilename():
            if other == card:
                return pile_name

    def draw(self, pilename, n=1):
        from_pile = self.piles[pilename]
        to_pile = self.piles['waste']
        for _ in range(n):
            card = from_pile.cards.pop()
            card.facing = True
            to_pile.cards.append(card)

    def move_card(self, card, pile):
        pass


class validate_suit:

    def __init__(self, suits):
        self.suits = suits

    def __call__(self, card, pile, game):
        if card.suit not in self.suits:
            raise ValidationError('Invalid suit')


def validate_draw_only(card, pile, game):
    raise ValidationError('Draw only pile')

def validate_rank(card, pile, game):
    assert pile.cards[-1].facing
    top_card = pile.cards[-1]
    if top_card.rank - card.rank != 1:
        raise ValidationError('Invalid rank')

def make_deck():
    return [Card(suit, rank) for suit, rank in it.product(SUITS, RANKS)]

# https://cardgames.io/solitaire/
