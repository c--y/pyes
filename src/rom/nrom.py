# coding=utf-8
from rom.mapper import Mapper


class NRom(Mapper):

    def __init__(self, nes_rom):
        self.battery = nes_rom.option.cart_battery_prg
        

    def read(self, a):


    def write(self, a, v):
        pass

    def write_vram(self, a, v):
        return super(NRom, self).write_vram(a, v)

    def read_vram(self, a):
        return super(NRom, self).read_vram(a)

    def is_battery_backed(self):
        return self.battery

