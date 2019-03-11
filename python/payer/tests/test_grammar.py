import payer.nodes as nodes

from payer.nodes import *
from payer.util import *


def test_languages():
    a = Terminal('a')
    b = Terminal('b')
    c = Terminal('c')

    abc = Concat(Concat(a, b), c)
    a_or_b = Union(a, b)
    repeat = Repeat(abc)

    assert null.nullity() is null
    assert null.derivative('a') is null
    assert null.regular()

    assert epsilon.nullity() is epsilon
    assert epsilon.derivative('a') is null
    assert epsilon.regular()

    assert dot.nullity() is null
    assert dot.derivative('a') is epsilon
    assert dot.regular()

    assert a.nullity() is null
    assert a.derivative('a') is epsilon
    assert a.derivative('b') is null
    assert a.regular()

    assert abc.nullity() is null
    assert abc.derivative('a') == Concat(b, c)
    assert abc.derivative('b') is null
    assert abc.derivative('a').derivative('b') == c
    assert abc.regular()

    assert a_or_b.nullity() is null
    assert a_or_b.derivative('a') is epsilon
    assert a_or_b.derivative('b') is epsilon
    assert a_or_b.derivative('c') is null
    assert a_or_b.regular()

    assert repeat.nullity() is epsilon
    assert repeat.derivative('a') is not null
    assert repeat.derivative('b') is null
    assert repeat.derivative('a').nullity() is null
    assert repeat.derivative('a').derivative('b').derivative('c') == repeat
    assert repeat.regular()


def test_terminal_bitset():
    from payer.terminal_bitset import TerminalBitset, Union

    lower_list = [ chr(i) for i in range(ord('a'), ord('z') + 1) ]
    upper_list = [ chr(i) for i in range(ord('A'), ord('Z') + 1) ]

    lower = TerminalBitset('abcdefghijklmnopqrstuvwxyz')
    upper = TerminalBitset('ABCDEFGHIJKLMNOPQRSTUVWXYZ')

    alpha = Union(lower, upper)

    assert lower.nullity() is null
    assert lower.derivative('b') is epsilon
    assert lower.derivative('B') is null
    assert lower.derivative('0') is null
    assert lower.regular()

    assert upper.nullity() is null
    assert upper.derivative('b') is null
    assert upper.derivative('B') is epsilon
    assert upper.derivative('0') is null
    assert upper.regular()

    assert alpha.nullity() is null
    assert alpha.derivative('b') is epsilon
    assert alpha.derivative('B') is epsilon
    assert upper.derivative('0') is null
    assert alpha.regular()

    for c in lower_list:
        assert c in lower
        assert c in alpha

    for c in upper_list:
        assert c in upper
        assert c in alpha

    for c in range(0, 10):
        assert chr(c) not in alpha


def test_output():
    a = Terminal('a')
    b = Terminal('b')
    c = Terminal('c')

    ab = Concat(a, b)
    abc = Concat(ab, c)
    ac = Concat(a, c)
    ab_dot = Concat(ab, dot)

    ab = Concat(ab, Output('ab_end', epsilon))
    abc = Concat(abc, Output('abc_end', epsilon))
    ac = Concat(ac, Output('ac_end', epsilon))
    ab_dot = Concat(ab_dot, Output('ab_dot_end', epsilon))

    ab = Output('ab_start', ab)
    abc = Output('abc_start', abc)
    ac = Output('ac_start', ac)
    ab_dot = Output('ab_dot_start', ab_dot)

    union = Union(Union(ab, abc), Union(ac, ab_dot))

    #TODO: Only checks nullity for now.  Need a way to collect and compare
    # output graphs.

    tests = [
        ( 'ab',  epsilon),
        ( 'abc', epsilon),
        ( 'abd', epsilon),
        ( 'ac',  epsilon),
        ( 'acd', null),
    ]

    for t, e in tests:
        test = union

        for c in t:
            test = test.derivative(c)

        assert test.nullity() is e


def test_terminal_set_grammar():
    from payer.terminal_bitset import terminal_set_grammar

    language = terminal_set_grammar()

    tests = [
        '[abc]',
        '[a-z]',
        '[-a-z]',
        '[^A]',
        '[^-]',
         r'[\]]',
         r'[\\]',
    ]

    for string in tests:
        test = language

        for c in string:
            test = test.derivative(c)

        assert test.terminate().nullity() is epsilon


def test_flat_concat():
    from payer.flat_concat import FlatConcat, Concat

    a = Terminal('a')
    b = Terminal('b')
    c = Terminal('c')

    ab = Concat(a, b)
    abc = FlatConcat([ a, b, c ])

    assert isinstance(ab, FlatConcat)
    assert isinstance(abc, FlatConcat)

    assert FlatConcat([]) is null
    assert FlatConcat([ a ]) is a

    assert ab.derivative('c') is null
    assert ab.derivative('a') == b

    assert ab.derivative('a').derivative('c') is null
    assert ab.derivative('a').derivative('b') is epsilon

    assert abc.derivative('a') == FlatConcat([ b, c ])


def test_flat_union():
    from payer.flat_union import FlatUnion, Union

    a = Terminal('a')
    b = Terminal('b')
    c = Terminal('c')

    ab = Union(a, b)
    abe = Union(ab, epsilon)

    assert isinstance(ab, FlatUnion)
    assert isinstance(abe, FlatUnion)

    assert ab.nullity() is null
    assert abe.nullity() is epsilon

    assert ab.derivative('c') is null
    assert ab.derivative('a') is epsilon
