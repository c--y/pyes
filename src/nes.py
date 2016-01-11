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
from memory import Memory


class Machine(object):
    def __init__(self):
        self.cpu = Cpu(self)
        self.memory = Memory(self)


M = Machine()