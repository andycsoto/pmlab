__author__ = 'alcifuen'

from general import ProcessTreeElement
import data
import uuid


class Node(ProcessTreeElement):

    def __init__(self, uid=uuid.uuid4(), name=None, incoming=[]):
        if name is None:
            name = str(uid)
        super(Node, self).__init__(uid, name)
        self.tree = None
        self.read_vars = set()
        self.write_vars = set()
        self.rem_read_vars = set()
        self.rem_write_vars = set()
        self.incoming = incoming

    def add_parent(self, parent, expression=Edge.NOEXPRESSION,  uid=uuid.uuid4()):
        e = Edge(uid, parent, self, expression)
        self.tree.add_edge(e)
        self.add_incoming_edge(e)
        self.read_vars.update(expression.variables)
        return e

    def add_incoming_edge(self, edge):
        if edge not in self.incoming:
            self.incoming.add(edge)

    def remove_incoming_edge(self, edge):
        return self.incoming.remove(edge)

    def get_parents(self):
        parents = []
        i = len(self.incoming)
        for x in range(i,0):
            parents[i] = self.incoming[i].source
        return parents

    def get_incoming_edges(self):
        return self.incoming

    def get_num_parents(self):
        return len(self.incoming)

    def __str__(self):
        return self.tree.__str__(self)


class Edge(ProcessTreeElement):

    NOEXPRESSION = data.Expression()

    def __init__(self, uid=uuid.uuid4(), source=None, target=None, expression=None, blockable=False, hideable=False):
        super(Edge).__init__(uid, source.name + " -> " + target.name())
        self.source = source
        self.target = target
        source.add_outgoing_edge(self)
        target.add_incoming_edge(self)
        self.expression = expression
        self.blockable = blockable
        self.hideable = hideable
        self.expressions = set()
        self.remExpressions = set()

    def is_blockable(self):
        return self.blockable

    def is_hideable(self):
        return self.hideable

    def __str__(self):
        return str(self.source) + " -> " + str(self.target)

    def has_expression(self):
        return not Edge.NOEXPRESSION.equals(self.expression)
    




