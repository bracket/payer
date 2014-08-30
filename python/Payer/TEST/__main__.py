import unittest;

from Payer.TransitionFunction import *;
from Payer.Language import *;
from Payer.Grammar import *;
from Matcher import _;
import Matcher.TEST;

class TestTransitionFunction(unittest.TestCase):
    def test_transition_function(self):
        f = TransitionFunction.from_items([ (2, 'x'), (6, 'z'), (4, 'y') ]);

        expected = [
            (1, 'x'), (2, 'x'), (3, 'y'),
            (4, 'y'), (5, 'z'), (6, 'z'),
            (7, f.undef)
        ];

        actual = [ (i, f(i)) for i in range(1, 8) ];

        self.assertEqual(actual, expected);

    def test_compaction(self):
        f = TransitionFunction.from_items([ (2, 'x'), (3, 'y'), (10, 'y'),
            (15, 'z'), (30, 'y'), (35, 'z') ])

        g = TransitionFunction.from_items([ (2, 'x'), (10, 'y'), (15, 'z'),
            (30, 'y'), (35, 'z') ]);

        self.assertEqual(f.compact(), g);

class TestLanguage(unittest.TestCase):
    assertMatches = Matcher.TEST.assertMatches;

    def test_language_operators(self):
        x, y, z = (terminals([ord(t)]) for t in 'xyz');

        tests = [
            (union(null(), null()), null()),
            (union(x, null()), x),
            (union(null(), y), y),
            (concat(x, null()), null()),
            (concat(null(), y), null()),
            (concat(x, epsilon()), x),
            (concat(epsilon(), y), y),
            (union(x, y), terminals(map(ord, 'xy'))),
        ];

        for actual, expected in tests:
            self.assertEqual(actual, expected);

    def test_nullable(self):
        x, y, z = (terminals([ord(t)]) for t in 'xyz');

        tests = [
            (null(), False),
            (epsilon(), True),
            (x, False),
            (repeat(x), True),
            (union(x, epsilon()), True),
            (union(x, y), False),
            (concat(x, y), False),
            (output(1, epsilon()), True),
            (output(1, x), False),
        ];

        for value, expected in tests:
            self.assertEqual(nullable(value), expected);

    def test_split_concat(self):
        x, y, z = (terminals([ord(t)]) for t in 'xyz');

        tests = [
            (x, (x, epsilon())),
            (concat(x, y), (x, y)),
            (reduce(concat, (x, y, z)), (x, concat(y, z))),
        ];

        for value, expected in tests:
            self.assertEqual(split_concat(value), expected);

    def test_derivative(self):
        x, y, z = (terminals([ord(t)]) for t in 'xyz');
        xy = concat(x, y);
        space = Grammar();

        tests = [
            (null(),       'x', [ null() ]),
            (epsilon(),    'x', [ null() ]),
            (x,            'x', [ epsilon() ]),
            (y,            'x', [ null() ]),
            (union(x, y),  'x', [ epsilon() ]),
            (union(x, y),  'z', [ null() ]),
            (concat(x, y), 'xy',[ y, epsilon() ]),
            (concat(x, y), 'y', [ null() ]),
            (repeat(x),    'xxy', [ repeat(x), repeat(x), null() ]),
            (repeat(xy),   'xyy', [ concat(y, repeat(xy)), repeat(xy), null() ]),
            (output(1, x), 'y', [ null() ]),
        ];

        for value, tokens, expecteds in tests:
            for token, expected in zip(tokens, expecteds):
                value = space.derivative(ord(token), value);
                self.assertEqual(value, expected);

    def test_derivative_concat(self):
        x, y, z = (terminals([ ord(t) ]) for t in 'xyz');
        ls = Grammar();

        L = reduce(concat, (x, output('z', div()), y, z));

        L = ls.derivative(ord('x'), L);
        self.assertMatches(L, output('z', reduce(concat, (div(), y, z))));

        L = ls.derivative(ord('y'), L);
        self.assertMatches(output_node(_, z), L);

    # def test_finalize(self):
    #     x, y, z = (terminals([ord(t)]) for t in 'xyz');
    #     space = Grammar();

    #     tests = [
    #         (null(), null()),
    #         (epsilon(), null()),
    #         (x, null()),
    #         (union(x, epsilon()), epsilon()),
    #         (concat(x, y), null()),
    #         (repeat(x), epsilon()),
    #         (output(1, x), null()),
    #     ];

    #     for value, expected in tests:
    #         print value;
    #         self.assertEqual(space.finalize(value), expected);

    def test_output(self):
        x,y,z = (terminals((ord(t),)) for t in 'xyz');
        space = Grammar();
        L = reduce(concat, [ output(3, x), output(1, y), union(output(5, y), output(4, z)) ]);
        for c in 'xyz': L = space.derivative(ord(c), L);

        out = tuple(reversed(list(next(get_outputs(L)))));
        self.assertEqual(out, (3, 1, 4));

class TestGrammar(unittest.TestCase):
    def test_get_set(self):
        ls = Grammar();
        ws = terminals([ord(' ')]);

        ls['ws'] = ws;

        expected = { ref('ws') : ws };
        self.assertEquals(expected, ls._languages);

    def test_nullity_cache(self):
        ls = Grammar();
        x = terminals([ord('x')]);

        ls['L'] = union(concat(ref('L'), x), ref('L'));
        ls['R'] = union(concat(x, ref('R')), epsilon());

        ls['X'] = reduce(concat, (ref('Y'), x, ref('Y')));
        ls['Y'] = union(ref('X'), epsilon());

        ls.update_nullity_cache();
        self.assertEqual(ls._nullity_cache, {
            ref('L') : null(),
            ref('R') : epsilon(),
            ref('X') : null(),
            ref('Y') : epsilon(),
        });

if __name__ == '__main__':
    unittest.main();
