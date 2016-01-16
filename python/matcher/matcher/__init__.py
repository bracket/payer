r'''Provides basic pattern matching against Python tuples, lists, and dictionaries.'''

__version__ = '0.1.0'

from collections import namedtuple
from itertools import zip_longest
import inspect
import re
import sys

__all__ = [
    'Finder',
    'FinderMethod',
    'MatchException',
    'Matcher',
    'MatcherMethod',
    '_',
    'bottom_up',
    'find',
    'get_placeholders',
    'match',
    'passvar',
    'regexvar',
    'top_down',
    'typedvar',
    'var',
]

none = object()

TEXT = (str,)
SEQUENCE = (tuple, list)
DICT = (dict,)


class PlaceholderBase(object):
    def __init__(self, name):
        self.name = name


class Placeholder(PlaceholderBase):
    def __init__(self, name):
        super().__init__(name)
        self.value = None
        
    def match(self, value):
        self.value = value
        return True

    def __repr__(self):
        if not self.name: return '_'
        else: return "var({})".format(self.name)


PassthroughTuple = namedtuple('PassthroughTuple', [ 'parent', 'children' ])


class PassThroughPlaceholder(PlaceholderBase):
    def __init__(self, name, pattern):
        super().__init__(name)
        self.pattern = pattern
        self.children = get_placeholders(pattern)

    def match(self, value):
        if not match(self.pattern, value):
            return False

        self.value = PassthroughTuple(
            value,
            { n : p.value for n, p in self.children.items() }
        )

        return True


class TypedPlaceholder(PlaceholderBase):
    def __init__(self, name, types):
        super().__init__(name)

        if isinstance(types, SEQUENCE):
            self.types = tuple(types)
        else:
            self.types = (types,)
    
    def match(self, value):
        if not type(value) in self.types:
            return False

        self.value = value
        return True


class RegExPlaceholder(PlaceholderBase):
    _re_type = type(re.compile(''))

    def __init__(self, name, regex):
        super(RegExPlaceholder, self).__init__(name)

        if not isinstance(regex, self._re_type): regex = re.compile(regex)

        self.regex = regex
        self.value = None

    def match(self, value):
        if not isinstance(value, TEXT):
            return False

        m = self.value = self.regex.match(value)
        return m is not None


def var(name):
    return Placeholder(name)


def passvar(name, pattern):
    return PassThroughPlaceholder(name, pattern)


def typedvar(name, ty):
    return TypePlaceholder(name, ty)


def regexvar(name, regex):
    return RegExPlaceholder(name, regex)


_ = var('')


def get_placeholders(pattern, accum = None):
    if accum is None: accum = { }

    if isinstance(pattern, PlaceholderBase):
        if pattern.name in accum:
            raise RuntimeError(
                "multiple instances of placeholder name in pattern name='{}'"
                .format(pattern.name)
            )
        if pattern.name:
            accum[pattern.name] = pattern
    elif isinstance(pattern, SEQUENCE):
        for p in pattern:
            get_placeholders(p, accum)
    elif isinstance(pattern, DICT):
        for k, p in pattern.items():
            get_placeholders(p, accum)

    return accum


def match(pattern, value):
    r'''Attempt to unify 'pattern' with 'value'.  Returns True on success. False otherwise.

    On successful completion, all placeholders in 'pattern' will have been
    mutated so that their 'value' attribute refers to the successfully matching
    element in the 'value'.  Note that placeholders may be mutated even if
    pattern matching fails.  Use 'get_placeholders' to extract all placeholders
    from 'pattern'.
    '''

    if value is none:
        return False
    elif isinstance(pattern, PlaceholderBase):
        return pattern.match(value)
    elif isinstance(pattern, DICT) and isinstance(value, DICT):
        return all(match(p, value.get(k, none)) for (k, p) in pattern.items())
    elif isinstance(pattern, SEQUENCE) and isinstance(value, SEQUENCE):
        return all(match(p, v) for p,v
            in zip_longest(pattern, value, fillvalue=none))
    else:
        return pattern == value


def find(pattern, value, depth = sys.maxsize):
    remaining = [ (value, depth) ]
    placeholders = get_placeholders(pattern).items()

    while remaining:
        value,depth = remaining.pop(0)
        if depth <= 0: continue

        if match(pattern, value):
            yield value, { k : v.value for k,v in placeholders }

        if isinstance(value, DICT):
            remaining.extend((v, depth - 1) for k, v in value.items())

        if isinstance(value, SEQUENCE):
            remaining.extend((v, depth - 1) for v in value)


def nest(f, term):
    result = f(term)
    while term is not result:
        term, result = result, f(result)
    return result


def top_down(f, term):
    term = nest(f, term)

    if isinstance(term, SEQUENCE):
        return type(term)(top_down(f, t) for t in term)
    elif isinstance(term, DICT):
        return type(term)((k, top_down(f, t)) for k, t in term.items())
    else:
        return term


def bottom_up(f, term):
    if isinstance(term, SEQUENCE):
        term = type(term)(bottom_up(f, t) for t in term)
    elif isinstance(term, DICT):
        term = type(term)((k, bottom_up(f, t)) for k, t in term.items())

    return nest(f, term)


class MatchException(Exception):
    pass


class PatternMatcherBase(object):
    def __init__(self, name, ignore_parameters = None):
        self.name = name
        self.patterns = [ ]

        self.ignore_parameters = (
            set()
            if ignore_parameters is None
            else set(ignore_parameters)
        )


    @classmethod
    def decorate(cls, f, ignore_parameters = set()):
        out = cls(f.__name__, ignore_parameters)
        f(out.make_add_decorator())
        return out


    def add(self, pattern, function):
        placeholders = get_placeholders(pattern)
        args = [ arg for arg in inspect.getargspec(function)[0] if arg not in self.ignore_parameters ]
        diff = (placeholders.keys() - args, args - placeholders.keys())

        if diff[0] or diff[1]:
            raise MatchException('\n'.join((
                'placeholder names differ from function argument names:',
                "extra placeholders = '%s'" % ', '.join(sorted(diff[0])),
                "extra args = '%s'" % ', '.join(sorted(diff[1])),
            )))

        args = tuple(placeholders[a] for a in args)
        self.patterns.append((pattern, args, function))

        return function


    def make_add_decorator(self):
        def decorator(*pattern):
            return lambda function: self.add(pattern, function)
        return decorator


class Matcher(PatternMatcherBase):
    def __call__(self, *value):
        for pattern, args, f in self.patterns:
            if match(pattern, value): return f(*(p.value for p in args))
        raise MatchException("Inexhaustive pattern match in '{}': value = '{}'".format(self.name, value))


class MatcherMethod(PatternMatcherBase):
    def __init__(self, name, ignore_parameters = None):
        ip = { 'self' }

        if ignore_parameters is not None:
            ip.update(ignore_parameters)

        super().__init__(name, ignore_parameters = ip)

    
    def __get__(self, instance, t):
        def bind(*value):
            for pattern, args, f in self.patterns:
                if match(pattern, value):
                    return f(instance, *(p.value for p in args))

            raise MatchException("Inexhaustive pattern match in '{}': value = '{}'".format(self.name, value))

        return bind
    
class Finder(PatternMatcherBase):
    def __call__(self, value):
        remaining = [ value ]

        while remaining:
            value = remaining.pop(0)

            for pattern, args, f in self.patterns:
                if match(pattern, (value,)):
                    f(*(p.value for p in args))

            if isinstance(value, DICT):
                remaining.extend(value.values())
            elif isinstance(value, SEQUENCE):
                remaining.extend(value)

class FinderMethod(PatternMatcherBase):
    def __init__(self, name, ignore_parameters = None):
        ip = { 'self' }

        if ignore_parameters is not None:
            ip.update(ignore_parameters)

        super().__init__(name, ignore_parameters = ip)
    
    def __get__(self, instance, t):
        def bind(value):
            remaining = [ value ]

            while remaining:
                value = remaining.pop(0)
                for pattern, args, f in self.patterns:
                    if match(pattern, (value,)):
                        f(instance, *(p.value for p in args))
                if isinstance(value, DICT):
                    remaining.extend(value.values())
                elif isinstance(value, SEQUENCE):
                    remaining.extend(value)

        return bind
