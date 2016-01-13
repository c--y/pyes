__author__ = 'chenyan'


class Memory(object):

    def __init__(self, machine):
        self.m = machine
        self.cells = [0] * 0x100000

    def read(self, a):
        if 0x2008 < a < 0x4000:
            # ppu memory
            pass
        elif 0x2000 <= a <= 0x2007:
            # ppu regs
            pass
        elif a == 0x4016:
            # pad[0]
            pass
        elif a == 0x4017:
            # pad[1]
            pass
        elif (a & 0xf000) == 0x4000:
            # apu reg
            pass
        elif 0x8000 <= a <= 0xffff:
            # rom
            pass
        elif 0x5100 <= a <= 0x6000:
            # mmc5
            pass
        else:
            return self.cells[a]

    def write(self, a, v):
        if 0x2000 <= a <= 0x2007:
            # write ppu regs
            pass
        elif a == 0x4014:
            #
            pass
        elif a == 0x4017:
            pass
        elif (a & 0xf000) == 0x4000:
            # write apu
            pass
        elif 0x8000 <= a <= 0xffff:
            # write rom
            pass
        elif 0x5100 <= a <= 0x6000:
            # mmc5
            pass
        else:
            self.cells[a] = v
