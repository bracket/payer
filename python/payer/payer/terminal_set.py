from .util import list_to_concat, list_to_union, memoize
from . import nodes

import numpy as np

# TODO: Allow import from *exactly* one module which offers increased
# optimization unless the user knows what they are doing.  It is desirable to
# keep the optimizations separate from the basic code so that the latter is
# more understandable (and potentially useable) than the former.

# Add imports here that aren't overridden

__all__ = [
    'TerminalSet',
    'Union',
    'terminal_set_grammar',
]


class TerminalSet(nodes.Node):
    # For now this class is immutable, and can only handle terminals between 0
    # and 255 inclusive.

    def __init__(self, left=None, right=None):
        # Save ourselves some array allocations and copies if we can
        if left is None:
            self.bits = np.zeros(32, np.uint8)
        elif isinstance(left, str):
            bits = self.bits = np.zeros(32, np.uint8)

            for c in left:
                bits |= terminal_map()[ord(c)]
        else:
            self.bits = np.copy(left)

        if right is not None:
            self.bits |= right

    def derivative(self, terminal):
        if terminal in self:
            return nodes.epsilon
        else:
            return nodes.null

    def nullity(self):
        return nodes.null

    def regular(self):
        return True

    def terminate(self):
        return self.nullity()

    def negate(self):
        return TerminalSet(np.invert(self.bits))

    def get_chars(self):
        bits = self.bits
        chars = set()

        bm = bit_map()
        
        for i in range(256):
            if bits[i//8] & bm[i%8]:
                chars.add(chr(i))

        return ''.join(sorted(chars))

    def __contains__(self, c):
        if isinstance(c, str):
            c = ord(c)

        byte = self.bits[c // 8]

        return bool(bit_map()[c % 8] & byte)

    def __str__(self):
        return '[{}]'.format(self.get_chars())

    def __repr__(self):
        return "TerminalSet('{}')".format(self.get_chars())


@memoize
def bit_map():
    return { i : np.uint8(1 << i) for i in range(8) }


@memoize
def terminal_map():
    # TODO: Compact this

    bm = bit_map()

    terminal_map = { i : np.zeros(32, np.uint8) for i in range(256) }

    for i in range(256):
        terminal_map[i][i // 8] = bm[i % 8]

    return terminal_map

UnionBase = nodes.Union

class Union(UnionBase):
    def __new__(cls, left, right, *args, **kwargs):
        if isinstance(left, TerminalSet):
            if isinstance(right, TerminalSet):
                return TerminalSet(left.bits, right.bits)
            elif isinstance(right, Terminal):
                return TerminalSet(left.bits, terminal_map()[right.value])

        if isinstance(left, Terminal):
            if isinstance(right, TerminalSet):
                return TerminalSet(terminal_map()[left.value], right.bits)
            elif isinstance(right, Terminal):
                return TerminalSet(
                    terminal_map()[left.value],
                    terminal_map()[right.value],
                )

        return UnionBase.__new__(cls, left, right, *args, **kwargs)


# Cannot tell if this is insane or not
nodes.Union = Union


def terminal_set_grammar():
    left_bracket  = nodes.TerminalSet('[')
    right_bracket = ndoes.TerminalSet(']')
    back_slash   = nodes.TerminalSet('\\')
    carat = nodes.TerminalSet('^')
    hyphen = TerminalSet('-')


    slash_escape = nodes.Concat(back_slash, back_slash)
    right_escape = nodes.Concat(back_slash, right_bracket)

    escape = nodes.Union(
        slash_escape,
        right_escape,
    )

    carat_option = nodes.Union(carat, nodes.epsilon)
    hyphen_option = nodes.Union(carat, nodes.epsilon)

    range = Concat(nodes.dot, Concat(hyphen, nodes.dot))

    # left_bracket (carat)? (hyphen)? (range|escape|not_right_bracket)* right_bracket
