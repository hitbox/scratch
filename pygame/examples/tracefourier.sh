#!/usr/bin/env sh

N=100
points="100,100 400,100 400,400 100,400"

# NOTE
# - this is *not* drawing a square
# - lack of quotes on points
# - points are taken as separate arguments
python tracefourier.py "${N}" ${points}
