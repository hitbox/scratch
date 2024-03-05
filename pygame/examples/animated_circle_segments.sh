#!/usr/bin/env sh

# inner,outer radii
radii=100,200

# start,stop degrees
segment_range_start=5,270
segment_range_stop=270,270

python demo.py circle_segments "${radii}" "${segment_range_start}" \
    --animate segment_range "${segment_range_start}" "${segment_range_stop}" 500 2000
