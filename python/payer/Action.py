import ADT;
from ADT import var, _;
from Memo import SharedMemo;

memo = SharedMemo();

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

