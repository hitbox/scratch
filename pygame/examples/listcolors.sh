#!/usr/bin/env sh

# filter out white, black and shades of grey
# filter for only 100% saturation
# sort by hue and lightness
python \
    listcolors.py \
    --display-size '1800,900' \
    --filter 'len(set(color[:3])) > 1 and color.hsla[1] == 100' \
    --sort 'color.hsla[0], color.hsla[2]'
