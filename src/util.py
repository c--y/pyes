# coding=utf-8
import ctypes
import functools

# normalize a value
def nv(fn, v):
    return fn(v).value

u8 = ctypes.c_uint8
u16 = ctypes.c_uint16
u32 = ctypes.c_uint32
u64 = ctypes.c_uint64

u8n = functools.partial(nv, u8)
u16n = functools.partial(nv, u16)
u32n = functools.partial(nv, u32)
u64n = functools.partial(nv, u64)


def bit(v, index):
    return (v & (1 << index)) > 0


def bit_all(v):
    return [bit(v, i) for i in xrange(8)]


def bit_range(v, start, end):
    assert start >= 0 and end <= 7
    return [bit(v, i) for i in range(start, end+1)]


def bits_to_int(bits):
    r = 0
    i = 0
    for b in bits:
        r += (1 << i) if b else 0
        i += 1
    return r


def set_bit(v, index, bv):
    return v | (1 << index) if bv else v & (~(1 << index))


def eq_seq(a, b):
    if len(a) != len(b):
        return False
    for i in xrange(len(a)):
        if a[i] != b[i]:
            return False
    return True


def make_u16(hb, lb):
    return u16n(hb << 8 | lb)


def unpack_u16(val):
    return (val & 0xff00) >> 8, val & 0xff