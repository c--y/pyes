# coding=utf-8
from rom.mapper import Mapper


class NRom(Mapper):

    def __init__(self, nes_rom):
        self.battery = nes_rom.option.cart_battery_prg
        self.prg_banks = nes_rom.prg_banks
        self.chr_banks = nes_rom.chr_banks

    def read(self, a):
        # 如果只有一个prg_banks,则0xc000~0xffff的访问是0x8000~0xbfff的mirror, 此时prg_banks[0] = prg_banks[-1]
        return self.prg_banks[0][a & 0x3fff] if a < 0xc000 else self.prg_banks[-1][a & 0x3fff]

    def write(self, a, v):
        pass

    def write_vram(self, a, v):
        return super(NRom, self).write_vram(a, v)

    def read_vram(self, a):
        return super(NRom, self).read_vram(a)

    def is_battery_backed(self):
        return self.battery

