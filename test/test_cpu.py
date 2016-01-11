# coding=utf-8
from cpu import Cpu


def test_cpu_init():
    c = Cpu(1)
    print c.__dict__

    c.set_carry()
    out = bin(c.p.value)
    print out

    c.set_interrupt()
    out = bin(c.p.value)
    print out

    c.clear_carry()
    out = bin(c.p.value)
    print out

test_cpu_init()
