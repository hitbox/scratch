#!/usr/bin/env sh

# TODO
# - something like svg <animate> just minus all the svg stuff

python animate.py \
    --shape 'rect rect1 red 100,200 100,150' \
    --shape 'rect rect2 green 300,200 100,150' \
    --shape 'circle circle1 orange 200,200 50' \
    --animate 'circle1 center 200,200 400,500 500 2500' \
    --animate 'circle1 radius 50 100 500 2500' \
    --animate 'circle1 color orange purple 500 2500' \
    --animate 'rect2 size 100,150 200,300 1000 1500' \
    --animate 'circle1 center 400,500 600,200 2500 4500' \
    --animate 'circle1 radius 100 50 2500 4500' \
    --animate 'circle1 color purple greenyellow 2500 4500'
