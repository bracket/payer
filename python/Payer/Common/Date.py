from Payer.Language import *;
from Payer import Common;

cm = Common.languages;

__all__ = [
    'strptime',
];

def _nrepeat(L, n):
    import itertools;
    return reduce(concat, itertools.repeat(L, n));

_strptime_map = {
    ord('%') : terminals([ord('%')]),
    ord('Y') : _nrepeat(cm['digit'], 4),
    ord('m') : _nrepeat(cm['digit'], 2),
    ord('d') : _nrepeat(cm['digit'], 2),
    ord('H') : _nrepeat(cm['digit'], 2),
    ord('M') : _nrepeat(cm['digit'], 2),
    ord('S') : _nrepeat(cm['digit'], 2),
};

def strptime(fmt):
    def _derivative(space, terminal, output, language):
        if output == 'escape':
            return output_node(OutputNode(_strptime_map[terminal]),
                space.derivative(terminal, language));
        elif output == 'terminal':
            return output_node(OutputNode(terminals([terminal])),
                space.derivative(terminal, language));

        return space.derivative(terminal, language);
    
    space = LanguageSpace(_derivative);

    escapes = { ord('%') };
    escape_terminal = terminals(escapes);

    escape = concat(
        escape_terminal,
        output('escape', terminals(_strptime_map.keys()))
    );

    not_escape = output('terminal', terminals(all_terminals - escapes));

    L = repeat(union(escape, not_escape));
    for c in fmt: L = space.derivative(ord(c), L);
    L = space.finalize(L);

    out = next(get_outputs(L), None);
    if out: return reduce(concat, reversed(list(out)));
    else: return None;
