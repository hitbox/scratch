#!/usr/bin/env sh

# defaults
minsize=1
maxsize=100
n=100
colattr=centerx
rowattr=centery

while [[ $# -gt 0 ]]; do
    case $1 in
        --minsize)
            minsize=$2
            shift
            shift
            ;;
        --maxsize)
            maxsize=$2
            shift
            shift
            ;;
        -n)
            n=$2
            shift
            shift
            ;;
        --colattr)
            colattr=$2
            shift
            shift
            ;;
        --rowattr)
            rowattr=$2
            shift
            shift
            ;;
    esac
done

# 1. generate random rects as x y w h separated by null
# 2. xargs pipe those as arguments to the grid demo

python randomshapes.py rect -n "${n}" -0 | \
    xargs -0 python demo.py grid \
        --colattr "${colattr}" \
        --rowattr "${rowattr}"
