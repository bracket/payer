import inspect, itertools, re, sys;

__all__ = [
    'match', 'find',
    'var', 'regex', '_', 'get_placeholders',
    'Matcher', 'MatcherMethod', 'Finder',
    'MatchException',
];

_none = object();

def _is_str(x): return isinstance(x, (str, unicode));
def _is_sequence(x): return isinstance(x, (tuple, list));
def _is_mapping(x): return isinstance(x, dict);

def _iteritems(x): return x.iteritems();

class PlaceholderBase(object):
    def __init__(self, name):
        self.name = name;

class Placeholder(PlaceholderBase):
    def __init__(self, name):
        super(Placeholder, self).__init__(name);
        self.value = None;
        
    def match(self, value):
        self.value = value;
        return True;

class RegEx(PlaceholderBase):
    _re_type = type(re.compile(''));

    def __init__(self, name, regex):
        super(RegEx, self).__init__(name);

        if not isinstance(regex, self._re_type): regex = re.compile(regex);

        self.regex = regex;
        self.value = None;

    def match(self, value):
        if not _is_str(value): return False;
        m = self.value = self.regex.match(value);
        return m is not None;

def var(name): return Placeholder(name);
def regex(name, regex): return RegEx(name, regex);

_ = var('');

def get_placeholders(pattern, accum = None):
    if accum is None: accum = { };

    if isinstance(pattern, PlaceholderBase):
        if pattern.name in accum:
            raise RuntimeError("multiple instances of placeholder name in pattern name='{}'"
                .format(pattern.name));
        if pattern.name: accum[pattern.name] = pattern;
    elif _is_sequence(pattern):
        for p in pattern: get_placeholders(p, accum);
    elif _is_mapping(pattern):
        for k, p in _iteritems(pattern): get_placeholders(p, accum);

    return accum;

def match(pattern, value):
    if value is _none: return False;
    elif isinstance(pattern, PlaceholderBase): return pattern.match(value);
    elif _is_mapping(pattern) and _is_mapping(value):
        return all(match(p, value.get(k, _none)) for (k, p) in _iteritems(pattern));
    elif _is_sequence(pattern) and _is_sequence(value):
        return all(match(p, v) for p,v
            in itertools.izip_longest(pattern, value, fillvalue = _none));
    else: return pattern == value;

def find(pattern, value, depth = sys.maxint):
    remaining = [ (value, depth) ];
    placeholders = get_placeholders(pattern).items();

    while remaining:
        value,depth = remaining.pop(0);
        if depth <= 0: continue;

        if match(pattern, value): yield value, { k : v.value for k,v in placeholders };
        if _is_mapping(value): remaining.extend((v, depth - 1) for k, v in _iteritems(value));
        if _is_sequence(value): remaining.extend((v, depth - 1) for v in value);

class MatchException(BaseException): pass;

class PatternMatcherBase(object):
    def __init__(self, f, ignore_parameters = set()):
        self.name = f.__name__;
        self.patterns = [ ];
        self.ignore_parameters = set(ignore_parameters);
        f(self.add);

    def add(self, *pattern):
        def add_(f):
            placeholders = get_placeholders(pattern);
            args = [ arg for arg in inspect.getargspec(f)[0] if arg not in self.ignore_parameters ];
            diff = (placeholders.viewkeys() - args, args - placeholders.viewkeys());

            if diff[0] or diff[1]:
                raise MatchException('\n'.join((
                    'placeholder names differ from function argument names:',
                    "extra placeholders = '%s'" % ', '.join(sorted(diff[0])),
                    "extra args = '%s'" % ', '.join(sorted(diff[1])),
                )));

            args = tuple(placeholders[a] for a in args);
            self.patterns.append((pattern, args, f));

        return add_;

class Matcher(PatternMatcherBase):
    def __init__(self, f):
        super(Matcher, self).__init__(f);

    def __call__(self, *value):
        for pattern, args, f in self.patterns:
            if match(pattern, value): return f(*(p.value for p in args));
        raise MatchException("Inexhaustive pattern match in '{}': value = '{}'".format(self.name, value));

class MatcherMethod(PatternMatcherBase):
    def __init__(self, f):
        super(MatcherMethod, self).__init__(f, ignore_parameters = set(['self']));
    
    def __get__(self, instance, t):
        def bind(*value):
            for pattern, args, f in self.patterns:
                if match(pattern, value): return f(instance, *(p.value for p in args));
            raise MatchException("Inexhaustive pattern match in '{}': value = '{}'".format(self.name, value));
        return bind;
    
class Finder(PatternMatcherBase):
    def __init__(self, f):
        super(Finder, self).__init__(f);

    def __call__(self, *value):
        remaining = [ value ];

        while remaining:
            value = remaining.pop(0);
            for pattern, args, f in self.patterns:
                if match(pattern, value): f(*(p.value for p in args));
            if _is_mapping(value): remaining.extend(value.values());
            elif _is_sequence(value): remaining.extend(value);
