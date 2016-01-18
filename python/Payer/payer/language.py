'''The basic terms and term construction functions for constructing language terms in Payer
'''

from . import proto
from .transition_function import *
from .type_tag import TypeTag
from functools import reduce
from matcher import *

__all__ = [
    'null', 'epsilon', 'terminals',
    'output', 'output_node',
    'union', 'concat', 'repeat',
    'optional', 'plus', 'sequence',
    'ref', 'derivative', 'finalize',
    'pretty_lines',
    'all_terminals', 'MAX_TERMINAL',
    'type_tags',
]

MAX_TERMINAL = 255

all_terminals = set(range(0, MAX_TERMINAL + 1))

type_tags = [
    'Null',   'Epsilon',  'Terminals',
    'Union',  'Concat',   'Repeat',
    'Output', 'OutputNode',
    'Ref',    'Derivative', 'Finalize',
]

type_tags = { k : TypeTag(k) for k in type_tags }

globals().update(type_tags)

def null(): return Null()
def epsilon(): return Epsilon()

def terminals(seq):
    'terminals(seq) - take a sequence of terminals and return the term representing the set of those terminals'

    if seq: return Terminals(indicator(seq, MAX_TERMINAL))
    else: return Epsilon()

Sigma = terminals(all_terminals)

@proto.decorate
def union():
    r'''union(L, R) - construct the term representing a union of L and R

        union Null x = x
        union x Null = x
        union (Union x) (Union y) = Union(x | y)
        union x (Union y) = Union(frozenset([x]) | y)
        union (Union x) y = Union(x | frozenset([y]))
        union (Terminals x) (Terminals y) = union_terminals(x, y)
        union x y = x if x == y else Union(frozenset([ x, y ]))
    '''

def union_terminals(x, y):
    f = merge((x, y), xform = lambda p: TransitionPair(p.terminal, any(p.value))).compact()
    return Terminals(f)


@proto.decorate
def concat():
    r'''concat(L, R) - construct the term representing the concatenation of L and R

        concat Null _ = Null()
        concat _ Null = Null()
        concat Epsilon x  = x
        concat x Epsilon = x
        concat (Concat x) (Concat y) = Concat(x + y)
        concat (OutputNode t x) y = output_node(t, concat(x, y))
        concat x (Concat y) = Concat((x,) + y)
        concat (Concat x) y = Concat(x + (y,))
        concat x y = Concat((x , y))
    '''

@proto.decorate
def repeat():
    r'''repeat(L) - construct the term representing any finite repetition of strings in L

        repeat Null = Null()
        repeat Epsilon = Epsilon()
        repeat (Repeat l) = Repeat(l)
        repeat (Output t Epsilon) = Output(t, Epsilon())
        repeat (OutputNode t l) = output_node(t, repeat(l))
        repeat l = Repeat(l)
    '''

@proto.decorate
def output():
    r'''output(t, L) - construct the term representing the output terminal t prepended to the language L

        output t Null = Null()
        output t l    = Output(t, l)
    '''

@proto.decorate
def output_node():
    r'''output_node(t, L) - construct a node representing output terminal t attached to a language L

        output_node t Null = Null()
        output_node t l    = OutputNode(t, l)
    '''

def ref(name): return Ref(name)

@proto.decorate
def derivative():
    r'''derivative(x, L) - construct the term repsenting the derivative of L with respect to x, simplifying if possible

        derivative x Null             = Null()
        derivative x Epsilon          = Null()
        derivative x (Terminals t)    = Epsilon() if t(x) else Null()
        derivative x (Union ls)       = reduce(union, (derivative(x, l) for l in ls))
        derivative x (Concat ls)      = derivative_concat(x, ls)
        derivative x (Repeat l)       = concat(derivative(x, l), Repeat(l))
        derivative x (Output t l)     = output_node(t, derivative(x, l))
        derivative x (OutputNode t l) = output_node(t, derivative(x, l))
        derivative _ (Finalize _)     = Null()
        derivative x l                = Derivative(x, l)
    '''


def concat_reduction(ls):
    last = len(ls) - 1
    for i in range(last):
        head = ls[i]
        yield (head, Concat(ls[i + 1:])) if i < last - 1 else (head, ls[i + 1])
        if finalize(head) == Null(): break

    if finalize(ls[last - 1]) != Null():
        yield (None, ls[last])


def derivative_concat(x, ls):
    return reduce(
        union,
        (
            concat(derivative(x, head), tail) if head is not None else derivative(x, tail)
            for head, tail
            in concat_reduction(ls)
        )
    )


@proto.decorate
def finalize():
    r'''finalize(L) - construct the term representing the finalization of L, simplifying if possible

        finalize Null             = Null()
        finalize Epsilon          = Epsilon()
        finalize (Terminals _)    = Null()
        finalize (Union ls)       = reduce(union, (finalize(l) for l in ls))
        finalize (Concat ls)      = reduce(concat, (finalize(l) for l in ls))
        finalize (Repeat l)       = union(finalize(l), Epsilon())
        finalize (Output t l)     = output_node(t, finalize(l))
        finalize (OutputNode t l) = output_node(t, finalize(l))
        finalize (Finalize l)     = Finalize(l)
        finalize l                = Finalize(l)
    '''

@proto.decorate
def reconstruct():
    r'''
        reconstruct(L) - take a language which may not have been constructed by the language constructors in here and make it obey those constraints

        reconstruct (Union ls)       = reduce(union, ls)
        reconstruct (Concat ls)      = reduce(concat, ls)
        reconstruct (Repeat l)       = repeat(l)
        reconstruct (Output t l)     = output(t, l)
        reconstruct (OutputNode t l) = output_node(t, l)
        reconstruct l                = l
    '''

class PrettyLines(object):
    def __init__(self, term):
        self.lines = [ ]
        self.indent = ''
        self.call_level = 0
        self(term)


    def __call__(self, term):
        self.indent = '    ' * self.call_level
        self.call_level += 1
        self.call(term)
        self.call_level -= 1


    @MatcherMethod.decorate
    def call(add):
        @add(Terminals(var('x')))
        def call(self, x):
            self.lines.append('{}Terminals({})'.format(self.indent, str(x)))


        @add(Union(var('x')))
        def call(self, x):
            self.lines.append('{}Union'.format(self.indent))
            for term in x:
                self(term)


        @add(Concat(var('x')))
        def call(self, x):
            self.lines.append('{}Concat'.format(self.indent))
            for term in x:
                self(term)


        @add(var('x'))
        def call(self, x):
            if isinstance(x, tuple):
                self.lines.append('{}{}'.format(self.indent, str[x[0]]))
                for term in x[1:]:
                    self(term)
            else:
                self.lines.append('{}{}'.format(self.indent, str(x)))


def pretty_lines(term):
    return PrettyLines(term).lines


def optional(L): return union(epsilon(), L)

def plus(L): return concat(L, repeat(L))

def sequence(L, d): return concat(L, repeat(concat(d, L)))

#TODO: Probably need to memoize this
@proto.decorate
def all_derivatives():
    r'''all_derivatives

        all_derivatives Null          = Sigma.transform(lambda v: Null())
        all_derivatives Epsilon       = Sigma.transform(lambda v: Null())
        all_derivatives (Terminals t) = t.transform(lambda v: Epsilon() if v else Null())
        all_derivatives (Union ls)    = merge((all_derivatives(l) for l in ls), lambda p: (p.terminal, reduce(union, p.value))).compact()
        all_derivatives (Concat ls)   = all_derivatives_concat(ls)
        all_derivatives (Repeat l)    = all_derivatives(l).transform(lambda v: concat(v, repeat(l))).compact()
    '''

def all_derivatives_concat(ls):
    ls = [ all_derivatives(head).transform(lambda v: concat(v, tail)) for head, tail in concat_reduction(ls) ]
    return merge(ls, lambda p: (p.terminal, reduce(union, p.value))).compact()
