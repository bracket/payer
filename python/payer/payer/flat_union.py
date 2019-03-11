from . import nodes

class FlatUnion(nodes.Node):
    def __new__(cls, items, *args, **kwargs):
        if isinstance(items, FlatUnion):
            return items
        
        if not items:
            return nodes.null

        items = frozenset(l for l in iter(items) if l is not nodes.null)

        if not items:
            return nodes.null

        if len(items) == 1:
            return next(iter(items))

        out = nodes.Node.__new__(cls, *args, **kwargs)
        out.items = items

        return out

    def derivative(self, terminal):
        return FlatUnion([
            l.derivative(terminal) for l in self.items
        ])

    def nullity(self):
        for node in self.items:
            if node.nullity() is nodes.epsilon:
                return nodes.epsilon

        return nodes.null

    def regular(self):
        for l in self.items:
            if not l.regular():
                return False

        return True

    def terminate(self):
        return FlatUnion([ l.terminate() for l in self.items ])

    def __str__(self):
        return '({})'.format('|'.join(str(l) for l in self.items))

    def __repr__(self):
        return 'FlatUnion({})'.format(repr(self.items))

    def __eq__(self, other):
        if not isinstance(other, FlatUnion):
            return False

        return self.items == other.items

    def __hash__(self):
        return (('flat_union',) + frozenset(self.items))

UnionBase = nodes.Union

class Union(UnionBase):
    def __new__(cls, left, right, *args, **kwargs):
        if isinstance(left, FlatUnion):
            if isinstance(right, FlatUnion):
                return FlatUnion(left.items | right.items)
            else:
                return FlatUnion(left.items | frozenset([ right ]))
        elif isinstance(right, FlatUnion):
            return FlatUnion(frozenset([ left ]) | right.items)
        
        return FlatUnion([ left, right ])

nodes.Union = Union
