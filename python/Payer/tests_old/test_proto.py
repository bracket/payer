from matcher import match, var
from payer import proto

def test_decorate():
    @proto.decorate
    def test():
        r'''Test function

            test 1 x = x + 1
            test 2 x = x - 2
            test x y = 10
        '''

    expected = [
        (1, var('x')),
        (2, var('x')),
        (var('x'), var('y')),
    ]

    actual = [ pattern for pattern, _, _ in test.patterns ]

    for e, a in zip(expected, actual):
        assert match(e, a)
        assert match(a, e)

    assert test(1, 2) == 3
    assert test(2, 1) == -1
    assert test(5, 6) == 10


def test_decorate_method():
    class TestClass(object):
        def __init__(self, value):
            self.value = value

        @proto.decorate_method
        def get_value():
            r'''Returns first argument, gets instance attribute 'value' otherwise.

                value x = x
                value   = self.value
            '''
    matcher = TestClass.__dict__['get_value']

    expected = [
        (var('x'),),
        tuple()
    ]

    actual = [ pattern for pattern, _, _ in matcher.patterns ]

    for e,a in zip(expected, actual):
        assert match(e, a)
        assert match(a, e)

    v = TestClass(2)
    assert v.get_value(1) == 1
    assert v.get_value() == 2
