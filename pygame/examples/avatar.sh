#!/usr/bin/env sh

# this was tricky to get working
# example serves to remind how somethig was made to work

python avatar.py --seed 0 --size 8 | convert - -scale 10000% png:- | feh -
