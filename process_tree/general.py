__author__ = 'alcifuen'

import uuid


class ProcessTreeElement:
    id = None
    name = None

    def __init__(self, id, name):
        self.id = id
        self.name = name

    @classmethod
    def process_tree_element_from_id(cls, id):
        cls(id, str(id))

    @classmethod
    def process_tree_element_no_params(cls):
        cls.process_tree_element_from_id(uuid.uuid4())

    @classmethod
    def process_tree_element_from_id_pte(cls, id, pte):
        cls(id, pte.name)

    @classmethod
    def process_tree_element_from_pte(cls, pte):
        cls(pte.id, pte.name)

    def __str__(self):
        return self.name


class ProcessTree(ProcessTreeElement):
    nodes = None
    edges = None
    variables = None
    originators = None
    expressions = None
    root = None
    startIndex = None

    def __init__(self, id, name):
        super(ProcessTree, self).__init__(id, name)

    @classmethod
    def process_tree_no_params(cls):
        super(ProcessTree, cls).process_tree_element_no_params()

    @classmethod
    def process_tree_from_id(cls, id):
        super(ProcessTree, cls).process_tree_from_id(id)