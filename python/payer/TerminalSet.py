def _front(x): return x[0] if isinstance(x, tuple) else x;
def _back(x): return x[1] if isinstance(x, tuple) else x;
def _range(x): return (_front(x), _back(x));
def _shrink(x, y): return x if x == y else (x, y);

def _S(c): return chr(ord(c) + 1) if isinstance(c, str) else c + 1;
def _P(c): return chr(ord(c) - 1) if isinstance(c, str) else c - 1;

def _meld(x, y):
	if _S(_back(x)) < _front(y): return (x, y);
	if _back(x) < _back(y): return ((_front(x), _back(y)), None);
	return (x, None);

def _meld_list(l):
	current = None;
	for v in l:
		if current is None: current = v;
		else:
			current, v = _meld(current, v);
			if v is not None:
				yield current;
				current = v;
	if current is not None: yield current;

_none = object();

def _merge(left, right, key = lambda x : x):
	left, right = map(iter, (left, right));
	l = next(left, _none); r = next(right, _none);

	while l is not _none and r is not _none:
		if key(l) <= key(r): yield l; l = next(left, _none);
		else: yield r; r = next(right, _none);
	
	while l is not _none: yield l; l = next(left, _none);
	while r is not _none: yield r; r = next(right, _none);

def _quote(s):
	return "'%s'" % s if isinstance(s, str) else str(s);

class TerminalSet(object):
	def __init__(self, *args, **kwargs):
		if not kwargs.get('skip_clean', False): args = tuple(_meld_list(sorted(args, key=_front)));
		self.values = args;
	
	def __str__(self):
		return 'TerminalSet(%s)' % ', '.join(map(_quote, self.values));
	
	def __contains__(self, x):
		low, high = 0, len(self.values);
		if high <= low: return False;

		while low < high:
			mid = (low + high - 1) / 2;
			ml, mh = _range(self.values[mid]);
			if x < ml: high = mid;
			elif x > mh: low = mid + 1;
			else: return True;

		return False;
	
	def __or__(self, other):
		return self.union(other);
	
	def __and__(self, other):
		return self.intersection(other);

	def empty(self):
		return not self.values;
	
	def min(self):
		return _front(self.values[0]);
	
	def max(self):
		return _back(self.values[-1]);
	
	def union(self, other):
		return TerminalSet(
			*_meld_list(_merge(self.values, other.values, key=_front)),
			skip_clean = True
		);
	
	def intersection(self, other):
		left, right = self.values, other.values;
		if not self.values: return self;
		if not other.values: return other;
		i, m = (0, len(left)); j, n = (0, len(right));

		out = [];
		while i < m and j < n:
			ip = i + 1; jp = j + 1;
			ll, lh = _range(left[i]);
			rl, rh = _range(right[j]);

			if lh < rl: i = ip;
			elif rh < ll: j = jp;
			else:
				l, h = max(ll, rl), min(lh, rh);
				out.append(_shrink(max(ll, rl), min(lh, rh)));
				if ip < m and _front(left[ip]) <= rh: i = ip;
				elif jp < n and _front(right[jp]) <= lh: j = jp;
				else: i, j = ip, jp;

		return TerminalSet(*out, skip_clean = True);
	
	def complement(self, low, high):
		out = [];
		last = None;
		for v in self.values:
			l, h = _range(v);
			if last is None:
				if low < l: out.append(_shrink(low, _P(l)));
			else:
				out.append(_shrink(_S(last), _P(l)));
			last = h;
		if h < high: out.append(_shrink(_S(h), high));
		return TerminalSet(*out, skip_clean = True);
	
	def subtract(self, other):
		return self.intersection(other.complement(self.min(), self.max()));
