from Payer import Proto;
from Payer.Language import *;
from Payer.Grammar import *;

__all__ = [
    'terminal_range', 'terminal_sequence'
];

globals().update(type_tags);

def terminal_range(low, high):
    return terminals(range(ord(low), ord(high) + 1));

def terminal_sequence(seq):
    return reduce(concat, (terminals([ord(x)]) for x in seq));

@Proto.decorate
def negate_terminals():
    r'''negate_terminals

        negate_terminals (Terminals f) = Terminals(f.transform(lambda v: not v));
    '''
def grammar():
    g = Grammar();

    g['lbracket'] = terminals([ord('[')]);
    g['rbracket'] = terminals([ord(']')]);
    g['bslash']   = terminals([ord('\\')]);
    g['hyphen']   = terminals([ord('-')]);
    g['lparen']   = terminals([ord('(')]);
    g['rparen']   = terminals([ord(')')]);
    g['pipe']     = terminals([ord('|')]);
    g['star']     = terminals([ord('*')]);

    g['special'] = reduce(union, map(g.__getitem__, [
        'lbracket', 'rbracket',
        'bslash',   'hyphen',
        'lparen',   'rparen', 'pipe', 'star',
    ]));

    g['non_special']     = negate_terminals(g['special']);
    g['escaped']         = concat(g['bslash'], g['special']);
    g['char']            = union(g['escaped'], g['non_special']);
    g['simple_range']    = reduce(concat, [ g['char'], g['hyphen'], g['char'] ]);
    g['char_class_atom'] = union(g['char'], g['simple_range']);
    g['char_class']      = reduce(concat, [ g['lbracket'], plus(g['char_class_atom']), g['rbracket'] ]);

    g['concat_atom']     = union(g['char'], g['char_class'])
    g['concat']          = plus(g['concat_atom'])
    g['union_sequence']  = sequence(g['concat'], g['pipe']);
    g['union']           = reduce(concat, [ g['lparen'], g['union_sequence'], g['rparen'] ]);
    g['repeat']          = concat(union(g['concat'], g['union']), g['star']);

    g['regular'] = plus(reduce(union, [ g['union'], g['concat'], g['repeat'] ]));

    return g;
