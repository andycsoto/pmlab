__author__ = 'alcifuen'

import uuid


class ProcessTreeElement:

    #This version doesn't use Properties
    #then, we don't need constructors based on other PTEs.
    def __init__(self, uid=uuid.uuid4(), name=None):
        if name is None:
            name = str(uid)
        self.uid = uid
        self.name = name

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

    def __init__(self, id=uuid.uuid4(), name=str(id)):
        super(ProcessTree, self).__init__(id, name)
