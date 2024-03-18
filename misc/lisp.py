class ParseError(Exception):
    pass


def tokenize(expr):
    return expr.replace('(', ' ( ').replace(')', ' ) ').split()

def parse(tokens, _is_open=None):
    expr = []
    tokens = iter(tokens)
    for token in tokens:
        if _is_open == ')' and token == _is_open:
            return expr
        elif _is_open and token[-1] == _is_open:
            return expr + [token]
        elif token == '(':
            expr.append(parse(tokens, _is_open=')'))
        elif token[0] in ("'", '"'):
            expr.append(''.join([token] + parse(tokens, _is_open=token[0])))
        else:
            expr.append(token)
    return expr

def dev(string):
    tokens = tokenize(string)
    print(f'{tokens=}')
    expr = list(parse(tokens))
    print(f'{expr=}')

dev('1')
dev('(+ 1 2)')
dev('(list 1 "some text" 2 3)')

# dicking around
# was reading:
# http://www.arclanguage.org/tut.txt
# https://github.com/kimtg/Arcpp/blob/master/arc.cpp
# https://www.reddit.com/r/lisp/comments/15miz6r/arcpp_a_c_implementation_of_the_arc_programming/
