#!/usr/bin/env sh

# listcolors.py provide an augmented Color class with things like saturation

# filter out white, black and shades of grey
# filter for only 100% saturation
# sort by hue and lightness
python \
    listcolors.py \
    --display-size '1800,900' \
    --filter 'len(set(color[:3])) > 1 and color.saturation == 100' \
    --sort 'color.hue, color.lightness'
