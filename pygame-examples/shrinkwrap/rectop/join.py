from itertools import combinations
from itertools import tee

from . import get
from . import query

def defrag(rects):
    """
    """
    def area(item):
        r1, r2, wrapped = item
        return wrapped.width * wrapped.height

    result = {
        'append': [],
        'remove': [],
    }
    append_ops = result['append']
    remove_ops = result['remove']
    while True:
        # generate rects as-if the operations have been applied
        with_ops = (rect for rect in rects + append_ops if rect not in remove_ops)
        # generate 2-tuples of rects that can be joined
        joinables = (
            (r1, r2) for r1, r2 in combinations(with_ops, 2) if query.is_joinable(r1, r2)
        )
        # duplicate generator to efficiently test and, if it has joinables,
        # join them
        has_join, joinables = tee(joinables)
        if not any(has_join):
            # nothing to join, done
            break
        # generate 3-tuples of rects and a wrapping rect
        joined = ((r1, r2, get.wrap((r1, r2))) for r1, r2 in joinables)
        # find the largest wrap and the rects that can be removed
        r1, r2, largest_join = sorted(joined, key=area)[-1]
        # replace rects with their wrapping rect
        append_ops.append(largest_join)
        remove_ops.extend([r1, r2])
    return result

def apply(defrag_result, rects):
    """
    Apply the result of defrag.
    """
    for newrect in defrag_result['append']:
        rects.append(newrect)
    for redundant in defrag_result['remove']:
        rects.remove(redundant)

def defrag_ip(rects):
    ops = defrag(rects)
    apply(ops, rects)
