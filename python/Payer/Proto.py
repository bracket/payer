r'''Proto is a mini-language used to translate case expressions into Matcher objects.

Since it is used to define Payer it has to parse everything manually (or really, via Python regular expressions).
'''

__all__ = [
    'decorate', 'generate_matcher',
];

import re, Matcher;

def build_tree_split_token_grammar():
    g           = { };

    g['var']    = r'[_a-z]+';
    g['type']   = r'[A-Z][_a-zA-Z0-9]*';
    g['unit']   = r'(?P<var>{var})|(?P<type>{type})'.format(**g);
    g['lparen'] = r'\(';
    g['rparen'] = r'\)';
    g['token']  = r'(?P<unit>{unit})|(?P<lparen>{lparen})|(?P<rparen>{rparen})'.format(**g);

    for key, r in g.iteritems(): g[key] = re.compile(r);
    return g;

split_tree_grammar = build_tree_split_token_grammar();

def tree_split(text):
    tree = [ ];
    stack = [ tree ];

    for token in split_tree_grammar['token'].finditer(text):
        if token.group('lparen'):
            stack[-1].append([]);
            stack.append(stack[-1][-1]);
        elif token.group('rparen'): stack.pop();
        else: stack[-1].append(token.group());

    if len(stack) != 1: raise Exception('unable to parse text into tree: %s' % text);
    return stack[0];

def format_pattern(term, ignore_vars = { }):
    return term[0], '({},)'.format(', '.join(map(format_term, term[1:])));

def format_term(term, ignore_vars = { }):
    if isinstance(term, list): return format_type(term);

    m = split_tree_grammar['unit'].match(term);
    if m.group('type'): return '%s()' % m.group('type');

    if term == '_': return '_';
    else: return "var('%s')" % term;

def format_type(term):
    args = map(format_term, term[1:])
    return '%s(%s)' % (term[0], ', '.join(args));

def generate_proto_cases(cases_text, global_ns, prefix_vars = [ ]):
    def_re = re.compile(r'\s*(?P<pattern>[^=]+?)\s*=\s*(?P<expr>.*);\s*$', re.MULTILINE);
    local_ns = { 'var' : Matcher.var, '_' : Matcher._ };

    for m in def_re.finditer(cases_text):
        name, pattern = format_pattern(tree_split(m.group('pattern')));

        pattern = eval(pattern, global_ns, { 'var' : Matcher.var });
        vars = ', '.join(prefix_vars + Matcher.get_placeholders(pattern).keys());

        expr = m.group('expr');
        definition = 'def {name}({vars}): return {expr};'.format(name = name,  vars = vars, expr = expr);
        exec definition in global_ns, local_ns;

        yield pattern, local_ns[name];

# TODO: Consolidate construction

def generate_matcher(name, cases_text, global_ns):
    m = Matcher.Matcher(name);
    for pattern, function in generate_proto_cases(cases_text, global_ns):
        m.add(pattern, function);
    return m;

def generate_matcher_method(name, cases_text, global_ns):
    m = Matcher.MatcherMethod(name);
    for pattern, function in generate_proto_cases(cases_text, global_ns, prefix_vars = [ 'self' ]):
        m.add(pattern, function);
    return m;

def generate_finder(name, cases_text, global_ns):
    m = Matcher.Finder(name);
    for pattern, function in generate_proto_cases(cases_text, global_ns):
        m.add(pattern, function);
    return m;

def generate_finder_method(name, cases_text, global_ns):
    m = Matcher.FinderMethod(name);
    for pattern, function in generate_proto_cases(cases_text, global_ns, prefix_vars = [ 'self' ]):
        m.add(pattern, function);
    return m;

def build_proto_doc_grammar():
    g = { };

    g['nl']         = r'(?:\r?\n)';
    g['firstline']  = r'\s*.*?{nl}'.format(**g);
    g['secondline'] = r'\s*{nl}'.format(**g);
    g['block']      = r'.*'.format(**g);
    g['doc']        = r'{firstline}{secondline}(?P<block>{block})'.format(**g);

    for key, r in g.iteritems(): g[key] = re.compile(r, re.MULTILINE | re.DOTALL);
    return g;

proto_doc_grammar = build_proto_doc_grammar();

def decorate(function):
    m = proto_doc_grammar['doc'].match(function.func_doc);
    return generate_matcher(function.__name__, m.group('block'), function.__globals__);

def decorate_method(function):
    m = proto_doc_grammar['doc'].match(function.func_doc);
    return generate_matcher_method(function.__name__, m.group('block'), function.__globals__);

def decorate_finder(function):
    m = proto_doc_grammar['doc'].match(function.func_doc);
    return generate_finder(function.__name__, m.group('block'), function.__globals__);

def decorate_finder_method(function):
    m = proto_doc_grammar['doc'].match(function.func_doc);
    return generate_finder_method(function.__name__, m.group('block'), function.__globals__);
