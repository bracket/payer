from . import nodes


class FlatConcat(nodes.Node):
    def __new__(cls, items, *args, **kwargs):
        if isinstance(items, FlatConcat):
            return items

        if not items:
            return nodes.null

        items = tuple(l for l in iter(items) if l is not nodes.epsilon)

        for l in items:
            if l is nodes.null:
                return nodes.null

        if not items:
            return nodes.epsilon

        if len(items) == 1:
            return items[0]

        out = nodes.Node.__new__(cls, *args, **kwargs)
        out.items = items

        return out

    def derivative(self, terminal):
        out = nodes.null

        for i, item in enumerate(self.items):
            d = item.derivative(terminal)

            out = nodes.Union(
                out,
                FlatConcat((d,) + self.items[i + 1:])
            )

            if item.nullity() is nodes.null:
                break

        return out

    def nullity(self):
        for l in self.items:
            if l.nullity() is nodes.null:
                return nodes.null

        return nodes.epsilon

    def regular(self):
        for l in self.items:
            if not l.regular():
                return False

        return True

    def terminate(self):
        return FlatConcat([ item.terminate() for item in self.items ])


    def __str__(self):
        return '({})'.format(''.join(str(l) for l in self.items))

    def __repr__(self):
        return  'FlatConcat({})'.format(repr(self.items))

    def __eq__(self, other):
        if not isinstance(other, FlatConcat):
            return False

        return self.items == other.items

    def __hash__(self):
        return hash(('flat_concat',) + tuple(self.items))


ConcatBase = nodes.Concat

class Concat(ConcatBase):
    def __new__(cls, left, right, *args, **kwargs):
        if isinstance(left, FlatConcat):
            if isinstance(right, FlatConcat):
                return FlatConcat(left.items + right.items)
            else:
                return FlatConcat(left.items + [ right ])
        elif isinstance(right, FlatConcat):
            return FlatConcat([ left ] + right.items)

        return FlatConcat([ left, right ])

nodes.Concat = Concat
