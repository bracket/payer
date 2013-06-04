__all__ = [
    'TransitionPair', 'TransitionFunction',
    'indicator', 'merge'
];

class TransitionPair(object):
    def __init__(self, terminal, value):
        self.terminal = terminal;
        self.value = value;

    def __eq__(self, right):
        return self.terminal == right.terminal and self.value == right.value;

    def __lt__(self, right):
        if self.terminal < right.terminal: return True;
        if right.terminal < self.terminal: return False;

        return self.value < right.value;

    def __le__(self, right):
        if self.terminal < right.terminal: return True;
        if right.terminal < self.terminal: return False;

        return self.value <= right.value;

    def __repr__(self):
        return 'TransitionPair(%i, %s)' % (self.terminal, repr(self.value));

    def __str__(self):
        return '(%i, %s)' % (self.terminal, str(self.value));

class TransitionFunction(object):
    undef = object();

    def __init__(self, definition):
        self.definition = sorted(definition);

    def __call__(self, terminal):
        d = self.definition;
        low, high = 0, len(d);

        while low < high:
            mid = (low + high) / 2;
            if d[mid].terminal < terminal: low = mid + 1;
            else: high = mid;

        return d[low].value if 0 <= low < len(d) else self.undef;

    def __eq__(self, other):
        return self.definition == other.definition;

    def __repr__(self):
        return 'TransitionFunction(%s)' % str(self.definition);

    def __str__(self):
        return 'TransitionFunction([%s])' % ', '.join(map(str, self.definition));

    def compact(self):
        return TransitionFunction(self.__compact());

    @classmethod
    def from_items(cls, items):
        return cls(TransitionPair(*p) for p in items);

    def transform(self, xform):
        return TransitionFunction(TransitionPair(p.token, xform(p.value)) for p in self.definition);

    def __compact(self):
        seq = iter(self.definition);
        p = n = next(seq, None);

        while n is not None:
            n = next(seq, None);

            if n is None: yield p; p = n;
            elif p.value == n.value: p = n;
            else: yield p; p = n;

        if p is not None: yield p;

def merge(transitions, xform = lambda x : x):
    import itertools, inspect;
    ichain = itertools.chain.from_iterable;

    if inspect.isgenerator(transitions): transitions = list(transitions);
    terminals = sorted(set(ichain((p.terminal for p in f.definition) for f in transitions)));

    return TransitionFunction(
        xform(p) for p in (
            TransitionPair(t, tuple(f(t) for f in transitions))
            for t in terminals
        )
        if all(x is not TransitionFunction.undef for x in p.value)
    );

def __merge_consecutive(seq, S = lambda x : x + 1):
    seq, n = iter(seq), object();
    low = high = next(seq, n);
    while high is not n:
        x = next(seq, n);
        if x is n or S(high) < x:
            yield (low, high); low = high = x;
        else: high = x;

    if low is not n: yield (low, low);

def __indicator(X, max_terminal, xform):
    for low, high in __merge_consecutive(sorted(X)):
        yield TransitionPair(low - 1, xform(False));
        yield TransitionPair(high, xform(True));

    if high != max_terminal: yield TransitionPair(max_terminal, xform(False));

def indicator(X, max_terminal, xform = lambda x : x):
    return TransitionFunction(__indicator(X, max_terminal, xform));
