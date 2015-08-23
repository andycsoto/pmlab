__author__ = 'alcifuen'

from general import ProcessTreeElement
from general import ProcessTree
import uuid


class Originator(ProcessTreeElement):

    def __init__(self, uid=uuid.uuid4(), name=None):
        if name is None:
            name=str(uid)
        super(Originator).__init__(uid, name)


class Resource(Originator):
    def __init__(self, uid=uuid.uuid4(), name=None):
        if name is None:
            name=str(uid)
        super(Resource).__init__(uid, name)


class Group(Originator):
    def __init__(self, uid=uuid.uuid4(), name=None):
        if name is None:
            name=str(uid)
        super(Group).__init__(uid, name)


class Role(Originator):
    def __init__(self, uid=uuid.uuid4(), name=None):
        if name is None:
            name=str(uid)
        super(Role).__init__(uid, name)