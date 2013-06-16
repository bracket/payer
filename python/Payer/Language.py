from Matcher import *;
from Payer.TransitionFunction import *;

__all__ = [
    'null', 'epsilon', 'terminals',
    'output', 'output_node', 'union', 'concat', 'repeat',
    'optional', 'plus',
    'ref',
    'nullable', 'nullity',
    'OutputNode', 'LanguageSpace',
    'pretty_print', 'get_outputs',
    'all_terminals', 'MAX_TERMINAL',
];

MAX_TERMINAL = 255;

all_terminals = set(range(0, MAX_TERMINAL + 1));

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
    if x: return (Terminals, indicator(x, MAX_TERMINAL));
    else: return (Epsilon,);

def output(t, L): return (Output, t, L);

@Matcher
def output_node(add):
    @add(_, (Null,))
    def _output_node(): return null();

    @add(var('prev_node'), (OutputNode, var('next_node'), var('L')))
    def _output_node(prev_node, next_node, L):
        next_node.prev = prev_node;
        return (OutputNode, next_node, L);

    @add(var('node'), var('L'))
    def _output_node(node, L): return (OutputNode, node, L);

@Matcher
def union(add):
    @add((Null,), var('x'))
    def _union(x): return x;

    @add(var('x'), (Null,))
    def _union(x): return x;

    @add((Union, var('x')), (Union, var('y')))
    def _union(x, y): return (Union, _unique_tuple(x + y));

    @add(var('x'), (Union, var('y')))
    def _union(x, y): return (Union, _unique_tuple((x,) + y));

    @add((Union, var('x')), var('y'))
    def _union(x, y): return (Union, _unique_tuple(x + (y,)));

    @add((Terminals, var('x')), (Terminals, var('y')))
    def _union(x, y):
        f = merge((x, y), xform = lambda p: TransitionPair(p.terminal, any(p.value))).compact();
        return (Terminals, f);

    @add(var('x'), var('y'))
    def _union(x, y):
        if x < y: return (Union, (x, y));
        elif y < x: return (Union, (y, x));
        else: return x;

@Matcher
def concat(add):
    @add((Null,), _)
    def _concat(): return null();

    @add(_, (Null,))
    def _concat(): return null();

    @add((Epsilon,), var('x'))
    def _concat(x): return x;

    @add(var('x'), (Epsilon,))
    def _concat(x): return x;

    @add((Concat, var('x')), (Concat, var('y')))
    def _concat(x, y): return (Concat, x + y);

    @add((OutputNode, var('node'), var('x')), var('y'))
    def _concat(node, x, y): return output_node(node, concat(x, y));

    @add(var('x'), (Concat, var('y')))
    def _concat(x, y): return (Concat, (x,) + y);

    @add((Concat, var('x')), var('y'))
    def _concat(x, y): return (Concat, x + (y,));

    @add(var('x'), var('y'))
    def _concat(x, y): return (Concat, (x, y));

@Matcher
def repeat(add):
    @add(OutputNode, var('node'), var('L'))
    def _repeat(node, L): return output_node(node, repeat(L));

    @add(var('L'))
    def _repeat(L): return (Repeat, L);

def ref(name): return (Ref, name);

@Matcher
def _pretty_print(add):
    @add(var('indent'), (Terminals, var('x')))
    def _pp(indent, x): print '%sTerminals(%s)' % (indent, str(x));

    @add(var('indent'), (Union, var('x')))
    def _pp(indent, x):
        print '%sUnion' % indent;
        indent += '    ';
        for t in x: _pretty_print(indent, t);

    @add(var('indent'), (Concat, var('x')))
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

@Matcher
def nullity(add):
    @add((Null,))
    def _nullity(): return null();

    @add((Epsilon,))
    def _nullity(): return epsilon();

    @add((Terminals, _))
    def _nullity(): return null();

    @add((Union, var('Ls')))
    def _nullity(Ls):
        return reduce(union, (nullity(L) for L in  Ls));

    @add((Concat, var('Ls')))
    def _nullity(Ls):
        return reduce(concat, (nullity(L) for L in Ls));

    @add((Repeat, _))
    def _nullity(): return epsilon();

    @add((Ref, var('name')))
    def _nullity(name): return ref(name);

    @add((Output, _, var('L')))
    def _nullity(L): return nullity(L);

    @add((OutputNode, _, var('L')))
    def _nullity(L): return nullity(L);

def nullable(L): return nullity(L) == epsilon();

def optional(L): return union(epsilon(), L);

def plus(L): return concat(L, repeat(L));

def get_outputs(term):
    pattern = (OutputNode, var('node'), _);
    for m, d in find(pattern, term): yield d['node'];

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

def _default_output_derivative(space, terminal, output, language):
    return output_node(OutputNode(output), space.derivative(terminal, language));

def _default_output_finalize(space, output, language):
    return output_node(OutputNode(output), space.finalize(language));

class LanguageSpace(object):
    def __init__(self, handle_derivative = None, handle_finalize = None):
        self._handle_derivative = handle_derivative if handle_derivative else _default_output_derivative;
        self._handle_finalize = handle_finalize if handle_finalize else _default_output_finalize;

        self._languages = { };
        self._nullity_cache = None;
    
    @MatcherMethod
    def __getitem__(add):
        @add((Ref, var('key')))
        def _getitem(self, key): return self._languages[(Ref, key)];

        @add(var('key'))
        def _getitem(self, key): return self._languages[(Ref, key)];

    @MatcherMethod
    def __setitem__(add):
        @add((Ref, var('key')), var('value'))
        def _setitem(self, key, value): self._languages[(Ref, key)] = value;

        @add(var('key'), var('value'))
        def _setitem(self, key, value): self._languages[(Ref, key)] = value;

    @MatcherMethod
    def derivative(add):
        @add(_, (Null,))
        def _derivative(self): return null();

        @add(_, (Epsilon,))
        def _derivative(self): return null();

        @add(var('c'), (Terminals, var('f')))
        def _derivative(self, c, f):
            if f(c): return epsilon();
            else: return null();

        @add(var('c'), (Union, var('x')))
        def _derivative(self, c, x):
            return (reduce(union, (self.derivative(c, t) for t in x)));

        @add(var('c'), (Concat, var('x')))
        def _derivative(self, c, x):
            L = null();
            for h, t in _subconcats(x):
                L = union(L, concat(self.derivative(c, h), t))
                if not nullable(h): break;
            return L;

        @add(var('c'), (Repeat, var('x')))
        def _derivative(self, c, x): return concat(self.derivative(c, x), repeat(x));

        @add(var('c'), (Output, var('t'), var('L')))
        def _derivative(self, c, t, L): return self._handle_derivative(self, c, t, L);

        @add(var('c'), (OutputNode, var('node'), var('L')))
        def _derivative(self, c, node, L): return output_node(node, self.derivative(c, L));

    @MatcherMethod
    def finalize(add):
        @add((Null,))
        def _finalize(self): return null();

        @add((Epsilon,))
        def _finalize(self): return epsilon();

        @add((Terminals, _))
        def _finalize(self): return null();

        @add((Union, var('Ls')))
        def _finalize(self, Ls): return reduce(union, (self.finalize(L) for L in Ls));

        @add((Concat, var('Ls')))
        def _finalize(self, Ls):
            out = null();
            for L in Ls:
                if not nullable(L): break;
                out = union(out, self.finalize(L));
            return out;

        @add((Repeat, var('L')))
        def _finalize(self, L): return union(epsilon(), self.finalize(L));

        @add((Output, var('t'), var('L')))
        def _finalize(self, t, L): return self._handle_finalize(self, OutputNode(t), self.finalize(L));

        @add((OutputNode, var('node'), var('L')))
        def _finalize(self, node, L): return output_node(node, self.finalize(L));

    @MatcherMethod
    def expand_nullity_ref(add):
        @add((Ref, var('name')))
        def _expand_nullity_ref(self, name): return self._nullity_cache[(Ref, name)];

        @add(var('L'))
        def _expand_nullity_ref(self, L): return L;

    def generate_nullity_cache(self):
        done = (null(), epsilon());
        self._nullity_cache = { k : nullity(L) for k, L in self._languages.iteritems() };
        changed = True;

        while changed:
            changed = False;
            for k, L in self._nullity_cache.iteritems():
                if L in done: continue;
                M = self._nullity_cache[k] = bottom_up(self.expand_nullity_ref, L);
                changed = changed or (M != L);

        for k, L in self._nullity_cache.iteritems():
            if L not in done: self._nullity_cache[k] = null();
