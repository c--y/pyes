# coding=utf-8

from nes import Machine
import sys

def test_nestest():
    m = Machine()
    m.load_rom('nestest.nes')
    m.cpu.pc.value = 0xc000
    m.run()

f = open('nestest_tmp.log', 'w')
sys.stdout = f
test_nestest()