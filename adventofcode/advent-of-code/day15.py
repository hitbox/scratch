#!python
import re
from itertools import permutations
from pprint import pprint as pp
from adventlib import input_path

FIELDS = 'capacity durability flavor texture calories'.split()

def mklineparser():
    mkgpattern = lambda name: '{name} (?P<{name}>\-?\d)'.format(name=name)
    pattern = '(?P<name>[A-Z][a-z]+): ' + ', '.join(map(mkgpattern, FIELDS))
    return re.compile(pattern).match

def parse(text):
    lineparser = mklineparser()

    r = {}
    for line in text.splitlines():
        match = lineparser(line)
        if match:
            d = match.groupdict()
            r[d['name']] = { k:int(v) for k,v in d.items() if k != 'name' }

    return r

SCOREFIELDS = [f for f in FIELDS if f != 'calories']

def score(ingredients, recipe):
    total = 1
    for scorefield in SCOREFIELDS:

        fieldtotal = 0
        for ingredient, teaspoons in recipe.items():
            fieldvalue = ingredients[ingredient][scorefield]
            fieldscore = fieldvalue * teaspoons
            fieldtotal += fieldscore

        if fieldtotal < 0:
            fieldtotal = 0
        total *= fieldtotal

    return total

def distributions(n):
    # all possible portions of n ingredients
    return ( c for c in permutations(range(1, 100), n) if sum(c) == 100 )

def get_recipes(ingredients):
    recipes = []
    for dist in distributions(len(ingredients)):
        recipe = dict(zip(ingredients.keys(), dist))
        recipes.append( (recipe, score(ingredients, recipe)) )
    return recipes

def calories(ingredients, recipe):
    return sum(ingredients[ingredient]['calories'] * amount for ingredient, amount in recipe.items())

def test():
    SAMPLE = """Butterscotch: capacity -1, durability -2, flavor 6, texture 3, calories 8
Cinnamon: capacity 2, durability 3, flavor -2, texture -1, calories 3"""

    ingredients = parse(SAMPLE)
    recipes = get_recipes(ingredients)

    assert max(r[1] for r in recipes) == 62842880

    assert max(r[1] for r in recipes if calories(ingredients, r[0]) == 500) == 57600000


def main():
    ingredients = parse(open(input_path(__file__, 1)).read())

    recipes = get_recipes(ingredients)

    print 'Part 1: %s' % max(r[1] for r in recipes)

    recipes = [ recipe_tuple for recipe_tuple in recipes
                             if calories(ingredients, recipe_tuple[0]) == 500 ]

    print 'Part 2: %s' % max(r[1] for r in recipes)
    #answer: 18965440

if __name__ == '__main__':
    test()
    main()
