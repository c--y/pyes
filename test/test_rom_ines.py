# coding=utf-8
from rom import ines


def test_read_ines():
    r = ines.read_ines('/Users/chenyan/py/pyes/test/nestest.nes')
    print r.__dict__
