#!/usr/bin/env sh

minsize=100
maxsize=200
nrandomrects=100
colattr=centerx
rowattr=centery

python randrects.py \
    -n "${nrandomrects}" \
    -0 \
    --minsize "${minsize}" \
    --maxsize "${maxsize}" \
    | \
    xargs -0 python griddemo.py \
        --colattr "${colattr}" \
        --rowattr "${rowattr}"
