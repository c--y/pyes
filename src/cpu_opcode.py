# coding=utf-8
from cpu import Cpu
from util import u8n, unpack_u16, make_u16

def test_overflow(b):
    return b > 0xff

opcodes_table = {}

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
        h, l = unpack_u16(c.pc.value)
        c.push_stack(h)
        c.push_stack(l)
        self.php(0)
        self.sei(0)

        c.set_interrupt(True)

        # read the irq interrupt vector
        h = c.m_read(0xffff)
        l = c.m_read(0xfffe)

        c.pc.value = make_u16(h, l)

    # branch if overflow clear
    def bvc(self, a):
        if not c.overflow():
            c.pc.value = a
            # TODO penalize
        else:
            c.pc.value += 1

    # branch if overflow set
    def bvs(self, a):
        if c.overflow():
            c.pc.value = a
            # TODO penalize
        else:
            c.pc.value += 1

    def clc(self, a):
        c.set_carry(False)

    def cld(self, a):
        c.set_decimal(False)

    def cli(self, a):
        c.set_interrupt(False)

    def clv(self, a):
        c.set_overflow(False)

    def _compare(self, a, b):
        c = a - b
        c.set_zero(c == 0)
        # FIXME ?
        c.set_negative(c < 0)
        c.test_and_set_carry_minus(c)

    # compare with acc
    def cmp(self, a):
        v = c.m_read(a)
        self._compare(c.acc.value, v)

    # compare with x
    def cpx(self, a):
        v = c.m_read(a)
        self._compare(c.x.value, v)

    # compare with y
    def cpy(self, a):
        v = c.m_read(a)
        self._compare(c.y.value, v)

    # dec memory value
    def dec(self, a):
        v = c.m_read(a)
        r = v - 1

        c.m_write(a, u8n(r))
        c.set_negative(r < 0)
        c.set_zero(r == 0)

    # dec x reg
    def dex(self, a):
        c.x.value -= 1
        c.set_zero(c.x.value == 0)
        c.test_and_set_negative(c.x.value)

    # dec y reg
    def dey(self, a):
        c.y.value -= 1
        c.set_zero(c.y.value == 0)
        c.test_and_set_negative(c.y.value)

    # exclusive or
    def eor(self, a):
        v = c.m_read(a)
        c.acc.value ^= v
        c.test_and_set_zero(c.acc.value)
        c.test_and_set_negative(c.acc.value)

    # inc memory value
    def inc(self, a):
        v = c.m_read(a)
        r = u8n(v + 1)

        c.m_write(a, r)
        c.test_and_set_negative(r)
        c.test_and_set_zero(r)

    def inx(self, a):
        c.x.value += 1
        c.test_and_set_negative(c.x.value)
        c.test_and_set_zero(c.x.value)

    def iny(self, a):
        c.y.value += 1
        c.test_and_set_negative(c.y.value)
        c.test_and_set_zero(c.y.value)

    def jmp(self, a):
        c.pc.value = a

    # jump to subroutine
    def jsr(self, a):
        h, l = unpack_u16(c.pc.value)
        c.push_stack(h)
        c.push_stack(l)
        c.pc.value = a

    # load acc
    def lda(self, a):
        v = c.m_read(a)
        c.acc.value = v

        c.test_and_set_negative(c.acc.value)
        c.test_and_set_zero(c.acc.value)

    # load x reg
    def ldx(self, a):
        v = c.m_read(a)
        c.x.value = v

        c.test_and_set_negative(c.x.value)
        c.test_and_set_zero(c.x.value)

    # load y reg
    def ldy(self, a):
        v = c.m_read(a)
        c.y.value = v

        c.test_and_set_negative(c.y.value)
        c.test_and_set_zero(c.y.value)

    # logic shift right
    def lsr(self, a):
        v = c.m_read(a)
        r = u8n(v >> 1)
        c.m_write(a, r)

        c.test_and_set_negative(r)
        c.test_and_set_zero(r)

    # lsr acc
    def lsr_acc(self):
        c.acc.value >>= 1
        c.test_and_set_negative(c.acc.value)
        c.test_and_set_zero(c.acc.value)

    def nop(self, a):
        pass

    # logic inclusive or
    def ora(self, a):
        v = c.m_read(a)
        r = u8n(c.acc.value | v)
        c.m_write(a, r)
        c.test_and_set_negative(r)
        c.test_and_set_zero(r)

    # push acc
    def pha(self):
        c.push_stack(c.acc.value)

    # push status register
    def php(self):
        c.push_stack(c.p.value)

    # pull acc
    def pla(self):
        c.acc.value = c.pop_stack()

    # pull status register
    def plp(self):
        c.p.value = c.pop_stack()

    # rotate left
    def rol(self, a):
        v = c.m_read(a)
        temp_carry = (v & 0x80) > 0
        v <<= 1
        v += 1 if c.carry() else 0
        c.set_carry(temp_carry)

        r = u8n(v)
        c.m_write(a, r)
        c.test_and_set_negative(r)
        c.test_and_set_zero(r)

    def rol_acc(self):
        temp_carry = (c.acc.value & 0x80) > 0
        c.acc.value <<= 1
        c.acc.value += 1 if c.carry() else 0
        c.set_carry(temp_carry)
        c.test_and_set_negative(c.acc.value)
        c.test_and_set_zero(c.acc.value)

    # rotate right
    def ror(self, a):
        v = c.m_read(a)
        temp_carry = (v & 0x1) > 0
        v >>= 1
        v += 0x80 if c.carry() else 0
        c.set_carry(temp_carry)

        r = u8n(v)
        c.m_write(a, r)
        c.test_and_set_negative(r)
        c.test_and_set_zero(r)

    def ror_acc(self):
        temp_carry = (c.acc.value & 0x1) > 0
        c.acc.value >>= 1
        c.acc.value += 0x80 if c.carry() else 0
        c.test_and_set_negative(c.acc.value)
        c.test_and_set_zero(c.acc.value)

    # return from interrupt
    def rti(self, a):
        self.plp()
        l = c.pop_stack()
        h = c.pop_stack()
        c.pc.value = make_u16(h, l)

    # return from subroutine
    def rts(self, a):
        l = c.pop_stack()
        h = c.pop_stack()
        c.pc.value = make_u16(h, l)

    # subtract with carry
    def sbc(self, a):
        v = c.m_read(a)
        temp = c.acc.value
        c.acc.value -= v

        carry_delta = 1 if c.carry() else 0
        c.acc -= 1 - carry_delta
        c.test_and_set_negative(c.acc.value)
        c.test_and_set_zero(c.acc.value)
        c.test_and_set_overflow_minus(temp, v)
        c.test_and_set_carry_minus(temp - v - 1 + int(c.carry()))

    # set carry
    def sec(self, a):
        c.set_carry(True)

    # set decimal
    def sed(self, a):
        c.set_decimal(True)

    # set interrupt
    def sei(self, a):
        c.set_interrupt(True)

    # store acc
    def sta(self, a):
        c.m_write(a, c.acc.value)

    # store x reg
    def stx(self, a):
        c.m_write(a, c.x.value)

    # store y reg
    def sty(self, a):
        c.m_write(a, c.y.value)

    # transfer acc t o x
    def tax(self, a):
        c.x.value = c.acc.value
        c.test_and_set_negative(c.x.value)
        c.test_and_set_zero(c.x.value)

    # transfer acc to y
    def tay(self, a):
        c.y.value = c.acc.value
        c.test_and_set_negative(c.y.value)
        c.test_and_set_zero(c.y.value)

    # transfer sp to x
    def tsx(self, a):
        c.x.value = c.sp.value
        c.test_and_set_negative(c.x.value)
        c.test_and_set_zero(c.x.value)

    # transfer x to acc
    def txa(self, a):
        c.acc.value = c.x.value
        c.test_and_set_negative(c.acc.value)
        c.test_and_set_zero(c.acc.value)

    # transfer x to acc
    def txs(self, a):
        c.sp.value = c.x.value

    # transfer y to acc
    def tya(self, a):
        c.acc.value = c.y.value
        c.test_and_set_negative(c.acc.value)
        c.test_and_set_zero(c.acc.value)

