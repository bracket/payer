from payer.nodes import *
from payer import util


def test_languages():
    a = Terminal('a')
    b = Terminal('b')
    c = Terminal('c')

    abc = Concat(Concat(a, b), c)

    print(abc)

    a_or_b = Union(a, b)
    print(a_or_b)


def test_terminal_set():
    from payer.terminal_set import TerminalSet, Union

    lower_list = [ chr(i) for i in range(ord('a'), ord('z') + 1) ]
    upper_list = [ chr(i) for i in range(ord('A'), ord('Z') + 1) ]

    lower = TerminalSet.from_string('abcdefghijklmnopqrstuvwxyz')
    upper = TerminalSet.from_string('ABCDEFGHIJLKLMNOPQRSTUWVXYZ')

    alpha = Union(lower, upper)

    for c in lower_list:
        assert c in lower
        assert c in alpha

    for c in upper_list:
        assert c in upper
        assert c in alpha

    for c in range(0, 10):
        assert chr(c) not in alpha

def test_terminal_set_grammar():
    from payer.terminal_set import terminal_set_grammar

    language = terminal_set_grammar()

    test_string = '[abc]'

    print(repr(language))

    # language = language.derivative(Terminal(ord('[')))
