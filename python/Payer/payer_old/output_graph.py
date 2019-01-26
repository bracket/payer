from Matcher import *;
from Payer.Lanugage import *;

globals().update(type_tags);

__all__ = [ 'OutputGraph' ];

class OutputGraph(object):
    def __init__(self, language):
        self.root = Node(language);
        self.remaining = [ self.root ];
        self.final = None;

    def derivative(self, x):
        remaining = list(self.remaining);
        self.remaining = [ ];

        for node in remaining:
            node.derivative(self, x);

    def finalize(self):
        self.final = [ ];
        for node in self.remaining:
            node.finalize(self);
        self.remaining = [ ];

class Node(object):
    def __init__(self, language, value = None):
        self.children = [ ];
        self.language = language;
        self.value = None;

    def derivative(self, graph, x):
        d = derivative(x, self.language);

        leaves = [ ];
        self.language = self.process_output_nodes(d, leaves);
        if self.language != Null(): graph.remaining.append(self);
        graph.remaining.extend(leaves);

    def finalize(self, graph):
        f = finalize(self.language);

        leaves = [ ];
        self.language = self.process_output_nodes(f, leaves);
        if self.language != Null(): graph.remaining.append(self);
        graph.final.extend(leaves);

    @MatcherMethod.decorate
    def process_output_nodes(add):
        @add(Union(var('Ls')), var('leaves'))
        def process_output_nodes(self, Ls, leaves):
            return reduce(union, (self.process_output_nodes(L, leaves) for L in Ls));

        @add(Concat(var('Ls')), var('leaves'))
        def process_output_nodes(self, Ls, leaves):
            new_leaves = [ ];
            remaining = self.process_output_nodes(Ls[0], new_leaves);
            tail = Ls[1] if len(Ls) == 2 else Concat(Ls[1:]);
            for leaf in new_leaves: leaf.language = concat(leaf.language, tail);
            leaves.extend(new_leaves);
            return concat(remaining, tail);

        @add(OutputNode(var('t'), var('L'), var('leaves'))
        def process_output_nodes(self, t, L, leaves):
            n = Node(L, t);
            self.children.append(n);
            n.process_output_nodes(L);
            return Null();

        @add(var('L'), var('leaves'))
        def process_output_nodes(self, L, leaves):
            if L != Null(): leaves.append(self);
            return L;
