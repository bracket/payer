import pytest
from matcher import *

def test_get_placeholders():
    x, y, z = map(var, 'xyz')
    pattern = (x, (1, y), { 'weasel' : z })

    actual = get_placeholders(pattern)
    expected = { 'x' : x, 'y' : y, 'z' : z }

    assert actual == expected

    with pytest.raises(RuntimeError):
        pattern = (x, x)
        get_placeholders(pattern)


def test_match():
    x, y, z = map(var, 'xyz')
    pattern = (x, 'weasel', y, { 'beaver' : z , 'weasel' : 1 })

    assert match(pattern, (1, 'weasel', 2, { 'weasel' : 1, 'beaver' : 3 }))
    assert (x.value, y.value, z.value) == (1, 2, 3)
    assert not match(pattern, (1, 2, 3))


def test_regex_match():
    x, y = regexvar('x', r'x*y'), regexvar('y', r'ba*b')
    pattern = (x, ('weasel', y))

    assert match(pattern, ('xxy', ('weasel', 'baaaaaab')))
    assert ('xxy', 'baaaaaab') == tuple(t.value.group() for t in (x, y))
    assert not match(pattern, ('xzy', ('weasel', 'baab')))


def test_pass_through_match():
    x = passvar('x', ('y', (var('x'))))
    value = ('y', 1)

    assert match(x, value)

    assert x.value[0] is value
    assert x.value.parent is value

    assert x.value[1] ==  {'x' : 1}
    assert x.value.children == {'x' : 1}

    assert not match(x, ('z', 2))


def test_find():
    pattern = (var('x'), 1, var('y'))
    f = list(find(pattern, ('a', { 'b' : ('x', 1, 'y') })))

    assert f == [(('x', 1, 'y'), {'x' : 'x', 'y' : 'y' })]


def test_matcher():
    @Matcher.decorate
    def f(add):
        @add(var('x'), 1, var('y'))
        def _f(x, y): return x + y

        @add(var('x'))
        def _f(x): return '-{}-'.format(x)

    assert f(2, 1, 3) == 5
    assert f('three') ==  '-three-'

    with pytest.raises(MatchException):
        f(2, 2, 3)


def test_matcher_method():
    class C(object):
        @MatcherMethod.decorate
        def f(add):
            @add(1, var('x'), var('y'))
            def _f(self, x, y):
                return (self, x, y)

            @add(2, var('x'), var('y'))
            def _f(self, x , y):
                return None

    c = C()

    assert c.f(1, 'x', 'y') == (c, 'x', 'y')
    assert c.f(2, 1, 2) is None

    with pytest.raises(MatchException):
        c.f(3)


def test_top_down():
    term = [ 'x', [ 'y', 2, 3 ], [ 'z', 4, 5 ] ]
    matches = set()

    a = var('a')

    @Matcher.decorate
    def f(add):
        @add(('x', a, _))
        def _f(a):
            matches.add('x')
            return [ 'x', a ]

        @add(passvar('y', ('y', _, _)))
        def _f(y):
            matches.add('y')
            return y.parent

        @add(passvar('z', ('z', _, _)))
        def _f(z):
            matches.add('z')
            return z.parent

        @add(a)
        def _f(a):
            matches.add('_')
            return a

    assert top_down(f, term) == [ 'x', [ 'y', 2, 3 ] ]
    assert matches == { 'x', 'y', '_' }


def test_bottom_up():
    term = [ 'x', [ 'y', 2, 3 ], [ 'z', 4, 5 ] ]
    matches = set()

    a = var('a')

    @Matcher.decorate
    def f(add):
        @add(('x', a, _))
        def _f(a):
            matches.add('x')
            return [ 'x', a ]

        @add(passvar('y', ('y', _, _)))
        def _f(y):
            matches.add('y')
            return y.parent

        @add(passvar('z', ('z', _, _)))
        def _f(z):
            matches.add('z')
            return z.parent

        @add(a)
        def _f(a):
            matches.add('_')
            return a

    assert bottom_up(f, term) == [ 'x', [ 'y', 2, 3 ] ]
    assert matches == { 'x', 'y', 'z', '_' }
