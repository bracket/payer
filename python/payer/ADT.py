from itertools import izip, starmap;
import inspect;
from functools import total_ordering;

@total_ordering
class Type(object):
	def __init__(self, constructor):
		self.constructor = constructor;
		self.__name__ = constructor.__name__;
		self.arg_types = constructor();
	
	def __call__(self, *args):
		assert(len(args) == len(self.arg_types));
		return (self,) + args;
	
	def __str__(self):
		return self.__name__;
	
	def __repr__(self):
		return self.__name__;
	
	def __eq__(self, other):
		return self.__name__ == other.__name__;
	
	def __lt__(self, other):
		return self.__name__ < other.__name__;
	
class Placeholder(object):
	def __init__(self, name):
		self.name = name;
		self.value = None;

	def bind(self, value):
		self.value = value;
	
	def get(self):
		return self.value;

def var(name):
	return Placeholder(name);

_ = var('');

def match(left, right):
	if isinstance(left, (tuple, list)) and isinstance(right, (tuple, list)):
		if len(left) != len(right): return False;
		return all(starmap(match, izip(left, right)));
	if isinstance(left, Placeholder):
		left.bind(right);
		return True;
	return left == right;

def get_placeholders(pattern):
	out = { };
	def traverse(p):
		if isinstance(p, (tuple, list)): 
			for x in p: traverse(x);
		if isinstance(p, Placeholder): out[p.name] = p;

	traverse(pattern);
	return out;

class Matcher(object):
	def __init__(self, f):
		self.patterns = [];
		m = lambda *p: (lambda g: self.add(p, g))
		f(m);
	
	def add(self, pattern, f):
		args = inspect.getargspec(f).args;
		binding = map(get_placeholders(pattern).get, args);
		self.patterns.append((pattern, binding, f));
	
	def __call__(self, *args):
		for pattern, binding, f in self.patterns:
			if match(pattern, args):
				return f(*map(Placeholder.get, binding));
	
	def __get__(self, other, other_type):
		def f(*args): return self.__call__(other, *args);
		return f;
