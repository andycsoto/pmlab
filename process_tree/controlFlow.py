__author__ = 'alcifuen'

from general import ProcessTreeElement
from general import ProcessTree
import uuid


class Node(ProcessTreeElement):
    tree = None
    read_vars = None
    write_vars = None
    rem_read_vars = None
    rem_write_vars = None
    incoming = None

    def __init__(self, id, name, incoming):
        super(Node, self).__init__(id, name)
        self.read_vars = None
        self.write_vars = None
        self.rem_read_vars = None
        self.rem_write_vars = None
        self.incoming = incoming

    @classmethod
    def node_from_name_incoming(cls, name, incoming):
        cls(uuid.uuid4(), name, incoming)

    @classmethod
    def node_from_id_name(cls, id, name):
        cls(id, name, [])



class Edge(ProcessTreeElement):
    pass

class Task(Node):
    pass

class Automatic(Task):
    pass

class Manual(Task):
    pass

class Block(Node):
    pass

class XOR(Block):
    pass

class OR(Block):
    pass

class LoopXOR(Block):
    pass

class DEF(Block):
    pass

class AND(Block):
    pass

class SEQ(Block):
    pass

class LoopDEF(Block):
    pass

class PlaceHolder(Block):
    pass

class Event(Block):
    pass

class TimeOut(Event):
    pass

class Message(Event):
    pass