__author__ = 'alcifuen'

from general import ProcessTreeElement
from general import ProcessTree


class Originator(ProcessTreeElement):
    @classmethod
    def variable_from_name(cls, name):
        super(Variable, cls.process_tree_element_from_name(name))

    @classmethod
    def variable_from_var(cls, var):
        super(Variable, cls.process_tree_element_from_pte(var))


class Resource(Originator):
    pass

class Group(Originator):
    pass

class Role(Originator):
    pass