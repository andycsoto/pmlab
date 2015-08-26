__author__ = 'alcifuen'

import uuid
from general import ProcessTreeElement


class Variable(ProcessTreeElement):
    def __init__(self, id=uuid.uuid4(), name=str(id)):
        self.id = id
        self.name = name


class Expression(ProcessTreeElement):

    def __init__(self, uid=uuid.uuid4(), name=None, expression='', variables=set()):
        if name is None:
            name = str(uid)
        super(Expression, self).__init__(uid, name)
        self.expression = expression
        self.variables = variables

    def equals(self, o):
        if super(Expression, self.equals(o)):
            return True
        elif isinstance(o, Expression):
            return (self.getExpression().lower() == o.getExpression().lower()) and not Edge.NOEXPRESSION.equals(o)
        return False

    def get_expression(self):
        return self.expression

    def get_variables(self):
        return self.variables

    def add_variable(self, var):
        return self.variables.add(var)

    def remove_variable(self, var):
        return self.variables.discard(var)

    def __str__(self):
        return '['+self.expression+']'


class NOEXPRESSION(Expression):

    def __init__(self):
        super(NOEXPRESSION, self).__init__()
        self.uid = None
        self.name = ""
        self.variables = set()
        self.expression = ""

    def __str__(self):
        return ""

    def equals(self, o):
        return isinstance(o, Expression) and o.uid is None

    def add_variable(self, var):
        return False

    def remove_variable(self, var):
        return False


class Edge(ProcessTreeElement):

    NOEXPRESSION = Expression()

    def __init__(self, uid=uuid.uuid4(), source=None, target=None, expression=None, blockable=False, hideable=False):
        super(Edge, self).__init__(uid, source.name + " -> " + target.name())
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