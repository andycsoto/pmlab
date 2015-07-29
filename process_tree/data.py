__author__ = 'alcifuen'

import uuid
from general import ProcessTreeElement
from controlFlow import Edge


class Variable(ProcessTreeElement):
    def __init__(self, id, name):
        self.id = id
        self.name = name

    @classmethod
    def variable_from_name(cls, name):
        super(Variable, cls.process_tree_element_from_name(name))

    @classmethod
    def variable_from_var(cls, var):
        super(Variable, cls.process_tree_element_from_pte(var))


class Expression(ProcessTreeElement):
    expression = ''
    variables = set()

    def __init__(self, e):
        super(Expression, self.process_tree_element_from_pte(e))
        self.expression = e.getExpression()
        self.variables = set()

    @classmethod
    def expression_from_parameters(cls, id, name, expression, variables):
        super(Expression, cls(id, name))
        cls.expression = expression
        cls.variables = set(variables)

    @classmethod
    def expression_from_id_expression_variables(cls, id, expression, variables):
        return cls.expression_from_parameters(id, str(id), expression, variables)

    @classmethod
    def expression_from_name_expression_variables(cls, name, expression, variables):
        return cls.expression_from_parameters(uuid.uuid4(), name, expression, variables)

    @classmethod
    def expression_from_expression_variables(cls, expression, variables):
        return cls.expression_from_id_expression_variables(uuid.uuid4(), expression, variables)

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
