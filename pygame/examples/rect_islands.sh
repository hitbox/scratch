#!/usr/bin/env sh
python randomshapes.py rects-from-ranges \
    --xrange 0,750 --yrange 0,750 --wrange 20,50 --hrange 20,50 -n 300 \
    | python islands.py - rect
