import unittest, Matcher.TEST;
from Payer.Language import *;

globals().update(type_tags);

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

    def test_finalize(self):
        x, y, z = (terminals([ord(t)]) for t in 'xyz');

        tests = [
            (null(), Null()),
            (epsilon(), Epsilon()),
            (x, Null()),
            (repeat(x), Epsilon()),
            (union(x, epsilon()), Epsilon()),
            (union(x, y), Null()),
            (concat(x, y), Null()),
            (output(1, epsilon()), OutputNode(1, Epsilon())),
            (output(1, x), Null()),
        ];

        for value, expected in tests:
            self.assertEqual(finalize(value), expected);

    def test_derivative(self):
        x, y, z = (terminals([ord(t)]) for t in 'xyz');
        xy = concat(x, y);

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
        ];

        for value, tokens, expecteds in tests:
            for token, expected in zip(tokens, expecteds):
                value = derivative(ord(token), value);
                self.assertEqual(value, expected);

    def test_output(self):
        x,y,z = (terminals((ord(t),)) for t in 'xyz');

        L = reduce(concat, [ output(3, x), output(1, y), union(output(5, y), concat(output(4, z), output(6, epsilon()))) ]);
        for c in 'xyz': L = derivative(ord(c), L);
        L = finalize(L);

        expected = output_node(3, output_node(1, output_node(4, output_node(6, epsilon()))));
        self.assertEqual(L, expected);

if __name__ == '__main__':
    unittest.main();
