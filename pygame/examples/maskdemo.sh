#!/usr/bin/env sh

# TODO
# - better shorthand or at least docs.
# - help shows as keyword args but they are positional and passed to a
#   namedtuple with defaults.

# path/to/image.ext <width> <height> <scale>
spritesheet_shorthand="assets/images/greenblob.18x-1.less.png 18 -1 18"

# <border width> <color>
outline_style="8 orange"

python maskdemo.py "${spritesheet_shorthand}" \
    --animation-delay=150 \
    --outline-style="${outline_style}" \
    --flash-delay=500
