#!/usr/bin/env sh

# demonstrates:
# - drawing a circle segment, like the parts of a health meter
# - a crude animation language for command line
# - crude adaptive angle step base on radius

# motivation:
# - see the adaptive step in action
# - verify drawing segments
# - animation
# - after fiddling with stuff in pygamelib meter_bar_circular no longer worked,
#   so this is helping break things down

# inner_radius outer_radius segment_offset
# center to midleft because we're going to animate
# animate inner_radius from 0 to 700 from time 500 to 10,000
# animate outer_radius from 10 to 800 from time 500 to 10,000

time_start=1000
time_end=6_000

inner_start=0
inner_end=800

outer_start=10
outer_end=810

segment_offset_start=5
segment_offset_end=30

# little animation language is five positional arguments to the --animate option
# 1. name of variable
# 2. start value
# 3. end value
# 4. start time
# 5. end time

python demo.py \
    circle_segments \
    $inner_start $outer_start $segment_offset_start \
    --center window.midleft \
    --animate inner_radius $inner_start $inner_end $time_start $time_end \
    --animate outer_radius $outer_start $outer_end $time_start $time_end \
    --animate segment_offset $segment_offset_start $segment_offset_end $time_start $time_end
