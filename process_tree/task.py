__author__ = 'alcifuen'
import control_flow as cf
import uuid


class Task(cf.Node):
    def __init__(self, uid=uuid.uuid4, name=None):
        if name is None:
            name=str(uid)
        super(Task, self).__init__(uid, name)
        
    def get_read_variables_recursive(self):
        read_vars = set()
        read_vars.update(cf.Node.read_vars)
        return read_vars
        
    def get_written_variables_recursive(self):
        write_vars = set()
        write_vars.update(cf.Node.write_vars)
        return write_vars
        
    def __str__(self):
        return self.name
        
    def is_leaf(self):
        return True


class Automatic(Task):
    def __init__(self, uid=uuid.uuid4, name=None):
        if name is None:
            name=str(uid)
        super(Automatic, self).__init__(uid, name)


class Manual(Task):
    def __init__(self, uid=uuid.uuid4, name=None, originators=list()):
        if name is None:
            name=str(uid)
        super(Manual, self).__init__(uid, name)
        self.originators=originators
        self.rem_originators=set()
        
    def add_originator(self, originator=None):
        return self.originators.append(originator)
        
    def add_removable_originator(self, removable_originator=None):
        return self.rem_originators.add(removable_originator)
        
    def remove_originator(self, originator=None):
        return self.originators.remove(originator)