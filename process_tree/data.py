__author__ = 'alcifuen'

import uuid
from general import ProcessTreeElement
from control_flow import Edge


class Variable(ProcessTreeElement):
    def __init__(self, id=uuid.uuid4(), name=str(id)):
        self.id = id
        self.name = name


class Expression(ProcessTreeElement):

    def __init__(self, uid=uuid.uuid4(), name=None, expression='', variables=set()):
        if name is None:
            name = str(uid)
        super(Expression, self.__init__(self, uid, name))
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
        super(NOEXPRESSION, self.__init__())
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