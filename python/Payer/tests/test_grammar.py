from payer.grammar import *
from payer.language import *
from functools import reduce

globals().update(language_tags)

def test_get_references():
    import payer.grammar as grammar

    L = union(terminals(map(ord, 'xyz')), ref('weasel'))
    L = concat(L, ref('beaver'))

    expected = { ref('weasel'), ref('beaver') }

    assert grammar.get_references(L) == expected


def test_get_set():
    grammar = Grammar();
    ws = terminals([ord(' ')]);

    grammar['ws'] = ws;

    expected = { ref('ws') : ws };
    assert grammar._raw == expected


def test_determine_language_types():
    g = Grammar()
    x, y, z = [ terminals([ord(c)]) for c in 'xyz' ]

    g['weasel'] = reduce(union, [ x, y, z ])
    g['beaver'] = union(ref('weasel'), concat(ref('weasel'), ref('beaver')))

    expected = {
        ref('weasel') : RegularLanguage(),
        ref('beaver') : ContextFreeLanguage(),
    }

    assert g.language_types == expected

def test_finalize():
    grammar = Grammar();

    grammar['X'] = terminals([ ord('x') ]);
    grammar['L'] = union(concat(ref('X'), ref('L')), epsilon())

    expected = {
        ref('X') : null(),
        ref('L') : epsilon()
    }

    assert grammar.finalized == expected

    L = union(ref('X'), ref('L'))
    assert grammar.finalize(L) == epsilon()
