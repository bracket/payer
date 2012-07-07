# # from ADT import Type, ADT.Matcher, var, _;
# # from TerminalSet import TerminalSet;
# # from TriBool import *;

import ADT, TerminalSet, TriBool, Memo;
from ADT import var, _;
from TriBool import True_, False_, Maybe_, and_, or_;
from itertools import product;

namespace = { };
nullspace = { };

memo = Memo.SharedMemo();

class Action(ADT.Type): pass;

@memo
@Action
def ActionGenerator(): return (None,); # function type

@memo
@Action
def ActionList(): return ([None],); # function type

@ADT.Matcher
def delay_action(add):
	@add(ActionGenerator(var('g')))
	def f(g): return ActionList((g(),));

	@add(var('x'))
	def f(x): return x;

@ADT.Matcher
def dispatch_action(add):
	@add(ActionGenerator(var('g')))
	def f(g): g()();

	@add(ActionList(var('t')))
	def f(t): 
		for g in t: g();

@ADT.Matcher
def combine_delay(add):
	@add(ActionList(var('x')), ActionGenerator(var('g')))
	def f(x, g): return ActionList(x + (g(),));

	@add(ActionList(var('x')), ActionList(var('y')))
	def f(x, y): return ActionList(x + y);

	@add(ActionGenerator(var('g')), ActionList(var('x')))
	def f(g, x): return ActionList((g(),) + x);

	@add(ActionGenerator(var('g')), ActionGenerator(var('h')))
	def f(g, h): return ActionList((g(), h()));

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

@Memo.Memo
def literal(x):
	if x: return Literal(x);
	else: return Epsilon();

@Memo.Memo
@ADT.Matcher
def union(add):
	@add(Null(), var('x'))
	def f(x): return x;

	@add(var('x'), Null())
	def f(x): return x;

	@add(var('x'), var('y'))
	def f(x, y): return Union(x, y);

@Memo.Memo
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

@Memo.Memo
@ADT.Matcher
def semantic_action(add):
	@add(_, Null())
	def f(): return null();

	@add(var('g'), var('L'))
	def f(g, L): return SemanticAction(g, L);

@Memo.Memo
@ADT.Matcher
def nullable(add):
	@add(Null())
	def f(): return False;

	@add(Epsilon())
	def f(): return True;

	@add(Div())
	def f(): return True;

	@add(Literal(_))
	def f(): return False;

	@add(Union(var('x'), var('y')))
	def f(x, y): return nullable(x) or nullable(y);

	@add(Concat(var('x'), var('y')))
	def f(x, y): return nullable(x) and nullable(y);

	@add(Repeat(_))
	def f(x): return True;

	@add(SemanticAction(_, var('L')))
	def f(L): return nullable(L);

def ref(name): return Ref(name);

@Memo.Memo
@ADT.Matcher
def nullable_(add):
	@add(Null())
	def f(): return False_();

	@add(Epsilon())
	def f(): return True_();

	@add(Div())
	def f(): return True_();

	@add(Literal(_))
	def f(): return False_();

	@add(Union(var('x'), var('y')))
	def f(x, y): return or_(nullable_(x), nullable_(y));

	@add(Concat(var('x'), var('y')))
	def f(x, y): return and_(nullable_(x), nullable_(y));

	@add(Repeat(_))
	def f(x): return True_();

	@add(SemanticAction(_, var('L')))
	def f(L): return nullable_(L);

	@add(Ref(var('name')))
	def f(name):
		l = Ref(name);
		r = nullspace.get(l, None)
		if r is not None: return r;

		nullspace[l] = Maybe_();
		r = nullspace[l] = nullable_(namespace[l]);
		return r;
	
	@add(Derivative(var('s'), var('L')))
	def f(s, L):
		l = Derivative(s, L);
		r = nullspace.get(l, None);
		if r is not None: return r;

		nullspace[l] = Maybe_();
		r = nullspace[l] = nullable_(namespace[l]);
		return r;

@Memo.Memo
@ADT.Matcher
def derivative(add):
	@add(_, Null())
	def f(): return null();

	@add(_, Epsilon())
	def f(): return null();

	@add(_, Div())
	def f(): return null();

	@add(var('c'), Literal(var('x')))
	def f(c, x): return literal(x[1:]) if c == x[0] else null();

	@add(var('c'), Union(var('x'), var('y')))
	def f(c, x, y): return union(delayed_derivative(c, x), delayed_derivative(c, y));

	@add(var('c'), Concat(var('x'), var('y')))
	def f(c, x, y):
		if nullable(x): return union(concat(derivative(c, x), y), derivative(c, y));
		else: return concat(derivative(c, x), y);
	
	@add(var('c'), Repeat(var('x')))
	def f(c, x): return concat(derivative(c, x), repeat(x));

	@add(var('c'), SemanticAction(var('x'), var('L')))
	def f(c, x, L): dispatch_action(x); return derivative(c, L);

	@add(var('c'), Ref(var('name')))
	def f(c, name):
		l = Ref(name);
		d = Derivative(c, Ref(name));
		r = namespace.get(d, None);
		if r is not None: return r;

		namespace[d] = d;
		r = namespace[d] = derivative(c, namespace[l]);
		return r;

	@add(var('c'), Derivative(var('s'), var('L')))
	def f(c, s, L):
		l = Derivative(s, L);
		d = Derivative(s + c, L);
		r = namespace.get(d, None);
		if r is not None: return r;

		namespace[d] = d;
		r = namespace[d] = derivative(c, namespace[l]);

		return r;

@Memo.Memo
@ADT.Matcher
def delayed_derivative(add):
	@add(var('c'), SemanticAction(var('x'), SemanticAction(var('y'), var('L'))))
	def f(c, x, y, L): return delayed_derivative(c, SemanticAction(combine_delay(x, y), L));

	@add(var('c'), SemanticAction(var('x'), var('L')))
	def f(c, x, L): return semantic_action(delay_action(x), delayed_derivative(c, L));

	@add(var('c'), Union(var('x'), var('y')))
	def f(c, x, y): return union(delayed_derivative(c, x), delayed_derivative(c, y));

	@add(var('c'), Concat(var('x'), var('y')))
	def f(c, x, y):
		if nullable(x): return union(concat(delayed_derivative(c, x), y), delayed_derivative(c, y));
		else: return concat(delayed_derivative(c, x), y);
	
	@add(var('c'), Repeat(var('x')))
	def f(c, x): return concat(delayed_derivative(c, x), repeat(x));

	@add(var('c'), var('L'))
	def f(c, L): return derivative(c, L);

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

@Memo.Memo
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
