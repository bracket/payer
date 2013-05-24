from Matcher import Matcher, var, _, find;
from Payer import TransitionFunction;

__all__ = [
    'null', 'epsilon', 'terminals',
    'output', 'output_node', 'union', 'concat', 'repeat',
    'nullable', 'nullity',
    'derivative', 'finalize',
    'pretty_print', 'get_outputs',
];

MAX_TERMINAL = 255;

def get_outputs(term):
    pattern = (OutputNode, var('node'), _);
    for m, d in find(pattern, term): yield d['node'];

class Token(object):
    def __init__(self, name): self.name = name;
    def __str__(self): return self.name;
    def __repr__(self): return self.name;

tokens = [
    'Null',   'Epsilon', 'Terminals',
    'Union',  'Concat',  'Repeat',
    'Output', 'Ref',
];

globals().update((k, Token(k)) for k in tokens);

class OutputNode(object):
    def __init__(self, value, prev = None):
        self.value = value;
        self.prev = prev;

    def __iter__(self):
        while self is not None:
            yield self.value;
            self = self.prev;

def _unique_tuple(x):
    return tuple(sorted(set(x)));

def null(): return (Null,);

def epsilon(): return (Epsilon,);

def terminals(x):
    if x: return (Terminals, TransitionFunction.indicator(x, MAX_TERMINAL));
    else: return (Epsilon,);

def output(t, L): return (Output, t, L);

@Matcher
def union(add):
    @add((Null,), var('x'))
    def f(x): return x;

    @add(var('x'), (Null,))
    def f(x): return x;

    @add((Union, var('x')), (Union, var('y')))
    def f(x, y): return (Union, _unique_tuple(x + y));

    @add(var('x'), (Union, var('y')))
    def f(x, y): return (Union, _unique_tuple((x,) + y));

    @add((Union, var('x')), var('y'))
    def f(x, y): return (Union, _unique_tuple(x + (y,)));

    @add(var('x'), var('y'))
    def f(x, y): 
        if x < y: return (Union, (x, y));
        elif y < x: return (Union, (y, x));
        else: return x;

@Matcher
def concat(add):
    @add((Null,), _)
    def f(): return null();

    @add(_, (Null,))
    def f(): return null();

    @add((Epsilon,), var('x'))
    def f(x): return x;

    @add(var('x'), (Epsilon,))
    def f(x): return x;

    @add((Concat, var('x')), (Concat, var('y')))
    def f(x, y): return (Concat, x + y);

    @add((OutputNode, var('node'), var('x')), var('y'))
    def f(node, x, y): return output_node(node, concat(x, y));

    @add(var('x'), (Concat, var('y')))
    def f(x, y):
        return (Concat, (x,) + y);

    @add((Concat, var('x')), var('y'))
    def f(x, y): return (Concat, x + (y,));
    
    @add(var('x'), var('y'))
    def f(x, y): return (Concat, (x, y));

@Matcher
def repeat(add):
    @add(OutputNode, var('node'), var('L'))
    def f(node, L): return output_node(node, repeat(L));

    @add(var('L'))
    def f(L): return (Repeat, L);
    
def ref(name): return (Ref, name);

@Matcher
def output_node(add):
    @add(_, (Null,))
    def f(): return null();

    @add(var('prev_node'), (OutputNode, var('next_node'), var('L')))
    def f(prev_node, next_node, L):
        next_node.prev = prev_node;
        return (OutputNode, next_node, L);

    @add(var('node'), var('L'))
    def f(node, L): return (OutputNode, node, L);

@Matcher
def _pretty_print(add):
    @add(var('indent'), (Terminals, var('x')))
    def f(indent, x): print '%sTerminals(%s)' % (indent, str(x));

    @add(var('indent'), (Union, var('x')))
    def f(indent, x):
        print '%sUnion' % indent;
        indent += '    ';
        for t in x: _pretty_print(indent, t);
    
    @add(var('indent'), (Concat, var('x')))
    def f(indent, x):
        print '%sConcat' % indent;
        indent += '    ';
        for t in x: _pretty_print(indent, t);
    
    @add(var('indent'), var('x'))
    def f(indent, x):
        if isinstance(x, tuple):
            print '%s%s' % (indent, str(x[0]));
            if len(x) > 1:
                indent += '    ';
                for y in x[1:]: _pretty_print(indent, y);
        else: print '%s%s' % (indent, str(x))

def pretty_print(term, indent = ''):
    _pretty_print(indent, term);

@Matcher
def nullable(add):
    @add((Epsilon,))
    def f(): return True;

    @add((Repeat, _))
    def f(): return True;

    @add((Output, _, var('L')))
    def f(L): return nullable(L);

    @add((Union, var('xs')))
    def f(xs): return any(nullable(x) for x in xs);

    @add((Concat, var('xs')))
    def f(xs): return all(nullable(x) for x in xs);

    @add((OutputNode, _, var('L')))
    def f(L): return nullable(L);

    @add(_)
    def f(): return False;

def nullity(L): return epsilon() if nullable(L) else null();

def _sublists(l):
    n = len(l);
    for i in xrange(n):
        yield l[i], l[i+1:n];

def _subconcats(l):
    for h, t in _sublists(l):
        n = len(t);
        if n > 1: yield h, (Concat, t);
        elif n == 1: yield h, t[0];
        else: yield h, epsilon();

@Matcher
def derivative(add):
    @add(_, (Null,))
    def f(): return null();

    @add(_, (Epsilon,))
    def f(): return null();

    @add(var('c'), (Terminals, var('f')))
    def f(c, f):
        if f(c): return epsilon();
        else: return null();

    @add(var('c'), (Union, var('x')))
    def f(c, x):
        return (reduce(union, (derivative(c, t) for t in x)));

    @add(var('c'), (Concat, var('x')))
    def f(c, x):
        L = null();
        for h, t in _subconcats(x):
            L = union(L, concat(derivative(c, h), t))
            if not nullable(h): break;
        return L;
    
    @add(var('c'), (Repeat, var('x')))
    def f(c, x): return concat(derivative(c, x), repeat(x));

    @add(var('c'), (Output, var('t'), var('L')))
    def f(c, t, L): return output_node(OutputNode(t), derivative(c, L));

    @add(var('c'), (OutputNode, var('node'), var('L')))
    def f(c, node, L): return output_node(node, derivative(c, L));

@Matcher
def finalize(add):
    @add((Null,))
    def f(): return null();

    @add((Epsilon,))
    def f(): return epsilon();

    @add((Terminals, _))
    def f(): return null();

    @add((Union, var('Ls')))
    def f(Ls): return reduce(union, (finalize(L) for L in Ls));

    @add((Concat, var('Ls')))
    def f(Ls): 
        out = null();
        for L in Ls:
            if not nullable(L): break;
            out = union(out, finalize(L));
        return out;
    
    @add((Repeat, var('L')))
    def f(L): return finalize(L);

    @add((Output, var('t'), var('L')))
    def f(t, L): return output_node(OutputNode(t), finalize(L));

    @add((OutputNode, var('node'), var('L')))
    def f(node, L): return output_node(node, finalize(L));
