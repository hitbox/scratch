# https://code.activestate.com/recipes/365013-linear-equations-solver-in-3-lines/?in=lang-python

# this seems like something cheap is going on

def solve(eq, var='x'):
    eq1 = eq.replace("=", "-(") + ")"
    c = eval(eq1, {var: 1j})
    return -c.real / c.imag

assert solve("x - 2*x + 5*x - 46*(235-24) = x + 2") == 3236.0
