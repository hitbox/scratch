#!/usr/bin/env sh

python make_arena.py 600 --percent 10 | python wireroute.py -
