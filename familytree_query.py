import operator as op

from pprint import pprint

facts = {
    ('female', 'alice'),
    ('female', 'jessica'),
    ('female', 'emily'),
    ('female', 'lisa'),
    ('female', 'olivia'),
    ('female', 'rebecca'),
    ('male', 'bob'),
    ('male', 'jack'),
    ('male', 'john'),
    ('male', 'peter'),
    ('male', 'mortimer'),

    ('parent', 'alice', 'lisa'),
    ('parent', 'bob', 'peter'),
    ('parent', 'jessica', 'alice'),
    ('parent', 'john', 'alice'),
    ('parent', 'john', 'bob'),
    ('parent', 'lisa', 'emily'),
    ('parent', 'lisa', 'jack'),
    ('parent', 'mortimer', 'alice'),
    ('parent', 'peter', 'jack'),
    ('parent', 'peter', 'olivia'),
    ('parent', 'peter', 'rebecca'),
}

def get_all(*predicates):
    for fact in facts:
        if all(map(op.eq, predicates, fact)):
            yield fact

def iter_humans():
    for fact in facts:
        if fact[0] in ('male', 'female'):
            yield ('human', fact[1])

def iter_children():
    for _, parent, child in get_all('parent'):
        yield ('child', child, parent)

def is_grandparent(parent, child):
    for _, candidate, _ in get_all('parent', child):
        if ('parent', candidate, parent) in facts:
            return candidate

def iter_grandparents():
    for _, parent1, child1 in get_all('parent'):
        for _, parent2, child2 in get_all('parent'):
            if child2 == parent1:
                yield ('grandparent', parent2, child1)

def iter_granddaughters():
    for _, grandparent, grandchild in iter_grandparents():
        if ('female', grandchild) in facts:
            yield ('grandaughter', grandchild, grandparent)

def iter_parentless():
    # gods?
    children = set(('child', child) for _, child, _ in iter_children())
    for _, human in iter_humans():
        if ('child', human) not in children:
            yield ('parentless', human)

def iter_siblings(same_sex=None):
    seen = set()
    for _, parent1, child1 in get_all('parent'):
        for _, parent2, child2 in get_all('parent'):
            if (
                parent1 == parent2
                and
                child1 != child2
                and
                (child1, child2) not in seen
            ):
                if (
                    same_sex is not None
                    and
                    not (
                        (same_sex, child1) in facts
                        and
                        (same_sex, child2) in facts)
                    ):
                        continue
                yield ('sibling', child1, child2)
                seen.add((child1, child2))
                seen.add((child2, child1))

def iter_brothers():
    for _, child1, child2 in iter_siblings(same_sex='male'):
        yield ('brother', child1, child2)

def iter_sisters():
    for _, child1, child2 in iter_siblings(same_sex='female'):
        yield ('sister', child1, child2)

def iter_parents_siblings():
    seen = set()
    for _, child, parent in iter_children():
        for _, sibling1, sibling2 in iter_siblings():
            if parent == sibling1:
                yield ('parent-sibling', sibling2, child)
                seen.add((sibling2, child))
            if parent == sibling2:
                yield ('parent-sibling', sibling1, child)
                seen.add((sibling1, child))

pprint(set(iter_grandparents()))
#pprint(set(iter_siblings()))
#pprint(set(iter_brothers()))
#pprint(set(iter_sisters()))
#pprint(set(iter_parents_siblings()))
