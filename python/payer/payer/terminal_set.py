from .util import memoize
from . import nodes

from .nodes import Concat, Repeat

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
        if terminal.value in self:
            return nodes.epsilon
        else:
            return nodes.null

    def nullity(self):
        return nodes.null

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


class Union(nodes.Union):
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
                    temrinal_map()[right.value],
                )

        return super(cls).__new__(cls, left, right, *args, **kwargs)


# Cannot tell if this is insane or not
# No, if other classes try to inherit from nodes.Union before this happens.
nodes.Union = Union


def terminal_set_grammar():
    left_bracket  = TerminalSet('[')
    not_special = TerminalSet(r'\-[').negate()
    right_bracket = TerminalSet(']')

    return Concat(left_bracket, Concat(not_special, right_bracket))
