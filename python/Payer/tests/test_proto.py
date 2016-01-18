import unittest;

from Payer import Proto;
from Payer.TypeTag import TypeTag;

Null = TypeTag('Null');
Union = TypeTag('Union');
Terminals = TypeTag('Terminals');

class TestProto(unittest.TestCase):
    def test_union(self):
        @Proto.decorate
        def union():
            r'''Returns the union of two languages

                union Null x = x;
                union x Null = x;
                union (Union x) (Union y) = Union(x | y);
                union x (Union y) = Union({x} | y);
                union (Union x) y = Union(x | {y});
                union (Terminals x) (Terminals y) = union_terminals(x, y);
                union x y = x if x == y else Union({ x, y });
            ''';

    def test_decorate_method(self):
        class TestClass(object):
            def __init__(self, value):
                self.value = value;

            @Proto.decorate_method
            def get_value():
                r'''Returns first argument, gets instance attribute 'value' otherwise.

                    value x = x;
                    value   = self.value;
                '''

        v = TestClass(2);
        self.assertEqual(v.get_value(1), 1);
        self.assertEqual(v.get_value(), 2);

if __name__ == '__main__':
    unittest.main();
