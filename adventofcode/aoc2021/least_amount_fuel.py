import math

# iterations of least_amount_fuel funcs trying to speed up

def least_amount_fuel(horzpos, costfunc):
    least = None
    for p1 in range(min(horzpos), max(horzpos)):
        n = sum(costfunc(p1, p2) for p2 in horzpos)
        if least is None or n < least:
            least = n
    return least
    # NOTE:
    # this took a long time, over a minute, for part 2:
    # $ time python adventofcode.py day07 2
    # Day 7 Part 2 Solution: 97038163
    #
    # real	1m1.283s
    # user	1m1.231s
    # sys	0m0.004s

def least_amount_fuel(horzpos, costfunc):
    least = math.inf
    horzpos = sorted(horzpos)
    for p1 in range(min(horzpos), max(horzpos)):
        n = 0
        for p2 in horzpos:
            n += costfunc(p1, p2)
            if n > least:
                # already over no need to check further. go to next p1
                break
        else:
            # didn't break, might be new least
            if n < least:
                least = n
    return least
    # NOTE:
    # this cut the time in half:
    # $ time python adventofcode.py day07 2
    # Day 7 Part 2 Solution: 97038163
    #
    # real	0m21.310s
    # user	0m21.220s
    # sys	0m0.014s
    # NOTE:
    # lru_cache on increasing_move_cost shaved 5 seconds
    # $ time python adventofcode.py day07 2
    # Day 7 Part 2 Solution: 97038163
    #
    # real	0m15.158s
    # user	0m15.113s
    # sys	0m0.030s
    # NOTE:
    # sorting horzpos first shaved off a little, about 4 seconds
    # $ time python adventofcode.py day07 2
    # Day 7 Part 2 Solution: 97038163
    #
    # real	0m11.052s
    # user	0m11.015s
    # sys	0m0.027s
