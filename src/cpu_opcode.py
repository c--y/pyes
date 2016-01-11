# coding=utf-8
from cpu import Cpu
from util import u8n

def test_overflow(b):
    return b > 0xff

c = Cpu(None)

class OpcodesMixin(object):

    def adc(self, a):
        v = c.m_read(a)
        r = v + c.acc.value + int(c.carry())
        c.test_and_set_zero(u8n(r))
        c.test_and_set_negative(u8n(r))
        c.test_and_set_carry_plus(r)
        c.test_and_set_overflow_plus(c.acc.value, v)
        c.acc.value = r

    def and_(self, a):
        v = c.m_read(a)
        c.acc.value = v & c.acc.value
        c.test_and_set_negative(c.acc.value)
        c.test_and_set_zero(c.acc.value)

    def asl(self, a):
        v = c.m_read(a)
        c.set_carry((v & 0x80) > 0)
        s_v = u8n(v << 1)
        c.m_write(a, s_v)
        c.test_and_set_negative(s_v)
        c.test_and_set_zero(s_v)

    def asl_acc(self, a):
        # a always equals 0
        c.set_carray((c.acc.value & 0x80) > 0)
        c.acc.value <<= 1
        c.test_and_set_negative(c.acc.value)
        c.test_and_set_zero(c.acc.value)

    def bcc(self, a):
        if not c.carry():
            c.pc.value = a
            # TODO penalize branch cycles
        else:
            c.pc.value += 1

    def bcs(self, a):
        if c.carry():
            c.pc.value = a
            # TODO penalise branch cycles
        else:
            c.pc.value += 1

    # branch is equal
    def beq(self, a):
        if c.zero():
            c.pc.value = a
            # TODO penalise branch cycles
        else:
            c.pc.value += 1

    def bit(self, a):
        v = c.m_read(a)
        r = u8n(c.acc.value & v)
        c.test_and_set_zero(r)
        c.test_and_set_negative(r)
        c.test_and_set_overflow(r)

    # branch if minus
    def bmi(self, a):
        if c.negative():
            c.pc.value = a
            # TODO penalise branch cycles
        else:
            c.pc.value += 1

    # branch if not equal
    def bne(self, a):
        if not c.zero():
            c.pc.value = a
            # TODO penalise branch cycles
        else:
            c.pc.value += 1

    # branch if positive
    def bpl(self, a):
        if not c.negative():
            c.pc.value = a
            # TODO penalise branch cycles
        else:
            c.pc.value += 1

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
    def brk(self, a):
        c.pc.value += 1

    def bvs(self, a):
        pass

    def clc(self, a):
        pass

    def cld(self, a):
        pass

    def cli(self, a):
        pass

    def clv(self, a):
        pass

    def cmp(self, a):
        pass

    def cpx(self, a):
        pass

    def cpy(self, a):
        pass

    def dec(self, a):
        pass

    def dex(self, a):
        pass

    def dey(self, a):
        pass

    def eor(self, a):
        pass

    def inc(self, a):
        pass

    def inx(self, a):
        pass

    def iny(self, a):
        pass

    def jmp(self, a):
        pass

    def jsr(self, a):
        pass

    def lda(self, a):
        pass

    def ldx(self, a):
        pass

    def ldy(self, a):
        pass

    def lsr(self, a):
        pass

    def nop(self, a):
        pass

    def ora(self, a):
        pass

    def pha(self, a):
        pass

    def php(self, a):
        pass

    def pla(self, a):
        pass

    def plp(self, a):
        pass

    def rol(self, a):
        pass

    def ror(self, a):
        pass

    def rti(self, a):
        pass

    def rts(self, a):
        pass

    def sbc(self, a):
        pass

    def sec(self, a):
        pass

    def sed(self, a):
        pass

    def sei(self, a):
        pass

    def sta(self, a):
        pass

    def stx(self, a):
        pass

    def sty(self, a):
        pass

    def tax(self, a):
        pass

    def tay(self, a):
        pass

    def tsx(self, a):
        pass

    def txa(self, a):
        pass

    def txs(self, a):
        pass

    def tya(self, a):
        pass
