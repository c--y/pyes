# coding=utf-8


def bit(v, index):
    return (v & (1 << index)) > 0


def bit_all(v):
    return [bit(v, i) for i in xrange(8)]


def bits_to_int(bits):
    r = 0
    i = 0
    for b in bits:
        r += (1 << i) if b else 0
        i += 1
    return r


def set_bit(v, index, bv):
    return v | (1 << index)


def eq_seq(a, b):
    if len(a) != len(b):
        return False
    for i in xrange(len(a)):
        if a[i] != b[i]:
            return False
    return True