import unittest;
from Matcher import  *;

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
    
    def test_matcher_method(self):
        class C(object):
            @MatcherMethod
            def f(add):
                @add(1, var('x'), var('y'))
                def _f(self, x, y): return (self, x, y);

                @add(2, var('x'), var('y'))
                def _f(self, x , y): return None;

        c = C();

        self.assertEqual(c.f(1, 'x', 'y'), (c, 'x', 'y'));
        self.assertEqual(c.f(2, 1, 2), None);
        self.assertRaises(MatchException, c.f, 3);
    
    def test_top_down(self):
        term = [ 'x', [ 1, 2 ], [ 2, 3 ] ];

        @Matcher
        def f(add):
            @add(('x', var('x'), var('y')))
            def _f(x, y): return x + y;

            @add((var('x')))
            def _f(x):
                if isinstance(x, list): return sum(x);
                else: return x;
        
        self.assertEqual(top_down(f, term), 8);

    def test_bottom_up(self):
        term = [ 'x', [ 'x', 1, 2 ], [ 'y', 3, 4] ];

        @Matcher
        def f(add):
            @add(('x', var('x'), var('y')))
            def _f(x, y): return x * y;

            @add(('y', var('x'), var('y')))
            def _f(x, y): return x - y;

            @add(var('x'))
            def _f(x): return x;

        self.assertEqual(bottom_up(f, term), -2);

if __name__ == '__main__':
    unittest.main();
