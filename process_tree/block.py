__author__ = 'alcifuen'
import control_flow as cf
import uuid
import data


class Block(cf.Node):

    def __init__(self, uid=None, name=None, incoming=None, outgoing=None):
        if uid is None:
            uid = uuid.uuid4()
        if name is None:
            name = str(uid)
        if incoming is None:
            incoming = []
        if outgoing is None:
            outgoing = []
        super(Block, self).__init__(uid, name, incoming)
        self.outgoing = outgoing
        self.changeable = False

    def get_read_variables_recursive(self):
        read_vars = set()
        read_vars.update(cf.Node.read_vars)
        for node in self.get_children():
            read_vars.update(node.get_read_variables_recursive(self))
        return read_vars

    def get_written_variables_recursive(self):
        write_vars = []
        write_vars.update(cf.Node.write_vars)
        for node in self.get_children():
            write_vars.update(node.get_written_variables_recursive(self))
        return write_vars

    def get_outgoing_edges(self):
        return tuple(self.outgoing)

    def add_outgoing_edge(self, edge):
        if edge not in self.outgoing:
            self.outgoing.append(edge)

    def remove_outgoing_edge(self, edge):
        self.outgoing.remove(edge)

    def add_outgoing_edge_at(self, edge, index):
        if edge in self.outgoing:
            self.outgoing.remove(edge)
        self.outgoing.insert(index, edge)

    def is_leaf(self):
        return False

    def add_child(self, child, expression=data.Edge.NOEXPRESSION):
        e = data.Edge(None, self, child, expression)
        self.tree.add_edge(e)
        self.add_outgoing_edge(e)
        self.read_vars.update(expression.variables)
        return e

    def add_child_at(self, child, index, expression=data.Edge.NOEXPRESSION):
        e = data.Edge(self, child, expression)
        self.tree.add_edge(e)
        self.add_outgoing_edge_at(e, index)
        return e

    #Original method has expression as a parameter and is not used
    def swap_child_at(self, child, index):
        e = self.get_outgoing_edges()[index]
        e.set_target(child)
        return e

    def get_children(self):
        children = cf.Node(len(self.outgoing))
        for i in range(1, len(self.outgoing)):
            children[i] = self.outgoing[i].get_target()
        return children

    #TODO
    def __iter__(self):
        pass

    def num_children(self):
        return len(self.outgoing)

    def __str__(self):
        return str(self.tree)


class XOR(Block):

    def __init__(self, uid=None, name=None, incoming=None, outgoing=None):
        if uid is None:
            uid = uuid.uuid4()
        if name is None:
            name = str(uid)
        if incoming is None:
            incoming = []
        if outgoing is None:
            outgoing = []
        super(XOR, self).__init__(uid, name, incoming, outgoing)
        
    def ordering_of_childern_matters(self):
        return True
        
    def expressions_of_outgoing_edges_matter(self):
        return True
        
    def __str__(self):
        return "Xor"


class OR(Block):
    
    def __init__(self, uid=None, name=None, incoming=None, outgoing=None):
        if uid is None:
            uid = uuid.uuid4()
        if name is None:
            name = str(uid)
        if incoming is None:
            incoming = []
        if outgoing is None:
            outgoing = []
        super(OR, self).__init__(uid, name, incoming, outgoing)
        
    def ordering_of_childern_matters(self):
        return True
        
    def expressions_of_outgoing_edges_matter(self):
        return True
        
    def __str__(self):
        return "Or"


class LoopXOR(Block):
    def __init__(self, uid=None, name=None, incoming=None, outgoing=None):
        if uid is None:
            uid = uuid.uuid4()
        if name is None:
            name = str(uid)
        if incoming is None:
            incoming = []
        if outgoing is None:
            outgoing = []
        super(LoopXOR, self).__init__(uid, name, incoming, outgoing)
        
    def ordering_of_childern_matters(self):
        return True
        
    def expressions_of_outgoing_edges_matter(self):
        return True
        
    def __str__(self):
        return "XorLoop"


class DEF(Block):
    def __init__(self, uid=None, name=None, incoming=None, outgoing=None):
        if uid is None:
            uid = uuid.uuid4()
        if name is None:
            name = str(uid)
        if incoming is None:
            incoming = []
        if outgoing is None:
            outgoing = []
        super(DEF, self).__init__(uid, name, incoming, outgoing)
        
    def ordering_of_childern_matters(self):
        return True
        
    def expressions_of_outgoing_edges_matter(self):
        return False
        
    def __str__(self):
        return "Def"


class AND(Block):
    def __init__(self, uid=None, name=None, incoming=None, outgoing=None):
        if uid is None:
            uid = uuid.uuid4()
        if name is None:
            name = str(uid)
        if incoming is None:
            incoming = []
        if outgoing is None:
            outgoing = []
        super(AND, self).__init__(uid, name, incoming, outgoing)
        
    def ordering_of_childern_matters(self):
        return False
        
    def expressions_of_outgoing_edges_matter(self):
        return False
        
    def __str__(self):
        return "And"


class SEQ(Block):
    def __init__(self, uid=None, name=None, incoming=None, outgoing=None):
        if uid is None:
            uid = uuid.uuid4()
        if name is None:
            name = str(uid)
        if incoming is None:
            incoming = []
        if outgoing is None:
            outgoing = []
        super(SEQ, self).__init__(uid, name, incoming, outgoing)
        
    def ordering_of_childern_matters(self):
        return True
        
    def expressions_of_outgoing_edges_matter(self):
        return False
        
    def __str__(self):
        return "Seq"


class LoopDEF(Block):
    def __init__(self, uid=None, name=None, incoming=None, outgoing=None):
        if uid is None:
            uid = uuid.uuid4()
        if name is None:
            name = str(uid)
        if incoming is None:
            incoming = []
        if outgoing is None:
            outgoing = []
        super(LoopDEF, self).__init__(uid, name, incoming, outgoing)
        
    def ordering_of_childern_matters(self):
        return True
        
    def expressions_of_outgoing_edges_matter(self):
        return False
        
    def __str__(self):
        return "DefLoop"


class PlaceHolder(Block):
    def __init__(self, uid=None, name=None, incoming=None, outgoing=None):
        if uid is None:
            uid = uuid.uuid4()
        if name is None:
            name = str(uid)
        if incoming is None:
            incoming = []
        if outgoing is None:
            outgoing = []
        super(PlaceHolder, self).__init__(uid, name, incoming, outgoing)
        
    def ordering_of_childern_matters(self):
        return False
        
    def expressions_of_outgoing_edges_matter(self):
        return True
        
    def __str__(self):
        return "P.H."


class Event(Block):
    def __init__(self, uid=None, name=None, message=None, incoming=None, outgoing=None):
        if uid is None:
            uid = uuid.uuid4()
        if name is None:
            name = str(uid)
        super(Event, self).__init__(uid, name)
        self.message = message
        self.add_incoming_edge(incoming)
        self.add_outgoing_edge(outgoing)
        
    def isChangeable(self):
        return False


class TimeOut(Event):
    def __init__(self, uid=None, name=None, message=None, incoming=None, outgoing=None):
        if uid is None:
            uid = uuid.uuid4()
        if name is None:
            name = str(uid)
        super(TimeOut, self).__init__(uid, name, message, incoming, outgoing)
        
    def ordering_of_childern_matters(self):
        return False
        
    def expressions_of_outgoing_edges_matter(self):
        return False
        
    def __str__(self):
        return "TimeOut"


class Message(Event):
    def __init__(self, uid=None, name=None, message=None, incoming=None, outgoing=None):
        if uid is None:
            uid = uuid.uuid4()
        if name is None:
            name = str(uid)
        super(TimeOut, self).__init__(uid, name, message, incoming, outgoing)
        
    def ordering_of_childern_matters(self):
        return False
        
    def expressions_of_outgoing_edges_matter(self):
        return False
        
    def __str__(self):
        return "Message"