#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

echo constants cubed with multiplication
python -m timeit "3 * 3 * 3"
echo

echo constants operator cubed
python -m timeit "3 ** 3"
echo

echo constants math.pow cubed
python -m timeit --setup "import math" "math.pow(3, 3)"
echo

echo constants functools.reduce and operators.mult
python -m timeit \
    --setup "from functools import reduce" \
    --setup "from operator import mul" \
    "reduce(mul, (3,3,3))"
echo

# with variables

echo variable cubed with multiplication
python -m timeit --setup "x = 3" "x * x * x"
echo

echo variable operator cubed
python -m timeit --setup "x = 3" "x ** 3"
echo

echo variable math.pow cubed
python -m timeit --setup "x = 3" --setup "import math" "math.pow(x, x)"
echo

echo constants functools.reduce and operators.mult
python -m timeit \
    --setup "from functools import reduce" \
    --setup "from operator import mul" \
    --setup "x = 3" \
    --setup "t = (x, x, x)" \
    "reduce(mul, t)"

# 2023-12-06
# - Surprising the exponent operator is slower, but only with a variable.
# - math.pow is slow!
# - reduce(mul, ... is slower!
# - so people are correct to multiply instead of exponentiate with the operator
#   and shave 5 nsec or so
