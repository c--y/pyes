__author__ = 'chenyan'


class Memory(object):

    def __init__(self, machine):
        self.machine = machine
        self.cells = [0] * 0x100000

    def read(self, a):
        pass

    def write(self, a, v):
        pass
