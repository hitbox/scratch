#!/usr/bin/env sh

rects='R(0,0,1,1),R(2,1,1,1),R(3,5,1,1),R(5,3,1,1),R(2,2,1,1)'

echo wrap with python
python -m timeit \
    -s 'import rectop; from pygame import Rect as R' \
    -- "rectop.get.wrap_python([${rects}])"

echo wrap with pygame
python -m timeit \
    -s 'import rectop; from pygame import Rect as R' \
    -- "rectop.get.wrap_pygame([${rects}])"

# ./timeit_wrap.sh
# wrap with python
# 200000 loops, best of 5: 1.86 usec per loop
# wrap with pygame
# 500000 loops, best of 5: 614 nsec per loop

# I think I have these units right.
# 1 micro = 1000 nano, so 1.86 micro 1860 nano
# >>> 1.86/1860
# 0.001
# >>> 100*(1.86/1860)
# 0.1
# So pygame takes about point one percent of the time as python.
