import argparse
import functools
import logging
import os
import re

def load():
    return open(os.path.join(os.path.dirname(__file__), 'input.txt')).read()

class Entity(object):

    def __init__(self, name, *chips):
        self.name = name
        self.chips = list(chips)
        self.compared = []

    def __str__(self):
        return self.name

    def givechips(self):
        comparison = tuple(self.chips)
        if comparison not in self.compared:
            self.compared.append(comparison)
        low, high = min(self.chips), max(self.chips)
        self.chips.clear()
        return (low, high)


class Instruction(object):

    def __init__(self, entity, lowto, highto):
        self.entity = entity
        self.lowto = lowto
        self.highto = highto

    def __str__(self):
        return '%s gives low to %s and high to %s' % (self.entity, self.lowto, self.highto)

    def __iter__(self):
        return iter((self.entity, self.lowto, self.highto))


class Resolver(object):

    def __init__(self, instructions):
        self.entities = []
        self.instructions = []
        self.goes_to = []
        self.parse_instructions(instructions)
        self.log = logging.getLogger('resolver')

    def one_or_new(self, name):
        for entity in self.entities:
            if entity.name == name:
                break
        else:
            entity = Entity(name)
            self.entities.append(entity)
        return entity

    def parse_instructions(self, instructions):
        assign_re = re.compile('value (\d+) goes to (bot \d+)').match
        instruction_re = re.compile(
                '(bot \d+) gives low to (bot \d+|input \d+|output \d+)'
                ' and high to (bot \d+|input \d+|output \d+)').match

        for line in instructions.splitlines():
            m = assign_re(line)
            if m:
                chip, name = m.groups()
                chip = int(chip)
                entity = self.one_or_new(name)
                entity.chips.append(chip)
                self.goes_to.append((chip, entity))
                continue

            m = instruction_re(line)
            if m:
                entities = [self.one_or_new(name) for name in m.groups()]
                entity, lowto, highto = entities
                self.instructions.append(Instruction(entity, lowto, highto))
                continue

    def buckets(self):
        return (entity for entity in self.entities
                       if entity.name.startswith('input')
                          or entity.name.startswith('output'))

    def bots(self):
        return (entity for entity in self.entities if entity.name.startswith('bot'))

    def stop(self):
        return self.iterations > 1

    def solve(self, stop=None, step_on_debug=False):

        if stop is None:
            stop = self.stop

        step = step_on_debug and logging.getLogger().level == logging.DEBUG

        self.iterations = 0
        while not stop():
            self.log.debug('iteration: %s' % self.iterations)
            self.update()
            if step:
                input('return to continue')
            self.iterations += 1

    def part2_interest(self):
        for bucket in self.buckets():
            _, id_ = bucket.name.split()
            if id_ in '012' and bucket.chips:
                self.log.debug('"%s" has %s' % (bucket, bucket.chips))

    def update(self):
        self.part2_interest()
        for chip, entity in self.goes_to:
            if len(entity.chips) < 2:
                for bucket in self.buckets():
                    if chip in bucket.chips:
                        self.log.debug('"%s" takes "%s" from "%s"' % (entity, chip, bucket))
                        bucket.chips.remove(chip)
                        entity.chips.append(chip)
                        break

        for instruction in self.instructions:
            entity, lowto, highto = instruction

            if len(entity.chips) != 2:
                continue

            low, high = entity.givechips()

            lowto.chips.append(low)
            highto.chips.append(high)

            self.log.debug('"%s" gives low chip "%s" to "%s"'
                           ' and high chip "%s" to "%s"' % (
                               entity, low, lowto, high, highto))

            self.part2_interest()

    def report(self):
        for entity in sorted(self.bots(), key=lambda e: e.name):
            if not entity.compared:
                continue
            cs = ', '.join('%s and %s' % c for c in entity.compared if len(c) == 2)
            print('%s compared %s' % (entity, cs))

    def state(self):
        def key(entity):
            type_, id_ = entity.name.split()
            return (type_, int(id_))

        for e in sorted(self.entities, key=key):
            if not e.chips:
                continue
            self.log.debug('CURRENT: "%s" has chips %s' % (e, e.chips))


def tests():
    instructions = ('value 5 goes to bot 2\n'
                    'bot 2 gives low to bot 1 and high to bot 0\n'
                    'value 3 goes to bot 1\n'
                    'bot 1 gives low to output 1 and high to bot 0\n'
                    'bot 0 gives low to output 2 and high to output 0\n'
                    'value 2 goes to bot 2\n')
    resolver = Resolver(instructions)
    resolver.state()
    resolver.solve()
    resolver.report()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', help='Show debugging ouput')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG,
                            format='%(name)s: %(message)s')

    #tests()

    resolver = Resolver(load())

    def stop():
        for entity in resolver.entities:
            if any(61 in c and 17 in c for c in entity.compared):
                return True

    resolver.solve(stop)

    for entity in resolver.entities:
        for comparison in entity.compared:
            if 61 in comparison and 17 in comparison:
                print('Part 1 answer: %s' % entity.name)

    resolver = Resolver(load())

    values = []
    def stop():
        for bucket in resolver.buckets():
            _, id_ = bucket.name.split()
            if id_ in '012' and bucket.chips:
                print(bucket.chips)
                values.extend(bucket.chips[:])
        if len(values) == 3:
            return True

    resolver.solve(stop)

    print('Part 2 answer: %s' % functools.reduce(lambda a,b: a*b, values))

    # Holy crap this is ugly and stumped me for too long!
    # Started with a complicated "solver" because I made-an-ass-out-of-you-and-me.
    # Took a while to realize the robots need to go take their chips back out of the buckets.
    # Also missed that the robots ONLY give away their chips when they have two.
