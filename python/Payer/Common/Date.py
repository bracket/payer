from Payer.Language import *;
from Payer import Common;

cm = Common.languages;

__all__ = [ 'strptime', 'languages' ];

def _nrepeat(L, n):
    import itertools;
    return reduce(concat, itertools.repeat(L, n));

languages = LanguageSpace();

languages['%'] = terminals([ord('%')]);
languages['Y'] = _nrepeat(cm['digit'], 4);
languages['m'] = _nrepeat(cm['digit'], 2);
languages['d'] = _nrepeat(cm['digit'], 2);
languages['H'] = _nrepeat(cm['digit'], 2);
languages['M'] = _nrepeat(cm['digit'], 2);
languages['S'] = _nrepeat(cm['digit'], 2);

def strptime(fmt):
    def _derivative(space, terminal, output, language):
        if output == 'escape':
            return output_node(OutputNode(ref(chr(terminal))),
                space.derivative(terminal, language));
        elif output == 'terminal':
            return output_node(OutputNode(terminals([terminal])),
                space.derivative(terminal, language));

        return space.derivative(terminal, language);
    
    ls = LanguageSpace(_derivative);

    escapes = { ord('%') };
    escape_terminal = terminals(escapes);

    escape = concat(
        escape_terminal,
        output('escape', terminals(map(ord, '%YmdHMS')))
    );

    not_escape = output('terminal', terminals(all_terminals - escapes));

    L = repeat(union(escape, not_escape));
    for c in fmt: L = ls.derivative(ord(c), L);
    L = ls.finalize(L);

    out = next(get_outputs(L), None);
    if out: return reduce(concat, reversed(list(out)));
    else: return None;
