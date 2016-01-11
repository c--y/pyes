# coding=utf-8

"""
6502 Cpu
"""
import functools
import types
from util import u8, u16, u8n, u16n, set_bit, bit, make_u16


class Cpu(object):

    def __init__(self, machine):
        # machine
        self.machine = machine

        # cycles
        self.cycles = 0

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

    @staticmethod
    def _p_test(obj, i=0):
        return bit(obj.p.value, i)

    @staticmethod
    def _p_set(obj, v, i=0):
        obj.p.value = set_bit(obj.p.value, i, v)

    def test_and_set_zero(self, v):
        self.set_zero(v == 0)

    def test_and_set_negative(self, v):
        self.set_negative((v & 0x80) > 0)

    def test_and_set_carry_plus(self, v):
        self.set_carry(v > 0xff)

    # if v < 0, clear the carry bit.
    def test_and_set_carry_minus(self, v):
        self.set_carry(v >= 0x00)

    def test_and_set_overflow(self, v):
        self.set_overflow((v & 0x40) > 0)

    # 溢出情况: a + b + carry = c, (a, b)符号相同, (a, c)符号不同
    def test_and_set_overflow_plus(self, a, b):
        c = a + b + int(self.carry())
        self.set_overflow((((a ^ b) & 0x80) == 0) and (((a ^ c) & 0x80) > 0))

    # 溢出情况: a - b - carry = c, (a, b)符号不同, (a, c)符号不同
    def test_and_set_overflow_minus(self, a, b):
        c = a - b - int(self.carry())
        self.set_overflow((((a ^ b) & 0x80) > 0) and (((a ^ c) & 0x80) > 0))

    def reset_p(self):
        self.p.value = 0x34

    def push_stack(self, v):
        pass

    def pop_stack(self):
        return

    @staticmethod
    def same_page(a1, a2):
        return (a1 & 0xff00) == (a2 & 0xff00)

    def m_read(self, n):
        return self.machine.memory.read(n)

    def m_write(self, offset, v):
        self.machine.memory.write(offset, v)

    # ===== addressing mode =====
    def am_implied(self):
        return 0

    # A
    def am_accumulator(self):
        return 0

    # am_* all return 16bit int
    # like #v
    def am_immediate(self):
        self.pc.value += 1
        return u16n(self.pc.value - 1)

    # d
    def am_zero_page(self):
        self.pc.value += 1
        return self.m_read(u16n(self.pc.value - 1))

    def _am_zero_page_index(self, idx_val):
        address = self.m_read(self.pc.value)
        self.pc.value += 1
        return u16n(address + idx_val)

    # d,x
    def am_zero_page_x(self):
        return self._am_zero_page_index(self.x.value)

    # d,y
    def am_zero_page_y(self):
        return self._am_zero_page_index(self.y.value)

    # label
    def am_relative(self):
        a1 = self.m_read(self.pc.value)
        # a1: this value is signed, values #00-#7F are positive, and values #FF-#80 are negative
        a2 = u16n(self.pc.value + a1) if a1 < 0x80 else u16n(a1 + self.pc.value - 0x100)
        return a2 + 1

    # a
    def am_absolute(self):
        high = self.m_read(u16n(self.pc.value + 1))
        low = self.m_read(self.pc.value)
        self.pc.value += 2
        return make_u16(high, low)

    def _am_absolute_index(self, idx_val):
        high = self.m_read(u16n(self.pc.value + 1))
        low = self.m_read(self.pc.value)
        address = make_u16(high, low)
        address_idx = u16n(address + idx_val)
        # cross-page penalty
        self.cycles += 0 if Cpu.same_page(address, address_idx) else 1
        self.pc.value += 2
        return address_idx

    # a,x
    def am_absolute_x(self):
        return self._am_absolute_index(self.x.value)

    # a,y
    def am_absolute_y(self):
        return self._am_absolute_index(self.y.value)

    # (a)
    def am_indirect(self):
        high = self.m_read(u16n(self.pc.value + 1))
        low = self.m_read(self.pc.value)
        ah = make_u16(high, low)
        al = make_u16(high, u8n(low + 1))
        h_high = self.m_read(ah)
        l_low = self.m_read(al)
        make_u16(h_high, l_low)

    # (d,x)
    # Pre-indexed indirect
    def am_indexed_indirect(self):
        a1 = u16n(self.m_read(self.pc.value) + self.x.value)
        high = self.m_read(u16n(a1 + 1))
        low = self.m_read(a1)
        self.pc.value += 1
        return make_u16(high, low)

    # (d),y
    # Post-indexed indirect
    def am_indirect_indexed(self):
        a1 = self.m_read(self.pc.value)
        high = self.m_read(u16n(a1 + 1))
        low = self.m_read(a1)
        a2 = make_u16(high, low)
        a2_idx = u16n(a2 + self.y.value)
        # cross-page
        self.cycles += 0 if Cpu.same_page(a2, a2_idx) else 1
        self.pc.value += 1
        return a2_idx

    # ===== end of addressing mode =====

