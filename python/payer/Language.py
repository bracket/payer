import ADT, Action, TriBool, Memo;
from ADT import var, _;
from TriBool import and_, or_, True_, False_, Maybe_;
from itertools import product;
from Action import ActionGenerator, ActionList;
from TerminalSet import TerminalSet;

memo = Memo.SharedMemo();

class Language(ADT.Type): pass;

@memo
@Language
def Null(): return ();

@memo
@Language
def Epsilon(): return ();

@memo
@Language
def Div(): return ();

@memo
@Language
def TerminalSequence(): return ([TerminalSet],);

@memo
@Language
def Union(): return (frozenset(),)

@memo
@Language
def Concat(): return (Language, Language);

@memo
@Language
def Repeat(): return (Language,);

@memo
@Language
def SemanticAction(): return (Action, Language);

@memo
@Language
def Ref(): return (str,);

@memo
@Language
def Derivative(): return (str, Language);

def null(): return Null();

def epsilon(): return Epsilon();

def div(): return Div();

def terminal_sequence(x):
	if x: return TerminalSequence(x);
	else: return Epsilon();

@ADT.Matcher
def union(add):
	@add(Null(), var('x'))
	def f(x): return x;

	@add(var('x'), Null())
	def f(x): return x;

	@add(Union(var('x')), Union(var('y')))
	def f(x, y): return Union(x | y);

	@add(var('x'), Union(var('y')))
	def f(x, y): return Union(frozenset(x) | y);

	@add(Union(var('x')), var('y'))
	def f(x, y): return Union(x | frozenset(y));

	@add(var('x'), var('y'))
	def f(x, y): return Union(frozenset((x, y)));

@ADT.Matcher
def concat(add):
	@add(Null(), var('x'))
	def f(): return null();

	@add(var('x'), Null())
	def f(): return null();

	@add(Epsilon(), var('x'))
	def f(x): return x;

	@add(var('x'), Epsilon())
	def f(x): return x;

	@add(Div(), Div())
	def f(): return Div();

	@add(TerminalSequence(var('x')), TerminalSequence(var('y')))
	def f(x, y): return terminal_sequence(x + y);

	@add(SemanticAction(var('g'), var('M')), var('N'))
	def f(g, M, N): return semantic_action(g, concat(M, N))

	@add(var('x'), var('y'))
	def f(x, y): return Concat(x, y);

def repeat(L): return Repeat(L);

@ADT.Matcher
def semantic_action(add):
	@add(_, Null())
	def f(): return null();

	@add(var('g'), var('L'))
	def f(g, L): return SemanticAction(g, L);

def ref(name): return Ref(name);

@ADT.Matcher
def _pretty_print(add):
	@add(var('indent'), TerminalSequence(var('x')))
	def f(indent, x): print '%sTerminalSequence(%s)' % (indent, ', '.join(map(str, x)));

	@add(var('indent'), Union(var('x')))
	def f(indent, x):
		print '%sUnion' % indent;
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
	
class LanguageSpace(object):
	def __init__(self, namespace = None, nullspace = None):
		if namespace: self.namespace = namespace;
		else: self.namespace = { };

		if nullspace: self.nullspace = nullspace;
		else: self.nullspace = { };

	def __getitem__(self, key):
		if isinstance(key, str): key = ref(key);
		return self.namespace[key];
	
	def __setitem__(self, key, value):
		if isinstance(key, str): key = ref(key);
		out = self.namespace[key] = value;
		return out;

	def nullable(self, L):
		ping = set(); pong = set();
		out = self.nullable_(ping, L);

		while out is Maybe_() and ping != pong:
			pong.clear();
			out = self.nullable_(pong, L);
			(ping, pong) = (pong, ping);

		if out is Maybe_(): out = False_();
		else:
			for k in ping:
				if self.nullspace.get(k, Maybe_()) is Maybe_():
					self.nullspace[k] = False_();

		return TriBool.to_bool(out);

	@ADT.Matcher
	def nullable_(add):
		@add(_, _, Null())
		def f(): return False_();

		@add(_, _, Epsilon())
		def f(): return True_();

		@add(_, _, Div())
		def f(): return True_();

		@add(_, _, TerminalSequence(_))
		def f(): return False_();

		@add(var('self'), var('traversed'), Union(var('x')))
		def f(self, traversed, x):
			return reduce(or_, (self.nullable_(traversed, t) for t in x));

		@add(var('self'), var('traversed'), Concat(var('x'), var('y')))
		def f(self, traversed, x, y):
			return and_(self.nullable_(traversed, x), self.nullable_(traversed, y));

		@add(_, _, Repeat(_))
		def f(): return True_();

		@add(var('self'), var('traversed'), SemanticAction(_, var('L')))
		def f(self, L): return self.nullable_(traversed, L);

		@add(var('self'), var('traversed'), Ref(var('name')))
		def f(self, traversed, name):
			l = Ref(name);
			r = self.nullspace.get(l, Maybe_());

			if r is not Maybe_(): return r;
			if l in traversed: return Maybe_();
			
			traversed.add(l);
			r = self.nullspace[l] = self.nullable_(traversed, self.namespace[l]);
			return r;
		
		@add(var('self'), var('traversed'), Derivative(var('s'), var('L')))
		def f(self, traversed, s, L):
			l = Derivative(s, L);
			r = self.nullspace.get(l, Maybe_());

			if r is not Maybe_(): return r;
			if l in traversed: return Maybe_();

			traversed.add(l);
			r = self.nullspace[l] = self.nullable_(traversed, self.namespace[l]);
			return r;

	@ADT.Matcher
	def derivative(add):
		@add(_, _, Null())
		def f(): return null();

		@add(_, _, Epsilon())
		def f(): return null();

		@add(_, _, Div())
		def f(): return null();

		@add(_, var('c'), TerminalSequence(var('x')))
		def f(c, x):
			return terminal_sequence(x[1:]) if c in x[0] else null();

		@add(var('self'), var('c'), Union(var('x')))
		def f(self, c, x):
			return reduce(union, (self.delayed_derivative(c, t) for t in x));

		@add(var('self'), var('c'), Concat(var('x'), var('y')))
		def f(self, c, x, y):
			if self.nullable(x): return union(concat(self.derivative(c, x), y), self.derivative(c, y));
			else: return concat(self.derivative(c, x), y);
		
		@add(var('self'), var('c'), Repeat(var('x')))
		def f(self, c, x): return concat(self.derivative(c, x), repeat(x));

		@add(var('self'), var('c'), SemanticAction(var('x'), var('L')))
		def f(self, c, x, L): dispatch_action(x); return self.derivative(c, L);

		@add(var('self'), var('c'), Ref(var('name')))
		def f(self, c, name):
			l = Ref(name);
			d = Derivative(c, Ref(name));
			r = self.namespace.get(d, None);
			if r is not None: return r;

			self.namespace[d] = d;
			r = self.namespace[d] = self.derivative(c, self.namespace[l]);
			return r;

		@add(var('self'), var('c'), Derivative(var('s'), var('L')))
		def f(self, c, s, L):
			l = Derivative(s, L);
			d = Derivative(s + c, L);
			r = self.namespace.get(d, None);
			if r is not None: return r;

			self.namespace[d] = d;
			r = self.namespace[d] = self.derivative(c, self.namespace[l]);
			return r;

	@ADT.Matcher
	def delayed_derivative(add):
		@add(var('self'), var('c'), SemanticAction(var('x'), SemanticAction(var('y'), var('L'))))
		def f(self, c, x, y, L): return self.delayed_derivative(c, SemanticAction(Action.combine_delay(x, y), L));

		@add(var('self'), var('c'), SemanticAction(var('x'), var('L')))
		def f(self, c, x, L): return semantic_action(Action.delay_action(x), self.delayed_derivative(c, L));

		@add(var('self'), var('c'), Union(var('x')))
		def f(self, c, x):
			return reduce(union, (self.delayed_derivative(c, t) for t in x));

		@add(var('self'), var('c'), Concat(var('x'), var('y')))
		def f(self, c, x, y):
			if self.nullable(x): return union(concat(self.delayed_derivative(c, x), y), self.delayed_derivative(c, y));
			else: return concat(self.delayed_derivative(c, x), y);
		
		@add(var('self'), var('c'), Repeat(var('x')))
		def f(self, c, x): return concat(self.delayed_derivative(c, x), repeat(x));

		@add(var('self'), var('c'), var('L'))
		def f(self, c, L): return self.derivative(c, L);

@ADT.Matcher
def dispatch_outer(add):
	@add(SemanticAction(ActionList(var('t')), var('L')))
	def f(t, L):
		for x in t: x();
		return dispatch_outer(L);
	
	@add(var('L'))
	def f(L): return L;

@ADT.Matcher
def dispatch_to_div(add):
	@add(SemanticAction(var('g'), Concat(Div(), var('L'))))
	def f(g, L): dispatch_action(g); return L;

	@add(var('L'))
	def f(L): return L;

@ADT.Matcher
def derivative_set(add):
	@add(var('s'), Null())
	def f(s): return [(s, null())]

	@add(var('s'), Epsilon())
	def f(s): return [(s, null())];

	@add(var('s'), TerminalSequence(var('x')))
	def f(s, x):
		return [
				(t, terminal_sequence(x[1:])),
				(s.subtract(x[0]), null())
			];

	@add(var('s'), Union(var('x')))
	def f(s, x, y):
		out = [];

		for (ls, l), (rs, r) in product(derivative_set(s, x), derivative_set(s, y)):
			t = ls & rs;
			if t.empty(): continue;
			out.append((t, union(l, r)));
		return out;
	
	@add(var('s'), Concat(var('x'), var('y')))
	def f(s, x, y):
		out = [];
		if nullable(x):
			for (ls, l), (rs, r) in product(derivative_set(s, x), derivative_set(s, y)):
				t = ls & rs;
				if t.empty(): continue;
				out.append((t, union(concat(l, y), r)));
		else:
			for (t, l) in derivative_set(s, x):
				out.append((t, concat(l, y)));
		return out;
	
	@add(var('s'), Repeat(var('x')))
	def f(s, x):
		return [(t, concat(l, repeat(x))) for t,l in derivative_set(s, x)];
