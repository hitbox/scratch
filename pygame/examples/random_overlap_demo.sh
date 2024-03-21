#!/usr/bin/env sh

xrange="0,700"
yrange="0,700"
wrange="25,100"
hrange="25,100"
seed="0"

python randomshapes.py rect \
    -0 \
    --xrange "${xrange}" \
    --yrange "${yrange}" \
    --wrange "${wrange}" \
    --hrange "${hrange}" \
    --seed "${seed}" \
    -n 25 \
    | \
    xargs -0 python demo.py overlap_demo --seed "${seed}"
