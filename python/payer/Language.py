# # from ADT import Type, ADT.Matcher, var, _;
# # from TerminalSet import TerminalSet;
# # from TriBool import *;

import ADT, TerminalSet, Action, TriBool, Memo;
from ADT import var, _;
from TriBool import and_, or_, True_, False_, Maybe_;
from itertools import product;
from Action import ActionGenerator, ActionList;

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
def Literal(): return (str,);

@memo
@Language
def Union(): return (Language, Language);

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

def literal(x):
	if x: return Literal(x);
	else: return Epsilon();

@ADT.Matcher
def union(add):
	@add(Null(), var('x'))
	def f(x): return x;

	@add(var('x'), Null())
	def f(x): return x;

	@add(var('x'), var('y'))
	def f(x, y): return Union(x, y);

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

	@add(Literal(var('x')), Literal(var('y')))
	def f(x, y): return literal(x + y);

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

class LanguageSpace(object):
	def __init__(self, namespace = None, nullspace = None):
		if namespace: self.namespace = namespace;
		else: self.namespace = { };

		if nullspace: self.nullspace = nullspace;
		else: self.nullspace = { };

	def nullable(self, L):
		return TriBool.to_bool(self.nullable_(L));
	
	def __getitem__(self, key):
		return self.namespace[key];
	
	def __setitem__(self, key, value):
		self.namespace[key] = value;

	@ADT.Matcher
	def nullable_(add):
		@add(_, Null())
		def f(): return False_();

		@add(_, Epsilon())
		def f(): return True_();

		@add(_, Div())
		def f(): return True_();

		@add(_, Literal(_))
		def f(): return False_();

		@add(var('self'), Union(var('x'), var('y')))
		def f(self, x, y): return or_(self.nullable_(x), self.nullable_(y));

		@add(var('self'), Concat(var('x'), var('y')))
		def f(self, x, y): return and_(self.nullable_(x), self.nullable_(y));

		@add(_, Repeat(_))
		def f(): return True_();

		@add(var('self'), SemanticAction(_, var('L')))
		def f(self, L): return self.nullable_(L);

		@add(var('self'), Ref(var('name')))
		def f(self, name):
			l = Ref(name);
			r = self.nullspace.get(l, None)
			if r is not None: return r;

			self.nullspace[l] = Maybe_();
			r = self.nullspace[l] = self.nullable_(self.namespace[l]);
			return r;
		
		@add(var('self'), Derivative(var('s'), var('L')))
		def f(self, s, L):
			l = Derivative(s, L);
			r = self.nullspace.get(l, None);
			if r is not None: return r;

			self.nullspace[l] = Maybe_();
			r = self.nullspace[l] = self.nullable_(self.namespace[l]);
			return r;

	@ADT.Matcher
	def derivative(add):
		@add(_, _, Null())
		def f(): return null();

		@add(_, _, Epsilon())
		def f(): return null();

		@add(_, _, Div())
		def f(): return null();

		@add(_, var('c'), Literal(var('x')))
		def f(c, x): return literal(x[1:]) if c == x[0] else null();

		@add(var('self'), var('c'), Union(var('x'), var('y')))
		def f(self, c, x, y): return union(self.delayed_derivative(c, x), self.delayed_derivative(c, y));

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

		@add(var('c'), Derivative(var('s'), var('L')))
		def f(c, s, L):
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

		@add(var('self'), var('c'), Union(var('x'), var('y')))
		def f(self, c, x, y): return union(self.delayed_derivative(c, x), self.delayed_derivative(c, y));

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

	@add(var('s'), Literal(var('x')))
	def f(s, x):
		t = TerminalSet(x[0]);
		return [
				(t, literal(x[1:])),
				(s.subtract(t), null())
			];

	@add(var('s'), Union(var('x'), var('y')))
	def f(s, x, y):
		out = [];

		for (ls, l), (rs, r) in product(derivative_set(s, x), derivative_set(s, y)):
			t = ls.intersect(rs);
			if t.empty(): continue;
			out.append((t, union(l, r)));
		return out;
	
	@add(var('s'), Concat(var('x'), var('y')))
	def f(s, x, y):
		out = [];
		if nullable(x):
			for (ls, l), (rs, r) in product(derivative_set(s, x), derivative_set(s, y)):
				t = ls.intersect(rs);
				if t.empty(): continue;
				out.append((t, union(concat(l, y), r)));
		else:
			for (t, l) in derivative_set(s, x):
				out.append((t, concat(l, y)));
		return out;
	
	@add(var('s'), Repeat(var('x')))
	def f(s, x):
		return [(t, concat(l, repeat(x))) for t,l in derivative_set(s, x)];
