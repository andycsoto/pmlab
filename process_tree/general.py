__author__ = 'alcifuen'

import uuid


class ProcessTreeElement(object):

    #This version doesn't use Properties
    #then, we don't need constructors based on other PTEs.
    def __init__(self, uid=uuid.uuid4(), name=None):
        if name is None:
            name = str(uid)
        self.uid = uid
        self.name = name

    def __str__(self):
        return self.name
        
    def equals(self, o):
        return o.uid if isinstance(o, ProcessTreeElement) else False
        
    def hash_code(self):
        return hash(self.uid)


class ProcessTree(ProcessTreeElement):

    def __init__(self, id=uuid.uuid4(), name=str(id)):
        super(ProcessTree, self).__init__(id, name)
        self.nodes = {}
        self.edges = set()
        self.variables = set()
        self.originators = []
        self.expressions = set()
        self.root = None
        self.start_index = 0

    #De la linea 201 en adelante (no pesques el constructor gigante).

    def add_node(self, node):
        if node in self.nodes:
            return False
        self.nodes[node] = self.start_index+1
        node.tree = self
        return True

    def add_edge(self, edge):
        self.edges.add(edge)
        
    def is_tree(self):
        return self.is_tree2(self, self.root, [False]*self.start_index)
        
    def is_tree2(self, node, visited):
        node_index = self.nodes[node]
        
        
