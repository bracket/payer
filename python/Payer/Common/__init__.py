from Payer.Language import *;
from Payer.Grammar import *;
from Payer.Regular import *;

__all__ = [
    'common_grammar',
];

def _negate(f):
	return f.transform(lambda v: not v);

def _make_quoted_string_def(quote_terminals):
    quotes = set(map(ord, quote_terminals));

    quote = terminals(quotes);
    not_quote = terminals(all_terminals - quotes);
    escape_terminal = terminals([ ord('\\') ]);
    escape = union(concat(escape_terminal, escape_terminal), concat(escape_terminal, quote));

    return reduce(concat, (quote, repeat(union(not_quote, escape)), quote));

def common_grammar():
    grammar = Grammar();

    grammar['lower_alpha'] = terminal_range('a', 'z');
    grammar['upper_alpha'] = terminal_range('A', 'Z');
    grammar['alpha'] = union(ref('lower_alpha'), ref('upper_alpha'));

    grammar['digit'] = terminal_range('0', '9');
    grammar['digits'] = plus(ref('digit'));
    grammar['hexdigit'] = reduce(union, (ref('digit'), terminal_range('a', 'f'), terminal_range('A', 'F')));

    grammar['alphanum'] = union(ref('alpha'), ref('digit'));

    grammar['underscore'] = terminals([ord('_')]);
    grammar['identifier'] = concat(union(ref('alpha'), ref('underscore')), repeat(union(ref('alphanum'), ref('underscore'))));

    grammar['space'] = terminals([ord(' ')]);
    grammar['whitespace'] = terminals(map(ord, ' \t\f'));
    grammar['newline'] = terminals([ord('\n')]);
    grammar['crlf'] = terminal_sequence('\r\n');
    grammar['universal_newline'] = union(ref('newline'), ref('crlf'));

    grammar['sign'] = terminals(map(ord, '-+'));
    grammar['integer'] = concat(optional(ref('sign')), plus(ref('digit')));
    grammar['exponent'] = concat(terminals(map(ord, 'eE')), ref('integer'));

    grammar['dot'] = terminals([ord('.')]);

    grammar['left_float'] = reduce(concat, (ref('integer'), ref('dot'), repeat(ref('digit')), optional(ref('exponent'))));
    grammar['right_float'] = reduce(concat, (ref('dot'), ref('digits'), optional(ref('exponent'))));
    grammar['float'] = union(ref('left_float'), ref('right_float'));

    grammar['single_quote'] = terminals([ord("'")]);
    grammar['double_quote'] = terminals([ord('"')]);

    grammar['single_quoted_string'] = _make_quoted_string_def("'");
    grammar['double_quoted_string'] = _make_quoted_string_def('"');

    grammar['lbrace'] = terminals([ ord('{') ]);
    grammar['rbrace'] = terminals([ ord('}') ]);
    grammar['lbracket'] = terminals([ ord('[') ]);
    grammar['rbracket'] = terminals([ ord(']') ]);
    grammar['langle'] = terminals([ ord('<') ]);
    grammar['rangle'] = terminals([ ord('>') ])

    return grammar;
