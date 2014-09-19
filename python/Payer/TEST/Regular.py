import unittest;
from Payer.Language import *;
import Payer.Regular as Regular;

class TestRegular(unittest.TestCase):
    def test_regular(self):
        g = Regular.grammar();

        tests = [
            (g['lbracket'], '['),
            (g['rbracket'], ']'),
            (g['bslash'], '\\'),
            (g['hyphen'], '-'),
            (repeat(g['special']),     '-[]\\'),
            (repeat(g['non_special']), 'abcdefg'),
            (repeat(g['escaped']), r'\\\[\]'),
            (repeat(g['char']), r'x\\\[abc'),
            (g['simple_range'], 'a-z'),
            (repeat(g['character_class_atom']), 'af-z'),
            (g['character_class'], '[af-z]'),
        ];

        for L, test in tests:
            for c in test:
                L = derivative(ord(c), L);
                self.assertNotEquals(L, null());
            self.assertEquals(finalize(L), epsilon());

if __name__ == '__main__':
    unittest.main();
