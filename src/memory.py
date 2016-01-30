# coding=utf-8


class Memory(object):

    def __init__(self, machine):
        self.m = machine
        # 0x0000 ~ 0x1fff (0x800 bytes) physical internal ram
        self.cells = [0] * 0x10000

    def read(self, a):
        if 0x2008 <= a < 0x4000:
            # ppu memory
            # Mirror of 0x2000-0x2007
            return self.m.ppu.reg_read(0x2000 + (a % 0x8))

        elif 0x2000 <= a <= 0x2007:
            # ppu regs
            return self.m.ppu.reg_read(a)

        elif a == 0x4016:
            # pad[0]
            return self.m.pads[0].read()

        elif a == 0x4017:
            # pad[1]
            return self.m.pads[1].read()

        elif (a & 0xf000) == 0x4000:
            # apu reg
            # TODO
            return 0xff

        elif 0x8000 <= a <= 0xffff:
            # rom
            # (0x8000~0xbfff) + (0xc000~0xffff)
            return self.m.rom.read(a)

        elif 0x5100 <= a <= 0x6000:
            # mmc5
            pass

        else:
            return self.cells[a]

    def write(self, a, v):
        if 0x2000 <= a <= 0x2007:
            # write ppu regs
            self.m.ppu.reg_write(a, v)
        elif a == 0x4014:
            #
            self.m.ppu.reg_write(a, v)
            self.cells[a] = v

        elif a == 0x4016:
            self.m.pads[0].write(v)
            self.cells[a] = v

        elif a == 0x4017:
            self.m.pads[1].write(v)
            self.cells[a] = v
            # apu
            # self.m.apu.reg_write(a, v)

        elif (a & 0xf000) == 0x4000:
            # write apu
            # self.m.apu.reg_write(a, v)
            pass

        elif 0x8000 <= a <= 0xffff:
            # write rom
            self.m.rom.write(a, v)

        elif 0x5100 <= a <= 0x6000:
            # TODO mmc5
            self.cells[a] = v
        else:
            self.cells[a] = v
