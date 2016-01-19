r'''Proto is a mini-language used to translate case expressions into matcher objects.

Since it is used to define Payer it has to parse everything manually (or really, via Python regular expressions).
'''

__all__ = [
    'decorate',
    'generate_matcher',
]

import re, matcher

class ProtoException(Exception):
    pass

def build_tree_split_token_grammar():
    g            = { }

    g['ws']      = r'\s'
    g['var']     = r'[_a-z]+'
    g['type']    = r'[A-Z][_a-zA-Z0-9]*'

    g['digits']  = r'(?:[0-9]+)'
    g['sign']    = r'[-+]'
    g['integer'] = r'(?:{sign}?{digits})'.format(**g)

    literals = [ 'integer' ]
    g['literal'] = '|'.join('(?P<{}>{})'.format(name, g[name]) for name in literals)

    units = [ 'var', 'type', 'literal' ]
    g['unit'] = '|'.join('(?P<{}>{})'.format(name, g[name]) for name in units)

    g['lparen']  = r'\('
    g['rparen']  = r'\)'

    tokens = [ 'ws', 'unit', 'lparen', 'rparen' ]
    g['token'] = '|'.join('(?P<{}>{})'.format(name, g[name]) for name in tokens)

    for key, r in g.items():
        g[key] = re.compile(r)

    return g

split_tree_grammar = build_tree_split_token_grammar()


def tokenize(regex, text):
    start, end = 0, len(text)

    while start < end:
        match = regex.match(text, start)
        yield match
        start = match.end()


def tree_split(text):
    tree = [ ]
    stack = [ tree ]

    token_re = split_tree_grammar['token']

    for token in tokenize(token_re, text):
        if token is None:
            raise ProtoException('unable to split text into tree', { 'text' : text })

        if token.group('ws'):
            continue
        elif token.group('lparen'):
            stack[-1].append([])
            stack.append(stack[-1][-1])
        elif token.group('rparen'):
            stack.pop()
        elif token.group('unit'):
            stack[-1].append(token.group())

    if len(stack) != 1:
        raise ProtoException('unable to parse text into tree: %s' % text)

    return stack[0]


def format_pattern(term, ignore_vars = { }):
    return term[0], '({})'.format(' '.join('{},'.format(format_term(t)) for t in  term[1:]))


def format_term(term, ignore_vars = { }):
    if isinstance(term, list):
        return format_type(term)

    m = split_tree_grammar['unit'].match(term)

    if m.group('literal'):
        return m.group('literal')

    if m.group('type'):
        return '%s()' % m.group('type')

    if term == '_':
        return '_'
    else:
        return "var('%s')" % term


def format_type(term):
    args = map(format_term, term[1:])
    return '%s(%s)' % (term[0], ', '.join(args))


def generate_proto_cases(cases_text, global_ns, prefix_vars = [ ]):
    def_re = re.compile(r'\s*(?P<pattern>[^=]+?)\s*=\s*(?P<expr>.*)$')
    local_ns = { 'var' : matcher.var, '_' : matcher._ }

    for line_no, line in enumerate(cases_text.splitlines()):
        line = line.strip()
        if not line: continue

        m = def_re.match(line)
        if not m:
            raise ProtoException('unable to parse line {}: {}'.format(line_no, line.strip()))

        tree = tree_split(m.group('pattern'))
        name, pattern = format_pattern(tree_split(m.group('pattern')))

        pattern = eval(pattern, global_ns, { 'var' : matcher.var })
        vars = ', '.join(prefix_vars + list(matcher.get_placeholders(pattern).keys()))

        expr = m.group('expr')
        definition = 'def {name}({vars}): return {expr}'.format(name = name,  vars = vars, expr = expr)
        exec(definition, global_ns, local_ns)

        yield pattern, local_ns[name]


# TODO: Consolidate construction

def generate_matcher(name, cases_text, global_ns):
    m = matcher.Matcher(name)
    for pattern, function in generate_proto_cases(cases_text, global_ns):
        m.add(pattern, function)
    return m


def generate_matcher_method(name, cases_text, global_ns):
    m = matcher.MatcherMethod(name)

    for pattern, function in generate_proto_cases(cases_text, global_ns, prefix_vars = [ 'self' ]):
        m.add(pattern, function)

    return m


def generate_finder(name, cases_text, global_ns):
    m = matcher.Finder(name)
    for pattern, function in generate_proto_cases(cases_text, global_ns):
        m.add(pattern, function)
    return m


def generate_finder_method(name, cases_text, global_ns):
    m = matcher.FinderMethod(name)
    for pattern, function in generate_proto_cases(cases_text, global_ns, prefix_vars = [ 'self' ]):
        m.add(pattern, function)
    return m


def build_proto_doc_grammar():
    g = { }

    g['nl']         = r'(?:\r?\n)'
    g['firstline']  = r'\s*.*?{nl}'.format(**g)
    g['secondline'] = r'\s*{nl}'.format(**g)
    g['block']      = r'.*'.format(**g)
    g['doc']        = r'{firstline}{secondline}(?P<block>{block})'.format(**g)

    for key, r in g.items():
        g[key] = re.compile(r, re.MULTILINE | re.DOTALL)

    return g


proto_doc_grammar = build_proto_doc_grammar()


def decorate(function):
    m = proto_doc_grammar['doc'].match(function.__doc__)
    return generate_matcher(function.__name__, m.group('block'), function.__globals__)


def decorate_method(function):
    m = proto_doc_grammar['doc'].match(function.__doc__)
    return generate_matcher_method(function.__name__, m.group('block'), function.__globals__)


def decorate_finder(function):
    m = proto_doc_grammar['doc'].match(function.__doc__)
    return generate_finder(function.__name__, m.group('block'), function.__globals__)


def decorate_finder_method(function):
    m = proto_doc_grammar['doc'].match(function.__doc__)
    return generate_finder_method(function.__name__, m.group('block'), function.__globals__)
