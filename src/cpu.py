# coding=utf-8

"""
6502 Cpu
"""
import functools
import types
import asm
from util import u8, u16, u8n, u16n, set_bit, bit, make_u16, unpack_u16


# bin() = 0b110100
# interrupt = 1
# brk = 1
# - = 1
CPU_P_INIT = 0x24
CPU_SP_INIT = 0xFD
CPU_INT_NMI = 0x1
CPU_INT_IRQ = 0x2
CPU_INT_RESET = 0x3


class Cpu(object):

    def __init__(self, machine):
        # machine
        self.machine = machine

        # cycles
        self.cycles = 0

        # 当前指令执行时间
        self.wait_cycles = 0

        # program counter
        self.pc = u16()
        # stack pointer
        self.sp = u8(CPU_SP_INIT)
        # accumulator
        self.acc = u8()

        # status
        # 0     1    2         3       4     5  6        7
        # Carry Zero Interrupt Decimal Break -  Overflow Negative
        self.p = u8(CPU_P_INIT)
        # x index
        self.x = u8()
        # y index
        self.y = u8()

        # total cycles
        self.cycles = 0

        # wait cycles
        self.wait_cycles = 0

        # current interrupt
        self.current_interrupt = None

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

        # setup opcodes executor
        # key = bytecode, value = (function, addressing, cycles)
        self.opcodes = {
            0x00: (self.brk, self.am_implied, 7),
            0x01: (self.ora, self.am_indexed_indirect, 6),
            0x05: (self.ora, self.am_zero_page, 2),
            0x06: (self.asl, self.am_zero_page, 5),
            0x08: (self.php, self.am_implied, 3),
            0x09: (self.ora, self.am_immediate, 2),
            0x0a: (self.asl_acc, self.am_accumulator, 2),
            0x0d: (self.ora, self.am_absolute, 4),
            0x0e: (self.asl, self.am_absolute, 6),
            0x10: (self.bpl, self.am_relative, 2),
            0x11: (self.ora, self.am_indirect_indexed, 5),
            0x15: (self.ora, self.am_zero_page_x, 4),
            0x16: (self.asl, self.am_zero_page_x, 6),
            0x18: (self.clc, self.am_implied, 2),
            0x19: (self.ora, self.am_absolute_y, 4),
            0x1d: (self.ora, self.am_absolute_x, 4),
            0x1e: (self.asl, self.am_absolute_x, 7),
            0x20: (self.jsr, self.am_absolute, 6),
            0x21: (self.and_, self.am_indexed_indirect, 6),
            0x24: (self.bit, self.am_zero_page, 3),
            0x25: (self.and_, self.am_zero_page, 3),
            0x26: (self.rol, self.am_zero_page, 5),
            0x28: (self.plp, self.am_implied, 4),
            0x29: (self.and_, self.am_immediate, 2),
            0x2a: (self.rol_acc, self.am_accumulator, 2),
            0x2c: (self.bit, self.am_absolute, 4),
            0x2d: (self.and_, self.am_absolute, 4),
            0x2e: (self.rol, self.am_absolute, 6),
            0x30: (self.bmi, self.am_relative, 2),
            0x31: (self.and_, self.am_indirect_indexed, 5),
            0x35: (self.and_, self.am_zero_page_x, 4),
            0x36: (self.rol, self.am_zero_page_x, 6),
            0x38: (self.sec, self.am_implied, 2),
            0x39: (self.and_, self.am_absolute_y, 4),
            0x3d: (self.and_, self.am_absolute_x, 4),
            0x3e: (self.rol, self.am_absolute_x, 7),
            0x40: (self.rti, self.am_implied, 6),
            0x41: (self.eor, self.am_indexed_indirect, 6),
            0x45: (self.eor, self.am_zero_page, 3),
            0x46: (self.lsr, self.am_zero_page, 5),
            0x48: (self.pha, self.am_implied, 3),
            0x49: (self.eor, self.am_immediate, 2),
            0x4a: (self.lsr_acc, self.am_accumulator, 2),
            0x4c: (self.jmp, self.am_absolute, 3),
            0x4d: (self.eor, self.am_absolute, 4),
            0x4e: (self.lsr, self.am_absolute, 6),
            0x50: (self.bvc, self.am_relative, 2),
            0x51: (self.eor, self.am_indirect_indexed, 5),
            0x55: (self.eor, self.am_zero_page_x, 4),
            0x56: (self.lsr, self.am_zero_page_x, 6),
            0x58: (self.cli, self.am_implied, 2),
            0x59: (self.eor, self.am_absolute_y, 4),
            0x5d: (self.eor, self.am_absolute_x, 4),
            0x5e: (self.lsr, self.am_absolute_x, 7),
            0x60: (self.rts, self.am_implied, 6),
            0x61: (self.adc, self.am_indexed_indirect, 6),
            0x65: (self.adc, self.am_zero_page, 3),
            0x66: (self.ror, self.am_zero_page, 5),
            0x68: (self.pla, self.am_implied, 4),
            0x69: (self.adc, self.am_immediate, 2),
            0x6a: (self.ror_acc, self.am_accumulator, 2),
            0x6c: (self.jmp, self.am_indirect, 5),
            0x6d: (self.adc, self.am_absolute, 4),
            0x6e: (self.ror, self.am_absolute, 6),
            0x70: (self.bvs, self.am_relative, 2),
            0x71: (self.adc, self.am_indirect_indexed, 5),
            0x75: (self.adc, self.am_zero_page_x, 4),
            0x76: (self.ror, self.am_zero_page_x, 6),
            0x78: (self.sei, self.am_implied, 2),
            0x79: (self.adc, self.am_absolute_y, 4),
            0x7e: (self.ror, self.am_absolute_x, 7),
            0x81: (self.sta, self.am_indexed_indirect, 6),
            0x84: (self.sty, self.am_zero_page, 3),
            0x85: (self.sta, self.am_zero_page, 3),
            0x86: (self.stx, self.am_zero_page, 3),
            0x88: (self.dey, self.am_implied, 2),
            0x8a: (self.txa, self.am_implied, 2),
            0x8c: (self.sty, self.am_absolute, 4),
            0x8d: (self.sta, self.am_absolute, 4),
            0x8e: (self.stx, self.am_absolute, 4),
            0x90: (self.bcc, self.am_relative, 2),
            0x91: (self.sta, self.am_indirect_indexed, 6),
            0x94: (self.sty, self.am_zero_page_x, 4),
            0x95: (self.sta, self.am_zero_page_x, 4),
            0x96: (self.stx, self.am_zero_page_y, 4),
            0x98: (self.tya, self.am_implied, 2),
            0x99: (self.sta, self.am_absolute_y, 5),
            0x9a: (self.txs, self.am_implied, 2),
            0x9d: (self.sta, self.am_absolute_x, 5),
            0xa0: (self.ldy, self.am_immediate, 2),
            0xa1: (self.lda, self.am_indexed_indirect, 6),
            0xa2: (self.ldx, self.am_immediate, 2),
            0xa4: (self.ldy, self.am_zero_page, 3),
            0xa5: (self.lda, self.am_zero_page, 3),
            0xa6: (self.ldx, self.am_zero_page, 3),
            0xa8: (self.tay, self.am_implied, 2),
            0xa9: (self.lda, self.am_immediate, 2),
            0xaa: (self.tax, self.am_implied, 2),
            0xac: (self.ldy, self.am_absolute, 4),
            0xad: (self.lda, self.am_absolute, 4),
            0xae: (self.ldx, self.am_absolute, 4),
            0xb0: (self.bcs, self.am_relative, 2),
            0xb1: (self.lda, self.am_indirect_indexed, 5),
            0xb4: (self.ldy, self.am_zero_page_x, 4),
            0xb5: (self.lda, self.am_zero_page_x, 4),
            0xb6: (self.ldx, self.am_zero_page_y, 4),
            0xb8: (self.clv, self.am_implied, 2),
            0xb9: (self.lda, self.am_absolute_y, 4),
            0xba: (self.tsx, self.am_implied, 2),
            0xbc: (self.ldy, self.am_absolute_x, 4),
            0xbd: (self.lda, self.am_absolute_x, 4),
            0xbe: (self.ldx, self.am_absolute_y, 4),
            0xc0: (self.cpy, self.am_immediate, 2),
            0xc1: (self.cmp, self.am_indexed_indirect, 2),
            0xc4: (self.cpy, self.am_zero_page, 3),
            0xc5: (self.cmp, self.am_zero_page, 3),
            0xc6: (self.dec, self.am_zero_page, 5),
            0xc8: (self.iny, self.am_implied, 2),
            0xc9: (self.cmp, self.am_immediate, 2),
            0xca: (self.dex, self.am_implied, 2),
            0xcc: (self.cpy, self.am_absolute, 4),
            0xcd: (self.cmp, self.am_absolute, 4),
            0xce: (self.dec, self.am_absolute, 6),
            0xd0: (self.bne, self.am_relative, 2),
            0xd1: (self.cmp, self.am_indirect_indexed, 5),
            0xd5: (self.cmp, self.am_zero_page_x, 4),
            0xd6: (self.dec, self.am_zero_page_x, 6),
            0xd8: (self.cld, self.am_implied, 2),
            0xd9: (self.cmp, self.am_absolute_y, 4),
            0xdd: (self.cmp, self.am_absolute_x, 4),
            0xde: (self.dec, self.am_absolute_x, 7),
            0xe0: (self.cpx, self.am_immediate, 2),
            0xe1: (self.sbc, self.am_indexed_indirect, 6),
            0xe4: (self.cpx, self.am_zero_page, 3),
            0xe5: (self.sbc, self.am_zero_page, 3),
            0xe6: (self.inc, self.am_zero_page, 5),
            0xe8: (self.inx, self.am_implied, 2),
            0xe9: (self.sbc, self.am_immediate, 2),
            0xea: (self.nop, self.am_implied, 2),
            0xeb: (self.cpx, self.am_absolute, 4),
            0xed: (self.sbc, self.am_absolute, 4),
            0xf0: (self.beq, self.am_relative, 2),
            0xf1: (self.sbc, self.am_indirect_indexed, 5),
            0xf5: (self.sbc, self.am_zero_page_x, 4),
            0xf6: (self.inc, self.am_zero_page_x, 6),
            0xf8: (self.sed, self.am_implied, 2),
            0xf9: (self.sbc, self.am_absolute_y, 4),
            0xfd: (self.sbc, self.am_absolute_x, 4),
            0xfe: (self.inc, self.am_absolute_x, 7)
        }

    def info(self):
        return 'A:%.2X X:%.2X Y:%.2X P:%.2X SP:%.2X' % \
               (self.acc.value, self.x.value, self.y.value, self.p.value, self.sp.value)

    def eval_bytecode(self, code):
        if code not in self.opcodes:
            raise Exception('illegal bytecode')

        fn, address_fn, cycles = self.opcodes[code]
        address = address_fn()
        # 如果address为None,则寻址方式是Implied或是Immediate, 则相应的执行函数不使用函数
        if address is not None:
            fn(address)
        else:
            fn()
        return cycles

    def step(self):
        """
        One run
        :return:
        """
        # nmi
        if self.wait_cycles > 0:
            self.wait_cycles -= 1
            return 1

        if self.current_interrupt:
            if self.current_interrupt == CPU_INT_NMI:
                self.nmi()
            elif self.current_interrupt == CPU_INT_IRQ:
                self.irq()
            elif self.current_interrupt == CPU_INT_RESET:
                self.reset()
            self.current_interrupt = None

        # read-eval-loop
        bytecode = self.m_read(self.pc.value)
        self.pc.value += 1
        print asm.dis(bytecode, self, self.pc.value), self.info()
        return self.eval_bytecode(bytecode)

    def nmi(self):
        pass

    def irq(self):
        h, l = unpack_u16(self.pc)
        self.push_stack(h)
        self.push_stack(l)
        self.push_stack()

    def reset(self):
        pass

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
        """
        stack: 0x100 - 0x1ff
        see: http://wiki.nesdev.com/w/index.php/Stack
        :param v:
        :return:
        """
        self.m_write(u16n(0x100 + self.sp.value), v)
        self.sp.value -= 1

    def pop_stack(self):
        self.sp.value += 1
        v = self.m_read(u16n(0x100 + self.sp.value))
        return v

    def load_reset_vector(self):
        h = self.m.m_read(0xfffd)
        l = self.m.m_read(0xfffc)
        self.pc = make_u16(h, l)

    @staticmethod
    def same_page(a1, a2):
        return (a1 & 0xff00) == (a2 & 0xff00)

    def m_read(self, n):
        return self.machine.memory.read(n)

    def m_write(self, offset, v):
        self.machine.memory.write(offset, v)

    def penalise_branch(self, a):
        """
        判定pc地址和地址a, 是否在同一个内存页.如果不在同一页,cycles多加1
        :param a:
        :return:
        """
        self.cycles += 2 if not Cpu.same_page(self.pc.value - 1, a) else 1

    # ===== addressing mode =====
    def am_implied(self):
        return None

    # A
    def am_accumulator(self):
        return None

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

    # ===== instructions ======
    def adc(self, a):
        v = self.m_read(a)
        r = v + self.acc.value + int(self.carry())
        self.test_and_set_zero(u8n(r))
        self.test_and_set_negative(u8n(r))
        self.test_and_set_carry_plus(r)
        self.test_and_set_overflow_plus(self.acc.value, v)
        self.acc.value = r

    def and_(self, a):
        v = self.m_read(a)
        self.acc.value = v & self.acc.value
        self.test_and_set_negative(self.acc.value)
        self.test_and_set_zero(self.acc.value)

    def asl(self, a):
        v = self.m_read(a)
        self.set_carry((v & 0x80) > 0)
        s_v = u8n(v << 1)
        self.m_write(a, s_v)
        self.test_and_set_negative(s_v)
        self.test_and_set_zero(s_v)

    def asl_acc(self):
        # a always equals 0
        self.set_carray((self.acc.value & 0x80) > 0)
        self.acc.value <<= 1
        self.test_and_set_negative(self.acc.value)
        self.test_and_set_zero(self.acc.value)

    def bcc(self, a):
        if not self.carry():
            self.pc.value = a
            self.penalise_branch(a)
        else:
            self.pc.value += 1

    def bcs(self, a):
        if self.carry():
            self.pc.value = a
            self.penalise_branch(a)
        else:
            self.pc.value += 1

    # branch is equal
    def beq(self, a):
        if self.zero():
            self.pc.value = a
            self.penalise_branch(a)
        else:
            self.pc.value += 1

    def bit(self, a):
        v = self.m_read(a)
        r = self.acc.value & v
        self.test_and_set_zero(r)
        self.test_and_set_negative(v)
        self.test_and_set_overflow(v)

    # branch if minus
    def bmi(self, a):
        if self.negative():
            self.pc.value = a
            self.penalise_branch(a)
        else:
            self.pc.value += 1

    # branch if not equal
    def bne(self, a):
        if not self.zero():
            self.pc.value = a
            self.penalise_branch(a)
        else:
            self.pc.value += 1

    # branch if positive
    def bpl(self, a):
        if not self.negative():
            self.pc.value = a
            self.penalise_branch(a)
        else:
            self.pc.value += 1

    # force interrupt

    # The BRK instruction forces the generation of an interrupt request.
    # The program counter and processor status are pushed on the stack
    #  then the IRQ interrupt vector at $FFFE/F is loaded into the PC and the break flag
    #  in the status set to one.
    #
    # 1. Push address of BRK instruction + 2
    # 2. PHP
    # 3. SEI
    # 4. JMP ($FFFE)
    #
    def brk(self):
        self.pc.value += 1
        h, l = unpack_u16(self.pc.value)
        self.push_stack(h)
        self.push_stack(l)
        self.php()
        self.sei()

        self.set_interrupt(True)

        # read the irq interrupt vector
        h = self.m_read(0xffff)
        l = self.m_read(0xfffe)

        self.pc.value = make_u16(h, l)

    # branch if overflow clear
    def bvc(self, a):
        if not self.overflow():
            self.pc.value = a
            self.penalise_branch(a)
        else:
            self.pc.value += 1

    # branch if overflow set
    def bvs(self, a):
        if self.overflow():
            self.pc.value = a
            self.penalise_branch(a)
        else:
            self.pc.value += 1

    def clc(self):
        self.set_carry(False)

    def cld(self):
        self.set_decimal(False)

    def cli(self):
        self.set_interrupt(False)

    def clv(self):
        self.set_overflow(False)

    def _compare(self, a, b):
        c = a - b
        self.set_zero(c == 0)
        # FIXME ?
        self.test_and_set_negative(c)
        self.test_and_set_carry_minus(c)

    # compare with acc
    def cmp(self, a):
        v = self.m_read(a)
        self._compare(self.acc.value, v)

    # compare with x
    def cpx(self, a):
        v = self.m_read(a)
        self._compare(self.x.value, v)

    # compare with y
    def cpy(self, a):
        v = self.m_read(a)
        self._compare(self.y.value, v)

    # dec memory value
    def dec(self, a):
        v = self.m_read(a)
        r = v - 1

        self.m_write(a, u8n(r))
        self.set_negative(r < 0)
        self.set_zero(r == 0)

    # dec x reg
    def dex(self):
        self.x.value -= 1
        self.set_zero(self.x.value == 0)
        self.test_and_set_negative(self.x.value)

    # dec y reg
    def dey(self):
        self.y.value -= 1
        self.set_zero(self.y.value == 0)
        self.test_and_set_negative(self.y.value)

    # exclusive or
    def eor(self, a):
        v = self.m_read(a)
        self.acc.value ^= v
        self.test_and_set_zero(self.acc.value)
        self.test_and_set_negative(self.acc.value)

    # inc memory value
    def inc(self, a):
        v = self.m_read(a)
        r = u8n(v + 1)

        self.m_write(a, r)
        self.test_and_set_negative(r)
        self.test_and_set_zero(r)

    def inx(self):
        self.x.value += 1
        self.test_and_set_negative(self.x.value)
        self.test_and_set_zero(self.x.value)

    def iny(self):
        self.y.value += 1
        self.test_and_set_negative(self.y.value)
        self.test_and_set_zero(self.y.value)

    def jmp(self, a):
        self.pc.value = a

    # jump to subroutine
    def jsr(self, a):
        h, l = unpack_u16(self.pc.value)
        self.push_stack(h)
        self.push_stack(l)
        self.pc.value = a

    # load acc
    def lda(self, a):
        v = self.m_read(a)
        self.acc.value = v

        self.test_and_set_negative(self.acc.value)
        self.test_and_set_zero(self.acc.value)

    # load x reg
    def ldx(self, a):
        v = self.m_read(a)
        self.x.value = v

        self.test_and_set_negative(self.x.value)
        self.test_and_set_zero(self.x.value)

    # load y reg
    def ldy(self, a):
        v = self.m_read(a)
        self.y.value = v

        self.test_and_set_negative(self.y.value)
        self.test_and_set_zero(self.y.value)

    # logic shift right
    def lsr(self, a):
        v = self.m_read(a)
        r = u8n(v >> 1)
        self.m_write(a, r)

        self.test_and_set_negative(r)
        self.test_and_set_zero(r)

    # lsr acc
    def lsr_acc(self):
        self.acc.value >>= 1
        self.test_and_set_negative(self.acc.value)
        self.test_and_set_zero(self.acc.value)

    def nop(self):
        pass

    # logic inclusive or
    def ora(self, a):
        v = self.m_read(a)
        r = u8n(self.acc.value | v)
        self.acc.value = r
        self.test_and_set_negative(r)
        self.test_and_set_zero(r)

    # push acc
    def pha(self):
        self.push_stack(self.acc.value)

    # push status register
    def php(self):
        self.push_stack(self.p.value | 0x10)

    # pull acc
    def pla(self):
        self.acc.value = self.pop_stack()
        self.test_and_set_zero(self.acc.value)
        self.test_and_set_negative(self.acc.value)

    # pull status register
    def plp(self):
        self.p.value = self.pop_stack()
        # unset bit 5
        self.p.value = (self.p.value | 0x30) - 0x10

    # rotate left
    def rol(self, a):
        v = self.m_read(a)
        temp_carry = (v & 0x80) > 0
        v <<= 1
        v += 1 if self.carry() else 0
        self.set_carry(temp_carry)

        r = u8n(v)
        self.m_write(a, r)
        self.test_and_set_negative(r)
        self.test_and_set_zero(r)

    def rol_acc(self):
        temp_carry = (self.acc.value & 0x80) > 0
        self.acc.value <<= 1
        self.acc.value += 1 if self.carry() else 0
        self.set_carry(temp_carry)
        self.test_and_set_negative(self.acc.value)
        self.test_and_set_zero(self.acc.value)

    # rotate right
    def ror(self, a):
        v = self.m_read(a)
        temp_carry = (v & 0x1) > 0
        v >>= 1
        v += 0x80 if self.carry() else 0
        self.set_carry(temp_carry)

        r = u8n(v)
        self.m_write(a, r)
        self.test_and_set_negative(r)
        self.test_and_set_zero(r)

    def ror_acc(self):
        temp_carry = (self.acc.value & 0x1) > 0
        self.acc.value >>= 1
        self.acc.value += 0x80 if self.carry() else 0
        self.test_and_set_negative(self.acc.value)
        self.test_and_set_zero(self.acc.value)

    # return from interrupt
    def rti(self):
        self.plp()
        l = self.pop_stack()
        h = self.pop_stack()
        self.pc.value = make_u16(h, l)

    # return from subroutine
    def rts(self):
        l = self.pop_stack()
        h = self.pop_stack()
        self.pc.value = make_u16(h, l)

    # subtract with carry
    def sbc(self, a):
        v = self.m_read(a)
        temp = self.acc.value
        self.acc.value -= v

        carry_delta = 1 if self.carry() else 0
        self.acc.value -= (1 - carry_delta)
        self.test_and_set_negative(self.acc.value)
        self.test_and_set_zero(self.acc.value)
        self.test_and_set_overflow_minus(temp, v)
        self.test_and_set_carry_minus(temp - v - 1 + int(self.carry()))

    # set carry
    def sec(self):
        self.set_carry(True)

    # set decimal
    def sed(self):
        self.set_decimal(True)

    # set interrupt
    def sei(self):
        self.set_interrupt(True)

    # store acc
    def sta(self, a):
        self.m_write(a, self.acc.value)

    # store x reg
    def stx(self, a):
        self.m_write(a, self.x.value)

    # store y reg
    def sty(self, a):
        self.m_write(a, self.y.value)

    # transfer acc t o x
    def tax(self):
        self.x.value = self.acc.value
        self.test_and_set_negative(self.x.value)
        self.test_and_set_zero(self.x.value)

    # transfer acc to y
    def tay(self):
        self.y.value = self.acc.value
        self.test_and_set_negative(self.y.value)
        self.test_and_set_zero(self.y.value)

    # transfer sp to x
    def tsx(self):
        self.x.value = self.sp.value
        self.test_and_set_negative(self.x.value)
        self.test_and_set_zero(self.x.value)

    # transfer x to acc
    def txa(self):
        self.acc.value = self.x.value
        self.test_and_set_negative(self.acc.value)
        self.test_and_set_zero(self.acc.value)

    # transfer x to acc
    def txs(self):
        self.sp.value = self.x.value

    # transfer y to acc
    def tya(self):
        self.acc.value = self.y.value
        self.test_and_set_negative(self.acc.value)
        self.test_and_set_zero(self.acc.value)
