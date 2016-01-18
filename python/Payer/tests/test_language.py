from payer.language import *
from functools import reduce

globals().update(type_tags)

def test_language_operators():
    x, y, z = (terminals([ord(t)]) for t in 'xyz')

    assert union(null(), null()) == null()
    assert union(x, null())      == x
    assert union(null(), y)      == y
    assert concat(x, null())     == null()
    assert concat(null(), y)     == null()
    assert concat(x, epsilon())  == x
    assert concat(epsilon(), y)  == y
    assert union(x, y)           == terminals(map(ord, 'xy'))


def test_finalize():
    x, y, z = (terminals([ord(t)]) for t in 'xyz')

    assert finalize(null())               == Null()
    assert finalize(epsilon())            == Epsilon()
    assert finalize(x)                    == Null()
    assert finalize(repeat(x))            == Epsilon()
    assert finalize(union(x, epsilon()))  == Epsilon()
    assert finalize(union(x, y))          == Null()
    assert finalize(concat(x, y))         == Null()
    assert finalize(output(1, epsilon())) == OutputNode(1, Epsilon())
    assert finalize(output(1, x))         == Null()


def test_derivative():
    x, y, z = (terminals([ord(t)]) for t in 'xyz')
    xy = concat(x, y)

    tests = [
        (null(),       'x',   [ null() ]),
        (epsilon(),    'x',   [ null() ]),
        (x,            'x',   [ epsilon() ]),
        (y,            'x',   [ null() ]),
        (union(x, y),  'x',   [ epsilon() ]),
        (union(x, y),  'z',   [ null() ]),
        (concat(x, y), 'xy',  [ y, epsilon() ]),
        (concat(x, y), 'y',   [ null() ]),
        (repeat(x),    'xxy', [ repeat(x), repeat(x), null() ]),
        (repeat(xy),   'xyy', [ concat(y, repeat(xy)), repeat(xy), null() ]),
        (output(1, x), 'y',   [ null() ]),
    ]

    for value, tokens, expecteds in tests:
        for token, expected in zip(tokens, expecteds):
            value = derivative(ord(token), value)
            assert value == expected


def test_output():
    x,y,z = (terminals((ord(t),)) for t in 'xyz')

    L = reduce(concat, [ output(3, x), output(1, y), union(output(5, y), concat(output(4, z), output(6, epsilon()))) ])
    for c in 'xyz':
        L = derivative(ord(c), L)
    L = finalize(L)

    expected = output_node(3, output_node(1, output_node(4, output_node(6, epsilon()))))
    assert L == expected
