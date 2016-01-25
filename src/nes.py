# coding=utf-8
"""
    General NES Hardware
    1. cpu
        6502 without decimal math
    2. 8kb internal memory
    3. up to 32kb external memory
    4. two joysticks
    5. ppu
        1) up to 16kb vram
    6. apu
"""
from cpu import Cpu
from ppu import Ppu
from memory import Memory
from control import JoyStick
from rom.ines import read_ines


class Machine(object):

    def __init__(self):
        self.cpu = Cpu(self)
        self.memory = Memory(self)
        self.ppu = Ppu(self)
        self.pads = [JoyStick(self), JoyStick(self)]
        self.rom = None

        self.total_cycles = 0

    def load_rom(self, file_path):
        nes_rom = read_ines(file_path)
        self.rom = nes_rom.to_mapper()


    def run(self):

        while True:
            cycles = self.cpu.step()
            self.total_cycles += cycles

            for i in xrange(3 * cycles):
                # self.ppu.step()
                pass

            for i in xrange(cycles):
                # self.apu.step()
                pass


M = Machine()