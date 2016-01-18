import unittest;

from Payer.Language import *;
from Payer import Common;
from Matcher import *;

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
        import Payer.Common.Date as pcd;
        ls = pcd.languages;
        fmt = pcd.strptime('%Y-%m-%d %H:%M:%S');

        @Matcher
        def add_outputs(add):
            outs = {
                'Y' : 'year',  'm' : 'month',    'd' : 'day',
                'H' : 'hour', 'M' : 'minute', 'S' : 'second',
            };

            @add(passvar('t', ref(var('L'))))
            def _add_output(t):
                L = t.children['L'];
                if L in outs:
                    return concat(
                        output('%s-start' % outs[L], ref(L)),
                        output('%s-end' % outs[L], div())
                    );
                else: return t.parent;

            @add(var('x'))
            def _add_output(x): return x;

        fmt = bottom_up(add_outputs, fmt);

        for c in '2013-10-01 06:00:00':
            fmt = ls.derivative(ord(c), fmt);
        fmt = ls.finalize(fmt);

        self.assertTrue(ls.nullable(fmt));

        expected_outputs = [
              'year-start',   'year-end',
             'month-start',  'month-end',
               'day-start',    'day-end',
              'hour-start',   'hour-end',
            'minute-start', 'minute-end',
            'second-start', 'second-end',
        ];

        node = next(get_outputs(fmt));
        actual_outputs = list(reversed(list(node)));

        self.assertEqual(expected_outputs, actual_outputs);

if __name__ == '__main__':
    unittest.main()
