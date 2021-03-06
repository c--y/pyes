# coding=utf-8
import util


def test_bit_all():
    v = 234
    r = util.bit_all(v)
    print r
    assert util.eq_seq(r, (False, True, False, True, False, True, True, True))


def test_bit_range():
    v = 234
    r = util.bit_range(v, 2, 5)
    print 'bit_range(234, 2, 5)=', r
    assert util.eq_seq(r, (False, True, False, True))


def test_bits_to_int():
    # 0b1101 = 13
    bits = (True, False, True, True)
    r = util.bits_to_int(bits)
    print r
    assert r == 13


def test_eq_seq():
    a = [1, 2, 3]
    b = (1, 2, 3)
    assert util.eq_seq(a, b)

    c = (1, 4, 5)
    assert not util.eq_seq(a, c)


def test_unpack_u16():
    x = 0x3344
    h, l = util.unpack_u16(x)
    print h, l
    assert h == 0x33
    assert l == 0x44
