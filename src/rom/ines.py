# coding=utf-8
import ctypes
from rom.cnrom import CNRom
from rom.mmc1 import Mmc1
from rom.mmc3 import Mmc3
from rom.nrom import NRom
from rom.unrom import UNRom
from util import bit, bit_all, bits_to_int, bit_range, eq_seq, u8, make_u16


HEADER_MAGIC = (0x4e, 0x45, 0x53)

# prg-rom 单位
BANK_SIZE_16K = 16384
# chr-rom 单位
BANK_SIZE_8K = 8192

MAPPER_MAP = {
    0x0: NRom,
    0x1: Mmc1,
    0x2: UNRom,
    0x3: CNRom,
    0x4: Mmc3
}


class INesRom(object):
    def __init__(self, option, trainer, prg_banks, chr_banks):
        self.option = option
        self.trainer = trainer
        self.prg_banks = prg_banks
        self.chr_banks = chr_banks

    def to_mapper(self):
        num = self.option.mapper_number()
        if num in MAPPER_MAP:
            return MAPPER_MAP[num](self)
        raise NotImplementedError('unsupported mapper')


class _HeaderOption(object):
    def __init__(self):
        self.prg_size = 0
        self.chr_size = 0
        self.prg_8k_size = 0

        # explain control options
        self.mirror_way = False
        # True = cartridge contains battery-backed prg ram(0x6000 - 0x7fff) or other persistent memory
        self.cart_battery_prg = False
        # True = 512 bytes trainer at 0x7000 - 0x71ff
        self.has_trainer = False
        self.lower_mapper_number = 0x0
        self.vs_unisystem = False
        self.play_choice_10 = False
        # if = 2, flags 8-15 are in nes2.0 format
        self.nes_ver = 0x0
        self.upper_mapper_number = 0x0
        # True = PAL, False = NTSC, flags9:0
        self.tv_system_1 = False
        # 0 = NTSC, 2 = PAL, 1|3 = dual compatible
        self.tv_system_2 = 0x0
        self.prg_ram_present = False
        self.bus_conflict = False

    def __repr__(self):
        return '_HeaderOption[]'

    def mapper_number(self):
        return make_u16(self.upper_mapper_number, self.lower_mapper_number)


def _parse_header(byte_array):
    data = map(ord, byte_array)
    magic = data[:3]
    if not eq_seq(magic, HEADER_MAGIC):
        raise

    o = _HeaderOption()
    o.prg_size = data[4]
    o.chr_size = data[5]
    flags_6 = data[6]
    flags_7 = data[7]
    o.prg_8k_size = data[8]
    flags_9 = data[9]
    flags_10 = data[10]
    # 11-15 zero filled

    # explain control options
    o.mirror_way = bit(flags_6, 0)
    o.cart_battery_prg = bit(flags_6, 1)
    o.has_trainer = bit(flags_6, 2)
    o.lower_mapper_number = bits_to_int(bit_range(flags_6, 4, 7))
    o.vs_unisystem = bit(flags_7, 0)
    o.play_choice_10 = bit(flags_7, 1)
    o.nes_ver = bits_to_int(bit_range(flags_7, 2, 3))
    o.upper_mapper_number = bits_to_int(bit_range(flags_7, 4, 7))
    o.tv_system_1 = bit(flags_9, 0)
    o.tv_system_2 = bits_to_int((bit_range(flags_10, 0, 1)))
    o.prg_ram_present = bit(flags_10, 4)
    o.bus_conflict = bit(flags_10, 5)
    return o


def _parse_ines(fd):
    i = 0
    header_option  = _parse_header(fd.read(16))
    trainer = fd.read(512) if header_option.has_trainer else None
    prg_rom = []
    for i in xrange(header_option.prg_size):
        prg_rom.append(map(ord, fd.read(16384)))
    chr_rom = []
    for i in xrange(header_option.chr_size):
        chr_rom.append(map(ord, fd.read(8192)))
    # TODO
    # play choice inst-rom, if present (0 or 8192 bytes)
    # play choice prom, if present (16 bytes data, 16 bytes counterout)

    return INesRom(header_option, trainer, prg_rom, chr_rom)


def read_ines(path):
    with open(path, 'rb') as f:
        ines_obj = _parse_ines(f)
        return ines_obj