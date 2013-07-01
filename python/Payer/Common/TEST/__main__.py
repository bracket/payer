import unittest;

from Payer.Language import *;
from Payer import Common;

class TestCommon(unittest.TestCase):
    def test_basic(self):
        ls = Common.languages;

        tests = [
            (ref('lower_alpha'), 'b', True),
            (ref('lower_alpha'), 'X', False),
            (ref('upper_alpha'), 'c', False),
            (ref('upper_alpha'), 'G', True),
            (ref('alpha'), 'h', True),
            (ref('alpha'), 'J', True),
            (ref('alpha'), '0', False),
        ];

        for value, seq, expected in tests:
            for x in seq: value = ls.derivative(ord(x), value);
            self.assertEqual(ls.nullable(value), expected);

    def test_date(self):
        from Payer.Common.Date import strptime;
        ls = LanguageSpace();

        fmt = strptime('%Y-%m-%d %H:%M:%S');
        for c in '2013-10-01 06:00:00': fmt = ls.derivative(ord(c), fmt);
        self.assertTrue(ls.nullable(fmt));

if __name__ == '__main__':
    unittest.main()
