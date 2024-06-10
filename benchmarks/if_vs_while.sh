#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

setup="some_list = []"

echo if
python -m timeit --setup "${setup}" -- "if some_list: pass"

echo while
python -m timeit --setup "${setup}" -- "while some_list: break"

# 2024-05-10
# If `some_list` is empty, is `if some_list` faster than `while some_list`?
# - They are fractions of a nsec different. `if` being slightly faster after
#   spamming runs. Probably due to `break`.
