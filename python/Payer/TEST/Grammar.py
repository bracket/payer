import unittest;
from Payer.Grammar import *
from Payer.Language import *;

class TestGrammar(unittest.TestCase):
    def test_get_set(self):
        grammar = Grammar();
        ws = terminals([ord(' ')]);

        grammar['ws'] = ws;

        expected = { ref('ws') : ws };
        self.assertEquals(expected, grammar._raw);

    # def test_nullity_cache(self):
    #     ls = Grammar();
    #     x = terminals([ord('x')]);

    #     ls['L'] = union(concat(ref('L'), x), ref('L'));
    #     ls['R'] = union(concat(x, ref('R')), epsilon());

    #     ls['X'] = reduce(concat, (ref('Y'), x, ref('Y')));
    #     ls['Y'] = union(ref('X'), epsilon());

    #     ls.update_nullity_cache();
    #     self.assertEqual(ls._nullity_cache, {
    #         ref('L') : null(),
    #         ref('R') : epsilon(),
    #         ref('X') : null(),
    #         ref('Y') : epsilon(),
    #     });

if __name__ == '__main__':
    unittest.main();
