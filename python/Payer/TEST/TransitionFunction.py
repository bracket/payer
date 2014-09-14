import unittest;
from Payer.TransitionFunction import *;

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

if __name__ == '__main__':
    unittest.main();
