__all__ = [
    'TransitionFunction',
    'TransitionPair',
    'indicator',
    'merge',
]

class TransitionPair(object):
    def __init__(self, terminal, value):
        self.terminal = terminal
        self.value = value


    def __eq__(self, right):
        return self.terminal == right.terminal and self.value == right.value


    def __lt__(self, right):
        if self.terminal < right.terminal:
            return True

        if right.terminal < self.terminal:
            return False

        return self.value < right.value


    def __le__(self, right):
        if self.terminal < right.terminal:
            return True

        if right.terminal < self.terminal:
            return False

        return self.value <= right.value


    def __repr__(self):
        return 'TransitionPair(%i, %s)' % (self.terminal, repr(self.value))


    def __str__(self):
        return '(%i, %s)' % (self.terminal, str(self.value))


class TransitionFunction(object):
    undef = object()

    def __init__(self, definition):
        if isinstance(definition, TransitionFunction):
            self.definition = list(definition.definition)
        else:
            self.definition = sorted(definition)


    def __call__(self, terminal):
        definition = self.definition
        low, high = 0, len(definition)

        while low < high:
            mid = int((low + high) // 2)

            if definition[mid].terminal < terminal:
                low = mid + 1
            else:
                high = mid

        return definition[low].value if 0 <= low < len(definition) else self.undef


    def __eq__(self, other):
        return type(other) == TransitionFunction and self.definition == other.definition


    def __repr__(self):
        return 'TransitionFunction(%s)' % str(self.definition)


    def __str__(self):
        return 'TransitionFunction([%s])' % ', '.join(map(str, self.definition))


    def compact(self):
        return TransitionFunction(self._compact_pairs())


    @classmethod
    def from_items(cls, items):
        return cls(TransitionPair(*p) for p in items)


    def transform(self, xform):
        return TransitionFunction(TransitionPair(p.terminal, xform(p.value)) for p in self.definition)


    def _compact_pairs(self):
        seq = iter(self.definition)
        current = previous = next(seq, None)

        while current is not None:
            current = next(seq, None)

            if current is None:
                yield previous
                previous = current
            elif previous.value == current.value:
                previous = current
            else:
                yield previous
                previous = current

        if previous is not None:
            yield previous


def merge(transitions, xform = lambda x : x):
    import itertools, inspect
    ichain = itertools.chain.from_iterable

    if inspect.isgenerator(transitions):
        transitions = list(transitions)

    terminals = sorted(set(ichain((p.terminal for p in f.definition) for f in transitions)))

    return TransitionFunction(
        xform(p) for p in (
            TransitionPair(t, tuple(f(t) for f in transitions))
            for t in terminals
        )
        if all(x is not TransitionFunction.undef for x in p.value)
    )


def merge_consecutive(seq, S = lambda x : x + 1):
    undef = object()
    seq = iter(seq)

    low = high = next(seq, undef)

    while high is not undef:
        x = next(seq, undef)

        if x is undef or S(high) < x:
            yield (low, high)
            low = high = x
        else:
            high = x

    if low is not undef:
        yield (low, low)


def indicator_pairs(X, max_terminal, xform):
    for low, high in merge_consecutive(sorted(X)):
        yield TransitionPair(low - 1, xform(False))
        yield TransitionPair(high, xform(True))

    if high != max_terminal:
        yield TransitionPair(max_terminal, xform(False))


def indicator(terminals, max_terminal, xform = lambda x : x):
    return TransitionFunction(indicator_pairs(terminals, max_terminal, xform))
