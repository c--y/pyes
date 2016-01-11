# coding=utf-8

"""
6502 Cpu
"""
import functools
import types
from util import u8, u16, u8n, u16n, set_bit, bit


class Cpu(object):

    def __init__(self, machine):

        # machine
        self.machine = machine

        # shortcut
        self._m = self.machine.memory

        # program counter
        self.pc = u16()
        # stack pointer
        self.sp = u8()
        # accumulator
        self.acc = u8()

        # status
        # 0     1    2         3       4     5  6        7
        # Carry Zero Interrupt Decimal Break -  Overflow Negative
        self.p = u8()
        # x index
        self.x = u8()
        # y index
        self.y = u8()

        self.cycles = 0

        p_bit_map = {
            'carry': 0,
            'zero': 1,
            'interrupt': 2,
            'decimal': 3,
            'break': 4,
            'overflow': 6,
            'negative': 7
        }

        for k, v in p_bit_map.iteritems():
            self.__dict__[k] = types.MethodType(functools.partial(Cpu._p_test, i=v), self)
            self.__dict__['set_' + k] = types.MethodType(functools.partial(Cpu._p_set, i=v), self)
            self.__dict__['clear_' + k] = types.MethodType(functools.partial(Cpu._p_clear, i=v), self)


    @staticmethod
    def _p_test(obj, i=0):
        return bit(obj.p.value, i)

    @staticmethod
    def _p_set(obj, i=0):
        obj.p.value = set_bit(obj.p.value, i, True)

    @staticmethod
    def _p_clear(obj, i=0):
        obj.p.value = set_bit(obj.p.value, i, False)

    @staticmethod
    def same_page(a1, a2):
        return (a1 & 0xff00) == (a2 & 0xff00)

    #
    def am_implied(self):
        pass

    # A
    def am_accumulator(self):
        pass

    # am_* all return 16bit int
    # like #v
    def am_immediate(self):
        self.pc.value += 1
        return u16n(self.pc.value - 1)

    # d
    def am_zero_page(self):
        self.pc.value += 1
        return self._m.read(u16n(self.pc.value - 1))

    # d,x
    def am_zero_page_x(self):
        pass

    # d,y
    def am_zero_page_y(self):
        pass

    # label
    def am_relative(self):
        pass

    # a
    def am_absolute(self):
        high = self._m.read(u16n(self.pc.value + 1))
        low = self._m.read(self.pc.value)
        self.pc += 2


    # a,x
    def am_absolute_x(self):
        pass

    # a,y
    def am_absolute_y(self):
        pass

    # (a)
    def am_indirect(self):
        pass

    # (d,x)
    def am_indexed_indirect(self):
        pass

    # (d),y
    def am_indirect_indexed(self):
        pass



