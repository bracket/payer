'''The basic terms and term construction functions for constructing language terms in Payer
'''

import Proto;
from Matcher import *;
from TypeTag import TypeTag;
from Payer.TransitionFunction import *;

__all__ = [
    'null', 'epsilon', 'terminals',
    'output',
    'union', 'concat', 'repeat',
    'optional', 'plus',
    'ref', 'derivative', 'finalize', # 'split_concat',
    'pretty_print',
    'all_terminals', 'MAX_TERMINAL',
    'type_tags',
];

MAX_TERMINAL = 255;

all_terminals = set(range(0, MAX_TERMINAL + 1));

type_tags = [
    'Null',       'Epsilon',  'Terminals',
    'Union',      'Concat',   'Repeat',
    'Output',     'Ref',
    'Derivative', 'Finalize',
];

type_tags = { k : TypeTag(k) for k in type_tags };

globals().update(type_tags);

def null(): return Null();
def epsilon(): return Epsilon();

def terminals(x):
    if x: return Terminals(indicator(x, MAX_TERMINAL));
    else: return Epsilon();

@Proto.decorate
def union(add):
    r'''construct the term representing a union of two languages

        union Null x = x;
        union x Null = x;
        union (Union x) (Union y) = Union(x | y);
        union x (Union y) = Union(frozenset([x]) | y);
        union (Union x) y = Union(x | frozenset([y]));
        union (Terminals x) (Terminals y) = union_terminals(x, y);
        union x y = Union(frozenset([ x, y ]));
    '''

def union_terminals(x, y):
    f = merge((x, y), xform = lambda p: TransitionPair(p.terminal, any(p.value))).compact();
    return Terminals(f);

@Proto.decorate
def concat(add):
    r'''construct the term representing the concatenation of two languages

        concat Null _ = Null();
        concat _ Null = Null();
        concat Epsilon x  = x;
        concat x Epsilon = x;
        concat (Concat x) (Concat y) = Concat(x + y);
        concat x (Concat y) = Concat((x,) + y);
        concat (Concat x) y = Concat(x + (y,));
        concat x y = Concat((x , y));
    '''

@Proto.decorate
def repeat(L):
    r'''construct the term representing any finite repetition of strings in a given language
    
        repeat Null = Null();
        repeat Epsilon = Epsilon();
        repeat (Repeat l) = Repeat(l);
        repeat l = Repeat(l);
    '''
    # repeat (Output t Epsilon) = Ouput(t, Epsilon());

def output(t, L): return (Output, t, L);

def ref(name): return Ref(name);

@Proto.decorate
def derivative():
    r'''Derivative
        
        derivative x Null          = Null();
        derivative x Epsilon       = Null();
        derivative x (Terminals t) = Epsilon() if t(x) else Null();
        derivative x (Union ls)    = reduce(union, (derivative(x, l) for l in ls));
        derivative x (Concat ls)   = derivative_concat(x, ls);
        derivative x (Repeat l)    = concat(derivative(x, l), Repeat(l));
        derivative x l             = Derivative(x, l);
    '''
    # derivative x (Output t l)  = derivative(x, l);
    # derivative _ (Finalize _)  = Null() # This seems wrong.  You could lose output when trying to simplify this around references.

def derivative_concat(x, ls):
    head, tail = (ls[0], ls[1]) if len(ls) == 2 else (ls[0], Concat(ls[1:]));
    return union(
        concat(derivative(x, head), tail),
        concat(finalize(head), derivative(x, tail))
    );

@Proto.decorate
def finalize():
    r'''Finalize

        finalize Null          = Null();
        finalize Epsilon       = Epsilon();
        finalize (Terminals _) = Null();
        finalize (Union ls)    = reduce(union, (finalize(l) for l in ls));
        finalize (Concat ls)   = reduce(concat, (finalize(l) for l in ls));
        finalize (Repeat l)    = union(finalize(l), Epsilon());
        finalize l             = Finalize(l);
    '''
    # finalize (Output _ l)  = nullity(l);

@Matcher.decorate
def _pretty_print(add):
    @add(var('indent'), Terminals(var('x')))
    def _pp(indent, x): print '%sTerminals(%s)' % (indent, str(x));

    @add(var('indent'), Union(var('x')))
    def _pp(indent, x):
        print '%sUnion' % indent;
        indent += '    ';
        for t in x: _pretty_print(indent, t);

    @add(var('indent'), Concat(var('x')))
    def _pp(indent, x):
        print '%sConcat' % indent;
        indent += '    ';
        for t in x: _pretty_print(indent, t);

    @add(var('indent'), var('x'))
    def _pp(indent, x):
        if isinstance(x, tuple):
            print '%s%s' % (indent, str(x[0]));
            if len(x) > 1:
                indent += '    ';
                for y in x[1:]: _pretty_print(indent, y);
        else: print '%s%s' % (indent, str(x))

def pretty_print(term, indent = ''):
    _pretty_print(indent, term);

def optional(L): return union(epsilon(), L);

def plus(L): return concat(L, repeat(L));
