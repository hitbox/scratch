# best psuedocode found so far
# http://www.cs.trincoll.edu/~ram/cpsc352/notes/unification.html
import argparse
import re
import unittest

not_whitespace = re.compile('\S')

class TestToken(unittest.TestCase):

    def test_token(self):
        self.assertEqual(Token('type1', 'value1', 3), Token('type1', 'value1', 3))
        self.assertNotEqual(Token('type1', 'value1', 3), Token('type2', 'value2', 4))


class TestLexer(unittest.TestCase):
    rules = [
        ('\s+', 'WHITESPACE'),
        ('\d+', 'NUMBER'),
        ('[a-zA-Z_]\w*', 'IDENTIFIER'),
        ('\+', 'PLUS'),
        ('\-', 'MINUS'),
        ('\*', 'MULTIPLY'),
        ('\/', 'DIVIDE'),
        ('\(', 'LEFT_PAREN'),
        ('\)', 'RIGHT_PAREN'),
        ('=', 'EQUALS'),
    ]

    def test_lexer_with_whitespace(self):
        lexer = Lexer(self.rules, skip_whitespace=False)
        lexer.input('erw = _abc + 12 * (R4 - 623902)  ')
        tokens = list(lexer.tokens())
        expect = [
            Token(type='IDENTIFIER', val='erw', pos=0),
            Token(type='WHITESPACE', val=' ', pos=3),
            Token(type='EQUALS', val='=', pos=4),
            Token(type='WHITESPACE', val=' ', pos=5),
            Token(type='IDENTIFIER', val='_abc', pos=6),
            Token(type='WHITESPACE', val=' ', pos=10),
            Token(type='PLUS', val='+', pos=11),
            Token(type='WHITESPACE', val=' ', pos=12),
            Token(type='NUMBER', val='12', pos=13),
            Token(type='WHITESPACE', val=' ', pos=15),
            Token(type='MULTIPLY', val='*', pos=16),
            Token(type='WHITESPACE', val=' ', pos=17),
            Token(type='LEFT_PAREN', val='(', pos=18),
            Token(type='IDENTIFIER', val='R4', pos=19),
            Token(type='WHITESPACE', val=' ', pos=21),
            Token(type='MINUS', val='-', pos=22),
            Token(type='WHITESPACE', val=' ', pos=23),
            Token(type='NUMBER', val='623902', pos=24),
            Token(type='RIGHT_PAREN', val=')', pos=30),
            Token(type='WHITESPACE', val='  ', pos=31), # two spaces
        ]
        self.assertEqual(tokens, expect)


class TestTerms(unittest.TestCase):

    def test_variable(self):
        with self.assertRaises(AssertionError):
            Var('not_variable')
        self.assertEqual(Var('X'), Var('X'))

    def test_constant(self):
        self.assertEqual(Const(6), Const(6))

    def test_function_application(self):
        self.assertEqual(
            App('func1', ('X',)),
            App('func1', ('X',)),
        )


class TestParser(unittest.TestCase):

    def check_terms(self, s1, s2):
        t1 = parse_term(s1)
        t2 = parse_term(s2)
        subst = unify(t1, t2, {})
        app1 = apply_unifier(t1, subst)
        app2 = apply_unifier(t2, subst)
        self.assertEqual(app1, app2)

    def test_unify1(self):
        self.check_terms('f(X,h(X),Y,g(Y))', 'f(g(Z),W,Z,X)')

    @unittest.skip("Unsure if this should unify")
    def test_unify2(self):
        # same length args for `p` but `foo(X)` does not unify with `a`(?)
        # plus, need an exception or something to indicate failure to unify
        self.check_terms('p(foo(X), Y)', 'p(a, b)')

    def test_unify3(self):
        self.check_terms('p(Y, Y)', 'p(a, Y)')


class LexerError(Exception):

    def __init__(self, pos):
        self.pos = pos


class ParseError(Exception):
    pass


class Token:

    def __init__(self, type, val, pos):
        self.type = type
        self.val = val
        self.pos = pos

    def __eq__(self, other):
        return (
            type(self) == type(other)
            and self.type == other.type
            and self.val == other.val
            and self.pos == other.pos
        )

    def __str__(self):
        return f'{self.type}({self.val}) at {self.pos}'


class Lexer:

    def __init__(self, rules, skip_whitespace=True, default_token=None):
        self.rules = rules
        self.skip_whitespace = skip_whitespace
        self.default_token = default_token
        patterns, self.group_type = zip(*self.rules)
        grouped_patterns = (f'({pattern})' for pattern in patterns)
        self.regex = re.compile('|'.join(grouped_patterns))

    def input(self, buf):
        self.buf = buf
        self.pos = 0

    def token(self, default_token=None):
        if default_token is None:
            default_token = self.default_token

        if self.pos >= len(self.buf):
            return default_token

        if self.skip_whitespace:
            m = not_whitespace.search(self.buf, self.pos)
            if not m:
                return default_token
            self.pos = m.start()

        m = self.regex.match(self.buf, self.pos)
        if not m:
            raise LexerError(self.pos)

        # first regex group starts at one
        tok_type = self.group_type[m.lastindex - 1]
        tok_val = m.group(m.lastindex)
        tok = Token(tok_type, tok_val, self.pos)
        self.pos = m.end()
        return tok

    def tokens(self):
        while (tok := self.token()):
            yield tok


class Var:
    "Variable"

    def __init__(self, name):
        assert isinstance(name, str) and name[0].isupper()
        self.name = name

    def __str__(self):
        return str(self.name)

    def __eq__(self, other):
        return type(self) is type(other) and self.name == other.name


class Const:
    "Constant"
    # rename as atom?

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        return type(self) is type(other) and self.value == other.value


class App:
    "Function Application"

    def __init__(self, funcname, args=()):
        self.funcname = funcname
        self.args = args

    def __str__(self):
        args_string = ','.join(map(str, self.args))
        return f'{self.funcname}({args_string})'

    def __eq__(self, other):
        return (
            type(self) is type(other)
            and self.funcname == other.funcname
            and all(arg1 == arg2 for arg1, arg2 in zip(self.args, other.args))
        )


class TermParser:

    rules = [
        # (regex pattern, type_name)
        ('\d+', 'NUMBER'),
        ('[a-zA-Z_]\w*', 'ID'),
        (',', 'COMMA'),
        ('\(', 'LEFT_PAREN'),
        ('\)', 'RIGHT_PAREN'),
    ]

    def __init__(self, text, rules=None):
        self.text = text
        self.cur_token = None
        if rules is None:
            rules = self.rules
        self.default_token = Token(None, None, None)
        self.lexer = Lexer(rules, default_token=self.default_token)
        self.lexer.input(self.text)
        self._next_token()

    def _next_token(self):
        self.cur_token = self.lexer.token()

    def parse_term(self):
        if self.cur_token.type == 'NUMBER':
            term = Const(self.cur_token.val)
            # consume the current token and return the Const term
            self._next_token()
            return term
        elif self.cur_token.type == 'ID':
            idtok = self.cur_token
            self._next_token()
            if self.cur_token.type == 'LEFT_PAREN':
                # begin function application
                if idtok.val.isupper():
                    raise ParseError('Function names should be constant')
                self._next_token()
                args = []
                while True:
                    args.append(self.parse_term())
                    cur_type = self.cur_token.type
                    if cur_type not in ('COMMA', 'RIGHT_PAREN'):
                        raise ParseError('Expected "," or ")" in application')
                    self._next_token()
                    if cur_type == 'RIGHT_PAREN':
                        break
                return App(funcname=idtok.val, args=args)
            else:
                if idtok.val.isupper():
                    class_ = Var
                else:
                    class_ = Const
                return class_(idtok.val)


def parse_term(text):
    return TermParser(text).parse_term()

def occurs_check(variable, term, subst):
    assert isinstance(variable, Var)
    if variable == term:
        return True
    elif isinstance(term, Var) and term.name in subst:
        return occurs_check(variable, subst[term.name], subst)
    elif isinstance(term, App):
        return any(occurs_check(variable, arg, subst) for arg in term.args)

def unify_variable(variable, other, subst):
    assert isinstance(variable, Var)
    if variable.name in subst:
        return unify(subst[variable.name], other, subst)
    elif isinstance(other, Var) and other.name in subst:
        return unify(variable, subst[other.name], subst)
    elif occurs_check(variable, other, subst):
        return
    else:
        # variable is not yet in subst
        return {**subst, variable.name: other}

def unify(x, y, subst):
    if x == y:
        return subst
    elif isinstance(x, Var):
        return unify_variable(x, y, subst)
    elif isinstance(y, Var):
        return unify_variable(y, x, subst)
    elif (
        isinstance(x, App)
        and isinstance(y, App)
        and x.funcname == y.funcname
        and len(x.args) == len(y.args)
    ):
        # XXX
        # - can we update like this because all args must unify?
        for args1, args2 in zip(x.args, y.args):
            subst.update(unify(args1, args2, subst))
        return subst

def apply_unifier(x, subst):
    if subst is None:
        return
    elif not subst or isinstance(x, Const):
        return x
    elif isinstance(x, Var):
        if x.name not in subst:
            return x
        else:
            return apply_unifier(subst[x.name], subst)
    elif isinstance(x, App):
        newargs = [apply_unifier(arg, subst) for arg in x.args]
        return App(x.funcname, newargs)

def main(argv=None):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True)
    args = parser.parse_args(argv)

    args.func()

if __name__ == '__main__':
    main()
