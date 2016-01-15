# coding=utf-8


class Apu(object):

    def __init__(self, machine):
        self.m = machine

    def read(self, a):
        return 0

    def write(self, a, v):
        return 0
