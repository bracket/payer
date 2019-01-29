from .nodes import *
import functools

memoize = functools.lru_cache()

def string_to_terminals(string):
    out = null
    terminals = reversed(sorted(set(string)))

    for c in terminals:
        Union(c, out)

    return out

    
def pairwise(seq):
    from itertools import tee
    a, b = tee(iter(seq))
    next(b)

    yield from zip(a, b)
