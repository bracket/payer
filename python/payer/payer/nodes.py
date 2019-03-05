import traceback

__all__ = [
    'Concat',
    'Epsilon',
    'Node',
    'Null',
    'Output',
    'Repeat',
    'Terminal',
    'Union',
    'dot',
    'epsilon',
    'null',
]


regular_sentinel = object()


class Node(object):
    "Base Class representing one node in a grammar graph"

    # Class variable intended to overshadowed by instance variable
    regular_ = None


null = None

class Null(Node):
    "Node representing the empty language."

    def __new__(cls, *args, **kwargs):
        global null

        if null is None:
            null = Node.__new__(cls, *args, **kwargs)

        return null

    def derivative(self, terminal):
        return null

    def nullity(self):
        return null

    def regular(self):
        return True

    def terminate(self):
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


epsilon = None

class Epsilon(Node):
    "Node represnting the language consisting of only the empty string."

    def __new__(cls, *args, **kwargs):
        global epsilon

        if epsilon is None:
            epsilon = Node.__new__(cls, *args, **kwargs)

        return epsilon


    def derivative(self, terminal):
        return null

    def nullity(self):
        return epsilon

    def regular(self):
        return True

    def terminate(self):
        return epsilon

    def __str__(self):
        return 'Epsilon'

    def __repr__(self):
        return 'Epsilon()'

    def __eq__(self, other):
        return isinstance(other, Epsilon)

    def __hash__(self):
        return hash('epsilon')


epsilon  = Epsilon()


class Terminal(Node):
    "Node representing the language of a single string containing the terminal's value."

    def __new__(cls, value, *args, **kwargs):
        out = Node.__new__(cls, *args, **kwargs)
        out.value = value

        return out

    def derivative(self, terminal):
        if self.value == terminal:
            return epsilon
        
        return null

    def nullity(self):
        return null

    def regular(self):
        return True

    def terminate(self):
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


dot = None

class Dot(Node):
    "Node representing any Terminal"

    def __new__(cls, *args, **kwargs):
        global dot

        if dot is None:
            dot = Node.__new__(cls, *args, **kwargs)

        return dot
    
    def derivative(self, terminal):
        return epsilon
    
    def nullity(self):
        return null

    def regular(self):
        return True
    
    def terminate(self):
        return null

    def __str__(sef):
        return '.'
    
    def __repr__(self):
        return 'Dot()'

    def __eq__(self, other):
        return isinstance(other, Dot)

    def __hash__(self):
        return hash('dot')


dot = Dot()

    
class Concat(Node):
    r'''Node representing the concatenation of all strings in the left language
        with all strings right language.
    '''
    

    def __new__(cls, left, right, *args, **kwargs):
        if isinstance(left, Null):
            return null

        if isinstance(right, Null):
            return null

        if isinstance(left, Epsilon):
            return right

        if isinstance(right, Epsilon):
            return left

        out = Node.__new__(cls, *args, **kwargs)

        out.left = left
        out.right = right

        return out

    
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

    def regular(self):
        if self.regular_ is regular_sentinel:
            self.regular_ = False
        elif self.regular_ is None:
            self.regular_ = regular_sentinel

            self.regular_ = (self.left.regular()
                    and self.right.regular())

        return self.regular_

    def terminate(self):
        return Concat(
            self.left.terminate(),
            self.right.terminate()
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
    r'''Node represting the union of all strings in the left language with all
        strings in the left language.
    '''

    def __new__(cls, left, right, *args, **kwargs):
        if isinstance(left, Null):
            return right

        if isinstance(right, Null):
            return left

        if left == right:
            return left

        out =  Node.__new__(cls, *args, **kwargs)
        out.left = left
        out.right = right

        return out

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

    def regular(self):
        if self.regular_ is regular_sentinel:
            self.regular_ = False
        elif self.regular_ is None:
            self.regular_ = regular_sentinel

            self.regular_ = (self.left.regular()
                    and self.right.regular())

        return self.regular_

    def terminate(self):
        return Union(
            self.left.terminate(),
            self.right.terminate(),
        )

    def __str__(self):
        return '({}|{})'.format(str(self.left), str(self.right))

    def __repr__(self):
        return 'Union({}, {})'.format(repr(self.left), repr(self.right))

    def __eq__(self, other):
        if not isinstance(other, Union):
            return False

        return (self.left == other.left
            and self.right == other.right)

    def __hash__(self):
        return hash(('union', self.left, self.right))


class Repeat(Node):
    r'''Node representing the repetition of a language zero or more times.
    '''
    def __new__(cls, language, *args, **kwargs):
        if isinstance(language, Null):
            return null

        if isinstance(language, Epsilon):
            return epsilon

        out =  Node.__new__(cls, *args, **kwargs)
        out.language = language
            
        return out

    def derivative(self, terminal):
        return Concat(
            self.language.derivative(terminal),
            Repeat(self.language)
        )

    def nullity(self):
        return epsilon

    def regular(self):
        if self.regular_ is regular_sentinel:
            self.regular_ = False
        elif self.regular_ is None:
            self.regular_ = regular_sentinel

            self.regular_ = self.language.regular()

        return self.regular_

    def terminate(self):
        return self.language.terminate()

    def __str__(self):
        return '({})*'.format(str(self.language))

    def __repr__(self):
        return 'Repeat({})'.format(repr(self.language))

    def __eq__(self, other):
        if not isinstance(other, Repeat):
            return False

        return self.language == other.language

    def __hash__(self):
        return hash(('repeat', self.language))


class Output(Node):
    'Represents output symbol from a parse'

    def __new__(cls, symbol, language, *args, **kwargs):
        if language is null:
            return null

        out = Node.__new__(cls, *args, **kwargs)

        out.symbol = symbol
        out.language = language

        return out
    
    def derivative(self, terminal):
        return Output(self.symbol, self.language.derivative(terminal))
    
    def nullity(self):
        return self.language.nullity()

    def regular(self):
        return self.language.regular()

    def terminate(self):
        return Output(self.symbol, self.language.terminate())

    def __str__(self):
        return 'Output({}, {})'.format(repr(self.symbol), self.language)

    def __repr__(self):
        return 'Output({}, {})'.format(repr(self.symbol), repr(self.language))

    def __eq__(self, other):
        if not isinstance(other, Output):
            return False

        return (self.symbol == other.symbol
                and self.language == other.language)

    def __hash__(self):
        return (('output', self.symbol, self.language))

