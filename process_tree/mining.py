__author__ = 'alcifuen'

import enum


class Cut:

    Operator = enum('Operator', 'xor sequence parallel loop')

    def __init__(self, Operator = None, partition = None):
        self.Operator = Operator
        self.partition = partition
    def isValid(self):
        if self.Operator == None and self.partition.size() <= 1:
            return False
        for part in self.partition:
            if part.size() == 0:
                return False
        return True

