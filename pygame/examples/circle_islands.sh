#!/usr/bin/env sh
python randomshapes.py circles-from-ranges \
    --xrange 0,750 --yrange 0,750 --radiusrange 2,50 -n 100 \
    | python islands.py - circle
