from Payer.Language import *;
from Payer.Grammar import *;

__all__ = [
    'terminal_range', 'terminal_sequence'
];

def terminal_range(low, high):
    return terminals(range(ord(low), ord(high) + 1));

def terminal_sequence(seq):
    return reduce(concat, (terminals([ord(x)]) for x in seq));

def _negate(f):
    return f.transform(lambda v: not v);

def grammar():
    grammar = Gramar();

    return grammar;
