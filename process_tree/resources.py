__author__ = 'alcifuen'

from general import ProcessTreeElement
from general import ProcessTree
import uuid


class Originator(ProcessTreeElement):

    def __init__(self, uid=None, name=None):
        if uid is None:
            uid = uuid.uuid4()
        if name is None:
            name = str(uid)
        super(Originator, self).__init__(uid, name)


class Resource(Originator):
    def __init__(self, uid=None, name=None):
        if uid is None:
            uid = uuid.uuid4()
        if name is None:
            name = str(uid)
        super(Resource, self).__init__(uid, name)


class Group(Originator):
    def __init__(self, uid=None, name=None):
        if uid is None:
            uid = uuid.uuid4()
        if name is None:
            name = str(uid)
        super(Group, self).__init__(uid, name)


class Role(Originator):
    def __init__(self, uid=None, name=None):
        if uid is None:
            uid = uuid.uuid4()
        if name is None:
            name = str(uid)
        super(Role, self).__init__(uid, name)