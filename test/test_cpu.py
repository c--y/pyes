# coding=utf-8
from cpu import Cpu
from nes import Machine


def test_cpu_init():
    c = Cpu(Machine())
    print c.__dict__

    c.set_carry(True)
    out1 = bin(c.p.value)
    print out1

    c.set_interrupt(True)
    out2 = bin(c.p.value)
    print out2

    c.test_and_set_negative(0x80)
    out4 = bin(c.p.value)
    print out4


def test_same_page():
    a1 = 0x3244
    a2 = 0x3256
    assert Cpu.same_page(a1, a2)

