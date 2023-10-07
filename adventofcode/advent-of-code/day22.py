#!python
import random
import argparse
from pprint import pprint as pp

from itertools import permutations
from pprint import pprint as pp
from adventlib import input_path, parseargs

DEBUG = False

class Game(object):

    def __init__(self, player, boss, difficulty):
        player.game = self
        self.player = player

        self.boss = boss
        self.spells = []

        self.difficulty = difficulty

    def effects(self):
        for spell in self.spells:
            spell.update(self.boss)
        self.spells = [ spell for spell in self.spells if spell.turns > 0 ]

    def info(self):
        s = '- Player has %s hit points, %s armor, %s mana\n' % (
                self.player.hitpoints, self.player.armor, self.player.mana)
        s += '- Boss has %s hit points' % (self.boss.hitpoints, )
        return s

    def get_winner(self):
        if self.boss.hitpoints <= 0:
            return self.player

        if (self.player.mana == 0 or self.player.hitpoints <= 0):
            return self.boss

    def run(self):
        while True:

            #if DEBUG:
            #    print
            #    print '-- Player turn --'
            #    print self.info()

            if self.difficulty == "hard":
                self.player.hitpoints += -1
                winner = self.get_winner()
                if winner:
                    return winner

            self.effects()
            winner = self.get_winner()
            if winner:
                return winner

            spell = self.player.attack(self.boss)
            if spell is None:
                return self.boss
            winner = self.get_winner()
            if winner:
                return winner

            #if DEBUG:
            #    print
            #    print '-- Boss turn --'
            #    print self.info()

            self.effects()
            winner = self.get_winner()
            if winner:
                return winner

            self.boss.attack(self.player)
            winner = self.get_winner()
            if winner:
                return winner


class Player(object):

    def __init__(self, hitpoints, mana, armor, spellchooser):
        self.hitpoints = hitpoints
        self.mana = mana
        self.armor = armor

        self.spellchooser = spellchooser
        try:
            self.spellchooser.player = self
        except AttributeError:
            pass

        self.casted = []

    def cast(self, spellclass):
        #if DEBUG:
        #    print 'Player casts %s' % (spellclass, )
        spell = spellclass(self)
        self.casted.append(spell)
        self.game.spells.append(spell)
        return spell

    def attack(self, other):
        spell = self.spellchooser()
        if spell is not None:
            return self.cast(spell)


class SpellChooser(object):

    def __init__(self, player=None):
        self.player = player
        self.best = None

    def spells_in_effect(self):
        return self.player.game.spells

    def is_in_effect(self, candidate):
        # candidate is a class
        return any(candidate == spell.__class__ for spell in self.spells_in_effect())

    def candidate_cost(self, candidate):
        return candidate.cost + sum(s.cost for s in self.player.casted)

    def __call__(self):
        candidates = [ candidate for candidate in SPELLS
                       if candidate.cost <= self.player.mana
                          and (self.best is None or self.candidate_cost(candidate) < self.best)
                          and not self.is_in_effect(candidate) ]

        if candidates:
            return random.choice(candidates)


class Boss(object):

    def __init__(self, hitpoints, damage):
        self.hitpoints = hitpoints
        self.damage = damage

    def attack(self, other):
        damage = max(1, self.damage) - other.armor
        other.hitpoints -= damage
        #if DEBUG:
        #    print 'Boss attacks for %s damage' % (damage, )


class Spell(object):

    cost = None
    turns = None

    def __init__(self, player):
        self.player = player
        player.mana -= self.cost
        self.turns = self.turns
        if self.turns is None:
            self.apply(self.player.game.boss)

    def __repr__(self):
        return '<{}(cost={})>'.format(self.__class__.__name__, self.__class__.cost)

    def apply(self, boss):
        pass

    def remove(self):
        pass

    def update(self, boss):
        if self.turns is not None:
            if self.turns > 0:
                self.apply(boss)
            self.turns -= 1
            #if DEBUG:
            #    print '%s timer is now %s' % (self, self.turns)
            if self.turns == 0:
                self.remove()


class MagicMissle(Spell):

    cost = 53

    def apply(self, boss):
        #if DEBUG:
        #    print 'Magic Missle deals 4 damage'
        boss.hitpoints -= 4


class Drain(Spell):

    cost = 73

    def apply(self, boss):
        self.player.hitpoints += 2
        boss.hitpoints -= 2


class Shield(Spell):

    cost = 113
    turns = 6

    def __init__(self, *args):
        super(Shield, self).__init__(*args)
        self.player.armor += 7

    def remove(self):
        self.player.armor -= 7


class Poison(Spell):

    cost = 173
    turns = 6

    def apply(self, boss):
        boss.hitpoints -= 3
        #if DEBUG:
        #    print 'Poison deals 3 damage; its timer is now %s.' % (self.turns - 1, )


class Recharge(Spell):

    cost = 229
    turns = 5

    def apply(self, boss):
        #if DEBUG:
        #    print 'Recharge provides 101 mana; its timer is now %s.' % (self.turns - 1, )
        self.player.mana += 101


SPELLS = [MagicMissle, Drain, Shield, Poison, Recharge]

def get_boss_from_input():
    text = open(input_path(__file__, 1)).read()
    stats = {}
    for line in text.splitlines():
        k, v = line.split(':')
        stats[k.replace(' ', '').lower()] = int(v)
    return Boss(**stats)

def init():
    player = Player(50, 500, 0)
    boss = get_boss_from_input()
    game = Game(player, boss)
    return game

def mkspellchooser(l):
    return l[::-1].pop

def test1():
    if DEBUG:
        print '== Test 1=='
    player = Player(10, 250, 0, mkspellchooser([Poison, MagicMissle]))
    boss = Boss(13, 8)
    game = Game(player, boss, "easy")
    winner = game.run()
    assert (winner == player and game.player.hitpoints == 2 and
            game.player.armor == 0 and game.player.mana == 24)
    if DEBUG:
        print winner

def cost(spells):
    return sum(spell.cost for spell in spells)

def test2():
    # add check for stats
    if DEBUG:
        print '== Test 2 =='
    player = Player(10, 250, 0, mkspellchooser([Recharge, Shield, Drain, Poison, MagicMissle]))
    boss = Boss(14, 8)
    game = Game(player, boss, "easy")
    winner = game.run()
    assert (winner == player and game.player.hitpoints == 1 and
            game.player.armor == 0 and game.player.mana == 114)
    if DEBUG:
        print winner

def get_spellplans(n):
    pspells = SPELLS[:]
    while len(pspells) < n:
        pspells += pspells
    return permutations(pspells, n)

def bestgenerator(difficulty):
    spellchooser = SpellChooser()

    while True:
        player = Player(50, 500, 0, spellchooser)
        boss = get_boss_from_input()
        game = Game(player, boss, difficulty)
        winner = game.run()
        if winner == player:
            winning_cost = cost(game.player.casted)
            if spellchooser.best is None or winning_cost < spellchooser.best:
                spellchooser.best = winning_cost
                print '== New Best =='
                print winning_cost
                pp(game.player.casted)

def part1():
    bestgenerator("easy")

def part2():
    bestgenerator("hard")

def main():
    args = parseargs(requirepart=True)

    test1()
    test2()

    if args.part == 1:
        part1()
    elif args.part == 2:
        part2()

if __name__ == '__main__':
    main()
