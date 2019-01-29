__all__ = [
    'Concat',
    'Epsilon',
    'Node',
    'Null',
    'Terminal',
    'Union',
    'epsilon',
    'null',
]

class Node(object):
    pass


class Null(Node):
    def derivative(self, terminal):
        return null

    def nullity(self):
        return null

    def __str__(self):
        return 'Null'

    def __repr__(self):
        return 'Null()'

    def __eq__(self, other):
        return isinstance(other, Null)

    def __hash__(self):
        return hash('null')

null = Null()


class Epsilon(Node):
    def derivative(self, terminal):
        return null

    def nullity(self):
        return epsilon

    def __str__(self):
        return 'Epsilon'

    def __repr__(self):
        return 'Epsllon()'

    def __eq__(self, other):
        return isinstance(other, Epsilon)

    def __hash__(self):
        return hash('epsilon')
    
epsilon = Epsilon()
        

class Terminal(Node):
    def __init__(self, value):
        self.value = value

    def derivative(self, terminal):
        if self.value == terminal.value:
            return epsilon
        
        return null

    def nullity(self):
        return null

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return "Terminal('{}')".format(self.value)

    def __eq__(self, other):
        if not isinstance(other, Terminal):
            return False

        return self.value == other.value
    
    def __hash__(self):
        return hash(self.value)

    
class Concat(Node):
    def __new__(cls, left, right, *args, **kwargs):
        if isinstance(left, Null):
            return  null

        if isinstance(right, Null):
            return null

        if isinstance(left, Epsilon):
            return right

        if isinstance(right, Epsilon):
            return left

        return Node.__new__(cls, *args, **kwargs)

    def __init__(self, left, right):
        if isinstance(left, Concat):
            left, right = (
                left.left,
                Concat(left.right, right)
            )

        self.left = left
        self.right = right
    
    def derivative(self, terminal):
        return Union(
            Concat(
                self.left.derivative(terminal),
                self.right
            ),
            Concat(
                self.left.nullity(),
                self.right.derivative(terminal)
            )
        )

    def nullity(self):
        return Concat(
            self.left.nullity(),
            self.right.nullity(),
        )

    def __str__(self):
        return '({}{})'.format(str(self.left), str(self.right))

    def __repr__(self):
        return 'Concat({}, {})'.format(repr(self.left), repr(self.right))

    def __eq__(self, other):
        if not isinstance(other, Concat):
            return False

        return (self.left == other.left
                and self.right == other.right)
    
    def __hash__(self):
        return hash(('concat', self.left, self.right))


class Union(Node):
    def __new__(cls, left, right, *args, **kwargs):
        if isinstance(left, Null):
            return right

        if isinstance(right, Null):
            return left

        return Node.__new__(cls, *args, **kwargs)

    def __init__(self, left, right):
        if isinstance(left, Union):
            left, right = (
                left.left,
                Union(left.right, right)
            )

        self.left = left
        self.right = right

    def derivative(self, terminal):
        return Union(
            self.left.derivative(terminal),
            self.right.derivative(terminal),
        )

    def nullity(self):
        return Union(
            self.left.nullity(),
            self.right.nullity()
        )
    
    def __str__(self):
        return '({}|{})'.format(str(self.left), str(self.right))

    def __repr__(self):
        return 'Union({}, {})'.format(repr(self.left), repr(self.right))

    def __eq__(self, other):
        return (self.left == other.left
            and self.right == other.right)

    def __hash__(self):
        return hash(('union', self.left, self.right))
