import argparse
import unittest

class Substitution:

    def __init__(self, variable, replacement):
        self.variable = variable
        self.replacement = replacement

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.variable == other.variable
            and self.replacement == other.replacement
        )

    def __str__(self):
        return f'{self.variable.name}={self.replacement}'


class NameMixin:

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.name == other.name
        )

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name


class Variable(NameMixin):

    def occurs_in(self, other):
        raise NotImplementedError


class Constant(NameMixin):
    pass


class Expression:

    def __init__(self, operator, arguments):
        self.operator = operator
        self.arguments = arguments

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.operator == other.operator
            and self.arguments == other.arguments
        )


class TestParseExpression(unittest.TestCase):

    def check_parse(self, s, expected):
        result = parse_expression(s)
        self.assertEqual(result, expected)

    def test_parse_constant(self):
        self.check_parse('a', Constant('a'))

    def test_parse_variable(self):
        self.check_parse('X', Variable('X'))

    def test_parse_expression_no_args(self):
        self.check_parse('f()', Expression('f', list()))

    def test_parse_expression_constant_arg(self):
        self.check_parse('f(a)', Expression('f', [Constant('a')]))

    def test_parse_expression_variable_arg(self):
        self.check_parse('f(X)', Expression('f', [Variable('X')]))


class TestUnification(unittest.TestCase):

    def check_substitution(self, t1, t2, sub):
        result = unify_with_occurence_check(t1, t2)
        self.assertEqual(result, sub)

    def check_tautology(self, t1, t2):
        self.check_substitution(t1, t2, [])

    def check_no(self, t1, t2):
        self.check_substitution(t1, t2, None)

    def test_tautology_constants(self):
        self.check_tautology(Constant('a'), Constant('a'))

    def test_tautology_variables(self):
        self.check_tautology(Variable('X'), Variable('X'))

    def test_no(self):
        self.check_no(Constant('a'), Constant('b'))

    def test_substitution_constant_and_variable(self):
        a = Constant('a')
        X = Variable('X')
        self.check_substitution(a, X, [Substitution(X, a)])

    def test_substitution_variable_and_variable(self):
        X = Variable('X')
        Y = Variable('Y')
        self.check_substitution(X, Y, [Substitution(X, Y)])

    @unittest.expectedFailure
    def test_function_variable(self):
        raise NotImplementedError


def parse_expression(s):
    d = 0
    i = 0
    op = None
    args = []
    for index, char in enumerate(s):
        if char == '(':
            if op is None:
                op = s[:index]
                i = index + 1
            d += 1
        elif char == ')':
            if d == 1:
                if index > i:
                    args.append(s[i:index])
                    i = index + 1
                d -= 1
        elif char == ',' and d == 1:
            args.append(s[i:index])
            i = index + 1
        elif char == ' ' and i == index:
            i += 1

    if op is None:
        if s[0].isupper():
            return Variable(s)
        else:
            return Constant(s)

    return Expression(op, list(map(parse_expression, args)))

def formulars_match(formular1, formular2):
    return (
        formular1.operator == formular2.operator
        and
        len(formular1.arguments) == len(formular2.arguments)
    )

def substitute(sub, exp):
    for s in (x for x in sub if occurs_in(x.variable, exp)):
        if isinstance(exp, Variable):
            exp = s.replacement
        else:
            exp.arguments = [substitute(sub, e) for e in exp.arguments]
    return exp

def occurs_in(var, exp):
    if var == exp:
        return True
    elif not isinstance(exp, Expression):
        return False
    return any(occurs_in(var, e) for e in exp.arguments)

def unify_variable(var, exp, mgu, trace):
    for s in (x for x in mgu if x.variable == var):
        return unify_with_occurence_check(s.replacement, exp, mgu, trace)
    t = substitute(mgu, exp)
    if isinstance(t, Expression) and occurs_in(var, t):
        # infinite loop
        return
    s = Substitution(var, t)
    mgu.append(s)
    for q in (x for x in mgu if x.replacement == s.variable):
        mgu.remove(q)
        new = Substitution(q.variable, s.replacement)
        mgu.append(new)
    for r in (x for x in mgu if isinstance(x.replacement, Expression)):
        mgu.remove(r)
        a = substitute(mgu, r.replacement)
        b = Substitution(r.variable, a)
        mgu.append(b)
    for s in (x for x in mgu if x.variable == x.replacement):
        mgu.remove(s)
    return mgu

initial_mgu = object()

def unify_with_occurence_check(
    formular1,
    formular2,
    mgu = initial_mgu,
    trace = False):
    """
    """
    if mgu is initial_mgu:
        mgu = []
    if mgu is None:
        return
    elif formular1 == formular2:
        return mgu
    elif isinstance(formular1, Variable):
        return unify_variable(formular1, formular2, mgu, trace)
    elif isinstance(formular2, Variable):
        return unify_variable(formular2, formular1, mgu, trace)
    elif isinstance(formular1, Expression) and isinstance(formular2, Expression):
        if formulars_match(formular1, formular2):
            for arg1, arg2 in zip(formular1.arguments, formular2.arguments):
                mgu = unify_with_occurence_check(arg1, arg2, mgu, trace)
            return mgu

def eval_terms(t1, t2):
    e1 = parse_expression(t1)
    e2 = parse_expression(t2)
    mgu = unify_with_occurence_check(e1, e2)
    return mgu

def print_result(mgu):
    if not mgu:
        print('No')
    else:
        print('Yes')
        print('\n'.join(map(str, mgu)))

def run():
    while True:
        t1 = input('Term 1> ')
        t2 = input('Term 2> ')
        if not (t1 or t2):
            break
        mgu = eval_terms(t1, t2)
        print_result(mgu)

def main(argv=None):
    """
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--term1')
    parser.add_argument('--term2')
    args = parser.parse_args(argv)

    if args.term1 and args.term2:
        mgu = eval_terms(args.term1, args.term2)
        print_result(mgu)
    else:
        run()

if __name__ == '__main__':
    main()

# 2023-10-14 Sat.
# - pretty good looking unify example
#   https://github.com/stanleyeze/Unification-Algorithm/blob/master/UnificationAlgorithm.ipynb
