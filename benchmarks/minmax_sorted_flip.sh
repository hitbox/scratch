#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

SETUP="a = 2; b = 1"
ASSERT="assert a < b"

python -m timeit --setup $SETUP -- "a, b = min(a, b), max(a, b)" $ASSERT
python -m timeit --setup "import pygame" -- "r = pygame.Rect(0, 0, -10, -10)" "r.normalize()"
python -m timeit --setup $SETUP -- "a, b = sorted([a, b])" $ASSERT
python -m timeit --setup $SETUP -- "if b < a:" "  b, a = a, b" $ASSERT

# 2024-01-25
# - fastest way to sort two values and store in variables
# - if-check-and-flip is super fast
