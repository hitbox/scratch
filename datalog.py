# https://btmc.substack.com/p/implementing-logic-programming

class Variable:

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


class Atom:

    def __init__(self, predicate, terms):
        self.predicate = predicate
        self.terms = terms


class Rule:

    def __init__(self, head, body):
        assert len(body) >= 1
        self.head = head
        self.body = body


class Predicate:

    def __init__(self, name, arity):
        self.name = name
        self.arity = arity
        self.facts = set()
        self.rules = []

    def __getitem__(self, terms):
        # make sure we always work with a tuple
        terms = terms if isinstance(terms, tuple) else (terms,)
        if len(terms) != self.arity:
            raise ValueError()
        return Atom(self.name, terms)

    def __setitem__(self, terms, rhs):
        # make sure we always work with a tuple
        terms = terms if isinstance(terms, tuple) else (terms,)
        # if the rhs is the empty tuple, we're adding a fact
        if rhs == ():
            # NOTE: facts cannot contain variables, add a check!
            self.facts.add(terms)
        elif isinstance(rhs, tuple):
            self.rules.append(Rule(Atom(self.name, terms), rhs))
        else:
            self.rules.append(Rule(Atom(self.name, terms), (rhs,)))


class Datalog:

    def __init__(self):
        self.variables = {}
        self.predicates = {}

    def variable(self, name):
        assert name not in self.variables
        v = Variable(name)
        self.variables[name] = v
        return v

    def predicate(self, name, arity):
        assert name not in self.predicates
        c = Predicate(name, arity)
        self.predicates[name] = c
        return c

    def infer(self):
        while True:
            newly_added_facts = []
            for predicate in self.predicates.values():
                for rule in predicate.rules:
                    for sub in self.evaluate(rule.body):
                        def getsub(term):
                            if isinstance(term, Variable) and term in sub:
                                return sub[term]
                            else:
                                return term
                        fact = tuple(
                            getsub(term)
                            for term in rule.head.terms
                        )
                        if fact not in predicate.facts:
                            newly_added_facts.append((predicate, fact))
            if not newly_added_facts:
                break
            for p, f in newly_added_facts:
                p.facts.add(f)

    def evaluate(self, atoms):
        return self.search(0, atoms, {})

    def search(self, i, atoms, sub):
        if i == len(atoms):
            yield sub
            return
        atom = atoms[i]
        for fact in self.predicates[atom.predicate].facts:
            new_sub = sub.copy()
            if unify(atom, fact, new_sub):
               yield from self.search(i + 1, atoms, new_sub)

    def query(self, *atoms):
        return self.evaluate(atoms)


def unify(atom, fact, substitution):
    for t, v in zip(atom.terms, fact):
        if isinstance(t, Variable):
            if t in substitution and substitution[t] != v:
                return False
            substitution[t] = v
        elif t != v:
            return False
    return True

def original_example():
    dl = Datalog()

    parent = dl.predicate('parent', 2)
    ancestor = dl.predicate('ancestor', 2)

    X, Y, Z = dl.variable('X'), dl.variable('Y'), dl.variable('Z')

    parent['alice', 'bob'] = ()
    parent['bob', 'carol'] = ()
    ancestor[X, Y] = parent[X, Y]
    ancestor[X, Y] = parent[X, Z], ancestor[Z, Y]

    dl.infer()

    for result in dl.query(ancestor[X, 'carol']):
        print(result)

def small_puzzle():
    # https://chatgpt.com/c/684d5fea-9f0c-8003-aa94-329e572434d8
    """
    Awesome! Here's a logic-programming puzzle modeled in your Datalog engine —
    it's a classic “escape the room” scenario where you chain object
    interactions without any imperative code.
    Puzzle Logic

    Goal: Open the door.

    Chain:
        - You need the crowbar to open the door.
        - The crowbar is inside a chest, which is locked.
        - To open the chest, you need the key.
        - The key is under a tile that must be pried up with a screwdriver.
        - The screwdriver is on a shelf.
        - You can reach the shelf if you stack a box.
        - The player starts with the box.
    """
    dl = Datalog()

    # Predicates
    has = dl.predicate('has', 2)
    inside = dl.predicate('inside', 2)
    can_open = dl.predicate('can_open', 2)
    reachable = dl.predicate('reachable', 1)
    on = dl.predicate('on', 2)
    stack = dl.predicate('stack', 1)

    # Variables
    Player = dl.variable('Player')
    Item = dl.variable('Item')
    Container = dl.variable('Container')
    Tool = dl.variable('Tool')

    # Facts
    has['player', 'box'] = ()
    inside['chest', 'crowbar'] = ()
    inside['tile', 'key'] = ()
    on['shelf', 'screwdriver'] = ()

    # Rules
    can_open['player', 'chest'] = has['player', 'key']
    has['player', 'crowbar'] = (
        can_open['player', 'chest'],
        inside['chest', 'crowbar'],
    )

    can_open['player', 'tile'] = has['player', 'screwdriver']
    has['player', 'key'] = can_open['player', 'tile'], inside['tile', 'key']

    reachable['screwdriver'] = (
        has['player', 'box'],
        stack['box'],
        on['shelf', 'screwdriver'],
    )
    has['player', 'screwdriver'] = reachable['screwdriver']

    can_open['player', 'door'] = has['player', 'crowbar']

    # Utility fact: player stacks the box
    stack['box'] = ()

    # Infer all possible truths
    dl.infer()

    # Query: Can player open the door?
    for result in dl.query(can_open['player', 'door']):
        print("Can open door?", result)

small_puzzle()
