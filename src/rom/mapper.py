# coding=utf-8


class Mapper(object):
    """
    Mapper interface
    """
    def read(self, a):
        raise NotImplemented()

    def write(self, a, v):
        raise NotImplemented()

    def read_vram(self, a):
        raise NotImplemented()

    def write_vram(self, a, v):
        raise NotImplemented()

    def read_tile(self):
        raise NotImplemented()

    def is_battery_backed(self):
        raise NotImplemented()
