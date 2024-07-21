from collections import deque

# Variables
variables = ['X1', 'X2', 'X3']

# Domains
domains = {
    'X1': {1, 2, 3},
    'X2': {1, 2, 3},
    'X3': {1, 2, 3},
}

# Constraints: A list of tuples representing pairs of variables with a binary
# inequality constraint
constraints = [
    ('X1', 'X2'),
    ('X2', 'X3'),
    ('X1', 'X3'),
]

def ac3(variables, domains, constraints):
    queue = deque(constraints)
    while queue:
        (xi, xj) = queue.popleft()
        if revise(domains, xi, xj):
            if not domains[xi]:
                # Domain wipeout
                return False
            for xk in (variables - {xi}):
                if (xk, xi) in constraints:
                    queue.append((xk, xi))
    return True

def revise(domains, xi, xj):
    revised = False
    for x in set(domains[xi]):
        if not any(y != x for y in domains[xj]):
            domains[xi].remove(x)
            revised = True
    return revised

# Convert variable list to a set for easier manipulation in AC-3
variable_set = set(variables)

# Perform AC-3
result = ac3(variable_set, domains, constraints)

# Print result
print("AC-3 result:", result)
print("Domains after AC-3:", domains)
