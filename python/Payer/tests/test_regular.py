import unittest, Payer.TEST;
from Payer.Language import *;
import Payer.Regular as Regular;

class TestRegular(unittest.TestCase):
    assertRecognizes = Payer.TEST.assertRecognizes;

    def test_regular(self):
        g = Regular.grammar();

        tests = [
            (g['lbracket'], '['),
            (g['rbracket'], ']'),
            (g['bslash'], '\\'),
            (g['hyphen'], '-'),
            (repeat(g['special']),     '-[]\\()|'),
            (repeat(g['non_special']), 'abcdefg'),
            (repeat(g['escaped']), r'\\\[\]'),
            (repeat(g['char']), r'x\\\[abc'),
            (g['simple_range'], 'a-z'),
            (repeat(g['char_class_atom']), 'af-z'),
            (g['char_class'], '[af-z]'),
            (g['concat_atom'], 'x'),
            (g['concat_atom'], r'[1-3\]]'),
            (g['concat'], r'a[a-zA-Z0-9]'),
            (g['union_sequence'], r'a|b|c|[d-z]'),
            (g['union'], r'([0-9]|a|b|\[)'),
            (g['repeat'], r'a*'),
            (g['regular'], '[_a-zA-Z][_a-zA-Z0-9]*'),
        ];

        for L, s in tests: self.assertRecognizes(L, s);

if __name__ == '__main__':
    unittest.main();
