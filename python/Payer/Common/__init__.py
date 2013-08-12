from Payer.Language import *;

__all__ = [
    'terminal_range', 'terminal_sequence', 'languages',
];

#TOOD: These are probably more useful elsewhere

def terminal_range(low, high):
    return terminals(range(ord(low), ord(high) + 1));

def terminal_sequence(seq):
    return reduce(concat, (terminals([ord(x)]) for x in seq));

def _negate(f):
	return f.transform(lambda v: not v);

languages = LanguageSpace();

languages['lower_alpha'] = terminal_range('a', 'z');
languages['upper_alpha'] = terminal_range('A', 'Z');
languages['alpha'] = union(ref('lower_alpha'), ref('upper_alpha'));

languages['digit'] = terminal_range('0', '9');
languages['digits'] = plus(ref('digit'));
languages['hexdigit'] = reduce(union, (ref('digit'), terminal_range('a', 'f'), terminal_range('A', 'F')));

languages['alphanum'] = union(ref('alpha'), ref('digit'));

languages['underscore'] = terminals([ord('_')]);
languages['identifier'] = concat(union(ref('alpha'), ref('underscore')), repeat(union(ref('alphanum'), ref('underscore'))));

languages['space'] = terminals([ord(' ')]);
languages['whitespace'] = terminals(map(ord, ' \t\f'));
languages['newline'] = terminals([ord('\n')]);
languages['crlf'] = terminal_sequence('\r\n');
languages['universal_newline'] = union(ref('newline'), ref('crlf'));

languages['sign'] = terminals(map(ord, '-+'));
languages['integer'] = concat(optional(ref('sign')), plus(ref('digit')));
languages['exponent'] = concat(terminals(map(ord, 'eE')), ref('integer'));

languages['dot'] = terminals([ord('.')]);

languages['left_float'] = reduce(concat, (ref('integer'), ref('dot'), repeat(ref('digit')), optional(ref('exponent'))));
languages['right_float'] = reduce(concat, (ref('dot'), ref('digits'), optional(ref('exponent'))));
languages['floating'] = union(ref('left_float'), ref('right_float'));

languages['single_quote'] = terminals([ord("'")]);
languages['double_quote'] = terminals([ord('"')]);

def _make_quoted_string_def(quote_terminals):
    quotes = set(map(ord, quote_terminals));

    quote = terminals(quotes);
    not_quote = terminals(all_terminals - quotes);
    escape_terminal = terminals([ ord('\\') ]);
    escape = union(concat(escape_terminal, escape_terminal), concat(escape_terminal, quote));

    return reduce(concat, (quote, repeat(union(not_quote, escape)), quote));

languages['single_quoted_string'] = _make_quoted_string_def("'");
languages['double_quoted_string'] = _make_quoted_string_def('"');

languages['lbrace'] = terminals([ ord('{') ]);
languages['rbrace'] = terminals([ ord('}') ]);
languages['lbracket'] = terminals([ ord('[') ]);
languages['rbracket'] = terminals([ ord(']') ]);
languages['langle'] = terminals([ ord('<') ]);
languages['rangle'] = terminals([ ord('>') ])
