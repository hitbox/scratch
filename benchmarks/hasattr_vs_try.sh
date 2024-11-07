#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

SETUP=$(cat <<EOF
class C:
    pass
c = C()
c.a = 1
EOF
)

echo "hasattr"
python -m timeit -s "${SETUP}" -- 'if hasattr(c, "a"):' ' c.a'

echo "getattr"
python -m timeit -s "${SETUP}" -- 'getattr(c, "a", None)'

echo "getattr without default"
python -m timeit -s "${SETUP}" -- 'getattr(c, "a")'

echo "try...except"
python -m timeit -s "${SETUP}" -- \
    'try:' \
    ' c.a' \
    'except AttributeError:' \
    ' pass'

# 2024-11-07 Thu.
# - try...except is much faster.
