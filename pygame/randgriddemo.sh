#!/usr/bin/env sh

nrandomrects=100
colattr=centerx
rowattr=centery

python randrects.py -n "${nrandomrects}" -0 \
    | xargs -0 python griddemo.py \
        --colattr "${colattr}" \
        --rowattr "${rowattr}"
