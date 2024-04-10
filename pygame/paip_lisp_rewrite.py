FAIL = "fail"

def unify(x, y, bindings=None):
    if bindings is None:
        bindings = {}

    if bindings == FAIL:
        return FAIL
    elif x == y:
        return bindings
    elif is_variable(x):
        return unify_variable(x, y, bindings)
    elif is_variable(y):
        return unify_variable(y, x, bindings)
    elif isinstance(x, list) and isinstance(y, list):
        return unify(x[1:], y[1:], unify(x[0], y[0], bindings))
    else:
        return FAIL

def is_variable(x):
    """
    Is x a variable (a symbol beginning with '?')?
    """
    return isinstance(x, str) and x.startswith('?')

def unify_variable(var, x, bindings):
    """
    Unify var with x, using (and maybe extending) bindings.
    Warning: This is a buggy version.
    """
    if var in bindings:
        return unify(bindings[var], x, bindings)
    else:
        return extend_bindings(var, x, bindings)

def extend_bindings(var, val, bindings):
    """
    Extend bindings dictionary with a new variable-value pair.
    """
    new_bindings = bindings.copy()
    new_bindings[var] = val
    return new_bindings

print(f"{unify('a', 'a')=}")
print(f"{unify('a', 'b')=}")
print(f"{unify('?x', 'b')=}")
print(f"{unify('?x', '?y')=}")
print(f"{unify(['?x', 'b'], ['a', '?y'])=}")
