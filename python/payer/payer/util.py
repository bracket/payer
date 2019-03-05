from . import nodes
import functools

__all__ = [
    'list_to_concat',
    'string_to_concat',
    'string_to_terminals',
]

memoize = functools.lru_cache()

def string_to_terminals(string):
    out = null
    terminals = reversed(sorted(set(string)))

    for c in terminals:
        out = nodes.Union(c, out)

    return out

def list_to_concat(seq):
    out = epsilon

    for l in reversed(list(iter(seq))):
        out = nodes.Concat(l, out)

    return out

def string_to_concat(string):
    return list_to_concat(string)


def list_to_union(seq):
    out = null

    for i in iter(seq):
        out = nodes.Union(i, out)

    return out
    
def pairwise(seq):
    from itertools import tee
    a, b = tee(iter(seq))
    next(b)

    yield from zip(a, b)
