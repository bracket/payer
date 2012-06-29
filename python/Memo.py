class Memo(object):
	def __init__(self, f, cache = None):
		self.f = f;
		if cache is None: self.cache = { };
		else: self.cache = cache;
		self.none = object();
	
	def __call__(self, *args):
		key = (self.f, args);
		v = self.cache.get(key, self.none);
		if v is not self.none: return v;
		v = self.cache[key] = self.f(*args);
		return v;

def SharedMemo():
	cache = { };
	return lambda f: Memo(f, cache = cache);
