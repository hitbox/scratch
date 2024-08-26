import unittest

from dataclasses import dataclass

class TestPretty(unittest.TestCase):

    def test_constant(self):
        self.assertEqual(pretty(Const(1)), '1')

    def test_subtract(self):
        expr = Sub(Sub(Const(1), Const(2)), Const(3))
        self.assertEqual(pretty(expr), '1-2-3')

    def test_addition(self):
        expr = Mul(Add(Const(1), Const(2)), Const(3))
        self.assertEqual(pretty(expr), '(1+2)*3')

    def test_division(self):
        expr = Div(Const(1),Sub(Const(1), Const(2)))
        self.assertEqual(pretty(expr), '1/(1-2)')

    def test_exponentiation(self):
        expr = Pow(Add(Const(1), Const(2)), Const(3))
        self.assertEqual(pretty(expr), '(1+2)^3')

        expr = Add(Const(7), Add(Mul(Const(6), Pow(Const(5), Const(2))), Const(3)))
        self.assertEqual(pretty(expr), '7+(6*5^2+3)')


@dataclass
class Expr:
    pass


@dataclass
class Const(Expr):
    value: int | float


@dataclass
class Binary(Expr):
    left: Expr
    right: Expr


@dataclass
class Add(Binary):
    pass


@dataclass
class Sub(Binary):
    pass


@dataclass
class Mul(Binary):
    pass


@dataclass
class Div(Binary):
    pass


@dataclass
class Pow(Binary):
    pass


PRECEDENCE = {
    Add: ("+", "any", 1),
    Sub: ("-", "left", 1),
    Mul: ("*", "any", 2),
    Div: ("/", "left", 2),
    Pow: ("^", "right", 3),
}

def pretty(expr, prec=0):
    match expr:
        case Const(val):
            return str(val)
        case Binary(left, right):
            op, assoc, op_prec = PRECEDENCE[type(expr)]

            left_prec = right_prec = op_prec
            if assoc == "left":
                left_prec -= 1
            if assoc == "right":
                right_prec -= 1

            left_pretty = pretty(left, left_prec)
            right_pretty = pretty(right, right_prec)
            result = left_pretty + op + right_pretty

            if prec >= op_prec:
                result = '(' + result + ')'
            return result
    raise NotImplementedError(type(expr))

# 2024-08-26 Mon.
# https://bernsteinbear.com/blog/precedence-printing/
