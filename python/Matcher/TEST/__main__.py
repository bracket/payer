import unittest, Matcher;
from Matcher import _, get_placeholders, match, find, var, regex, Matcher, MatchException;

class TestMatcher(unittest.TestCase):
    def test_get_placeholders(self):
        x, y, z = map(var, 'xyz');
        pattern = (x, (1, y), { 'weasel' : z });

        actual = get_placeholders(pattern);
        expected = { 'x' : x, 'y' : y, 'z' : z };

        self.assertEqual(actual, expected);

        pattern = (x, x);
        self.assertRaises(RuntimeError, get_placeholders, pattern);

    def test_match(self):
        x, y, z = map(var, 'xyz');
        pattern = (x, 'weasel', y, { 'beaver' : z , 'weasel' : 1 });

        self.assertTrue(match(pattern, (1, 'weasel', 2, { 'weasel' : 1, 'beaver' : 3 })))
        self.assertEqual((x.value, y.value, z.value), (1, 2, 3));
        self.assertFalse(match(pattern, (1, 2, 3)));

    def test_regex_match(self):
        x, y = regex('x', r'x*y'), regex('y', r'ba*b');
        pattern = (x, ('weasel', y));
        self.assertTrue(match(pattern, ('xxy', ('weasel', 'baaaaaab'))));
        self.assertEqual(('xxy', 'baaaaaab'), tuple(t.value.group() for t in (x, y)));
        self.assertFalse(match(pattern, ('xzy', ('weasel', 'baab'))));

    def test_find(self):
        pattern = (var('x'), 1, var('y'));
        f = list(find(pattern, ('a', { 'b' : ('x', 1, 'y') })));
        self.assertEqual(f, [(('x', 1, 'y'), {'x' : 'x', 'y' : 'y' })]);

    def test_matcher(self):
        @Matcher
        def f(add):
            @add(var('x'), 1, var('y'))
            def _f(x, y): return x + y;

            @add(var('x'))
            def _f(x): return '-{}-'.format(x);

        self.assertEqual(f(2, 1, 3), 5);
        self.assertEqual(f('three'), '-three-');
        self.assertRaises(MatchException, f, 2, 2, 3)

            
if __name__ == '__main__':
    unittest.main();