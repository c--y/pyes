# coding=utf-8
import util


def test_bit_all():
    v = 234
    r = util.bit_all(v)
    print r
    assert util.eq_seq(r, (False, True, False, True, False, True, True, True))


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

