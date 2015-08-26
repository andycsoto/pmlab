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
    nodes = None
    edges = None
    variables = None
    originators = None
    expressions = None
    root = None
    start_index = None

    def __init__(self, id=uuid.uuid4(), name=str(id)):
        super(ProcessTree, self).__init__(id, name)

    #De la linea 201 en adelante (no pesques el constructor gigante).

    def add_node(self, node):
        if node in self.nodes.keys:
            return False
        self.nodes[node] = self.start_index+1
        node.tree = self
        return True
        
    def is_tree(self):
        return is_tree2(self, self.root, [False]*self.start_index)
        
    def is_tree2(self, node, visited):
        node_index = self.nodes[node]
        
        
