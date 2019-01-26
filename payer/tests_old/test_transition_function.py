from payer.transition_function import *

def test_transition_function():
    f = TransitionFunction.from_items([ (2, 'x'), (6, 'z'), (4, 'y') ])

    expected = [
        (1, 'x'), (2, 'x'), (3, 'y'),
        (4, 'y'), (5, 'z'), (6, 'z'),
        (7, f.undef)
    ]

    actual = [ (i, f(i)) for i in range(1, 8) ]

    assert actual == expected


def test_compaction():
    f = TransitionFunction.from_items([ (2, 'x'), (3, 'y'), (10, 'y'),
        (15, 'z'), (30, 'y'), (35, 'z') ])

    g = TransitionFunction.from_items([ (2, 'x'), (10, 'y'), (15, 'z'),
        (30, 'y'), (35, 'z') ])

    assert f.compact() == g


def test_indicator():
    terminals = { 0, 2, 3,  5, 7, 9, 10 }
    f = indicator(terminals, 10)

    for t in range(-1, 11):
        assert f(t) == (t in terminals)
