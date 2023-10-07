import os

class Group:

    def __init__(self):
        self.children = []


class Garbage:

    def __init__(self):
        self.characters = ""

    def count(self):
        ignore = False
        n = 0
        for char in self.characters[1:-1]:
            if ignore:
                ignore = False
                continue
            elif char == "!":
                ignore = True
            else:
                n += 1
        return n


def parse(iterator):
    ignore = False
    result = None
    current = None
    stack = []
    for char in iterator:
        if stack and isinstance(stack[-1], Garbage):
            stack[-1].characters += char
            if ignore:
                ignore = False
                continue
            if char == "!":
                ignore = True

            elif char == ">":
                if stack:
                    garbage = stack.pop()
                    stack[-1].children.append(garbage)
        else:
            if char == "{":
                new = Group()
                if stack:
                    stack[-1].children.append(new)
                stack.append(new)

            elif char == "<":
                new = Garbage()
                new.characters += char
                stack.append(new)

            elif char == "}":
                if stack:
                    result = stack.pop()

            elif char == ",":
                pass

    return result

def score(root, n=1):
    childscore = 0
    for child in root.children:
        if isinstance(child, Group):
            childscore += score(child, n+1)
    return n + childscore

def count_garbage(root, n=0):
    childcount = 0
    for child in root.children:
        if isinstance(child, Group):
            childcount += count_garbage(child)
        else:
            childcount += child.count()
    return childcount

def tests():
    rv = parse(iter("{}"))
    assert isinstance(rv, Group) and len(rv.children) == 0

    rv = parse(iter("{{{}}}"))
    assert (isinstance(rv, Group)
            and len(rv.children) == 1
            and isinstance(rv.children[0], Group)
            and len(rv.children[0].children) == 1
            and isinstance(rv.children[0].children[0], Group))

    rv = parse(iter("{{},{}}"))
    assert (isinstance(rv, Group)
            and len(rv.children) == 2
            and all(isinstance(child, Group) for child in rv.children))

    rv = parse(iter("{{{},{},{{}}}}"))
    assert (isinstance(rv, Group)
            and len(rv.children) == 1
            and isinstance(rv.children[0], Group)
            and len(rv.children[0].children) == 3
            and all(isinstance(child, Group) for child in rv.children[0].children)
            and len(rv.children[0].children[-1].children) == 1
            and isinstance(rv.children[0].children[-1].children[0], Group))

    rv = parse(iter("{<{},{},{{}}>}"))
    assert isinstance(rv, Group) and len(rv.children) == 1 and isinstance(rv.children[0], Garbage)

    rv = parse(iter("{<a>,<a>,<a>,<a>}"))
    assert isinstance(rv, Group) and len(rv.children) == 4 and all(isinstance(child, Garbage) for child in rv.children)

    rv = parse(iter("{{<a>},{<a>},{<a>},{<a>}}"))
    assert isinstance(rv, Group) and len(rv.children) == 4 and all(isinstance(child, Group) for child in rv.children)

    rv = parse(iter("{{<!>},{<!>},{<!>},{<a>}}"))
    assert isinstance(rv, Group) and len(rv.children) == 1 and isinstance(rv.children[0], Group)

    assert score(parse(iter("{}"))) == 1
    assert score(parse(iter("{{{}}}"))) == 6
    assert score(parse(iter("{{},{}}"))) == 5
    assert score(parse(iter("{{{},{},{{}}}}"))) == 16
    assert score(parse(iter("{<a>,<a>,<a>,<a>}"))) == 1
    assert score(parse(iter("{{<ab>},{<ab>},{<ab>},{<ab>}}"))) == 9
    assert score(parse(iter("{{<!!>},{<!!>},{<!!>},{<!!>}}"))) == 9
    assert score(parse(iter("{{<a!>},{<a!>},{<a!>},{<ab>}}"))) == 3

    # my parser doesn't handle Garbage-only strings.
    assert count_garbage(parse(iter("{<>}"))) == 0
    assert count_garbage(parse(iter("{<random characters>}"))) == 17
    assert count_garbage(parse(iter("{<<<<>}"))) == 3
    assert count_garbage(parse(iter("{<{!>}>}"))) == 2
    assert count_garbage(parse(iter("{<!!>}"))) == 0
    assert count_garbage(parse(iter("{<!!!>>}"))) == 0
    assert count_garbage(parse(iter("""{<{o"i!a,<{i<a>}"""))) == 10

def main():
    tests()

    inputstr = open(os.path.join(os.path.dirname(__file__), "input.txt")).read()

    print("part 1: %s" % (score(parse(iter(inputstr))), ))
    print("part 2: %s" % (count_garbage(parse(iter(inputstr))), ))

if __name__ == "__main__":
    main()
