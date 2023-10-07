#!python
from itertools import repeat
from pprint import pprint as pp
from adventlib import input_path

SHOP = """\
Weapons:    Cost  Damage  Armor
Dagger        8     4       0
Shortsword   10     5       0
Warhammer    25     6       0
Longsword    40     7       0
Greataxe     74     8       0

Armor:      Cost  Damage  Armor
Leather      13     0       1
Chainmail    31     0       2
Splintmail   53     0       3
Bandedmail   75     0       4
Platemail   102     0       5

Rings:      Cost  Damage  Armor
Damage +1    25     1       0
Damage +2    50     2       0
Damage +3   100     3       0
Defense +1   20     0       1
Defense +2   40     0       2
Defense +3   80     0       3"""

def parse_shop(text):
    shop = {}
    for line in text.splitlines():
        if ':' in line:
            parts = line.split(':')
            itemtype = parts[0]
            fields = parts[1].strip().split()
            shop[itemtype] = []
        elif line:
            parts = line.split()

            name = parts[0]
            if '+' in line:
                name += ' ' + parts[1]

            item = dict(zip(fields, map(int, parts[-3:])))
            item['name'] = name
            shop[itemtype].append(item)
    return shop

def parse_input(text):
    stats = {}
    for line in text.splitlines():
        key, val = line.split(':')
        stats[key.replace(' ', '').lower()] = int(val.strip())
    return stats

def fight(player, boss):
    player = player.copy()
    boss = boss.copy()

    while True:
        boss['hitpoints'] -= max(1, player['damage']) - boss['armor']
        if boss['hitpoints'] < 1:
            return player

        player['hitpoints'] -= max(1, boss['damage']) - player['armor']
        if player['hitpoints'] < 1:
            return boss

def tests():
    player = dict(name='player', hitpoints=8, damage=5, armor=5)
    boss = dict(name='boss', hitpoints=12, damage=7, armor=2)
    assert fight(player, boss)['name'] == 'player'

def equipiter(shop):
    for weapon in shop['Weapons']:

        armors = [None] + shop['Armor']
        for armor in armors:

            rings1 = [None] + shop['Rings']
            for ring1 in rings1:

                rings2 = [None] + shop['Rings']
                for ring2 in rings2:

                    if ring1 != ring2 or (ring1 is None and ring2 is None):
                        yield dict(weapon=weapon, armor=armor, rings=[ring1, ring2])

def get_player(base, equip):
    hitpoints = base['hitpoints']

    armor_value = (base['armor']
                   # parenthesis bit me here (values weren't adding correctly without them)
                   + (equip['armor']['Armor'] if equip['armor'] else 0)
                   + sum(ring['Armor'] for ring in equip['rings'] if ring is not None))

    damage_value = (base['damage']
                    + (equip['weapon']['Damage'] if equip['weapon'] else 0)
                    + sum(ring['Damage'] for ring in equip['rings'] if ring is not None))

    return dict(name=base['name'], hitpoints=hitpoints, armor=armor_value, damage=damage_value)

def get_cost(equip):
    x = sum(v.get('Cost', 0) for k,v in equip.items() if k in ('weapon', 'armor') and v is not None)
    y = sum(ring.get('Cost', 0) for ring in equip.get('rings', []) if ring is not None)
    return x + y

def init():
    player = dict(name='player', hitpoints=100, damage=0, armor=0)

    boss_text = open(input_path(__file__, 1)).read()
    boss = parse_input(boss_text)
    boss['name'] = 'boss'

    shop = parse_shop(SHOP)

    return player, boss, shop

def part1():
    print '== part 1 =='
    player, boss, shop = init()
    winners = []
    for equip in equipiter(shop):
        test_player = get_player(player, equip)
        if fight(test_player, boss)['name'] == 'player':
            winners.append( (get_cost(equip), equip) )

    print '== least cost equip that wins =='
    pp(min(winners, key=lambda t: t[0]))

def part2():
    print '== part 2 =='
    player, boss, shop = init()
    losers = []
    for equip in equipiter(shop):
        test_player = get_player(player, equip)
        if fight(test_player, boss)['name'] != 'player':
            losers.append( (get_cost(equip), equip) )

    print '== most cost to lose =='
    pp(max(losers, key=lambda t: t[0]))


def main():
    tests()
    part1()
    part2()

if __name__ == '__main__':
    main()
