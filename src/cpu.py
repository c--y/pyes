# coding=utf-8

"""
6502 Cpu
"""
import ctypes


class Cpu(object):

    def __init__(self, p):
        # program counter
        self.pc = ctypes.c_uint16()
        # stack pointer
        self.sp = ctypes.c_uint8()
        # accumulator
        self.acc = ctypes.c_uint8()

        # status
        self.p = ctypes.c_uint8()
        # x index
        self.x = ctypes.c_uint8()
        # y index
        self.y = ctypes.c_uint8()


