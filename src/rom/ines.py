# coding=utf-8
import util
import ctypes

HEADER_MAGIC = (0x4e, 0x45, 0x53)


class INesObj(object):
    pass


class _HeaderOption(object):

    def __init__(self):
        self.prg_size = 0
        self.chr_size = 0
        self.prg_8k_size = 0


def _parse_header(bytes):
    magic = bytes[:3]
    if not util.eq_seq(magic, HEADER_MAGIC):
        raise
    prg_size = ctypes.c_uint8(bytes[4])
    chr_size = ctypes.c_uint8(bytes[5])
    flags_6 = ctypes.c_uint8(bytes[6])
    flags_7 = ctypes.c_uint8(bytes[7])
    prg_8k_size = ctypes.c_uint8(bytes[8])
    flags_9 = ctypes.c_uint8(bytes[9])
    flags_10 = ctypes.c_uint8(bytes[10])
    # 11-15 zero filled

    flags_6_bits = util.bit_all(flags_6)
    flags_7_bits = util.bit_all(flags_7)
    flags_9_bits = util.bit_all(flags_9)
    flags_10_bits = util.bit_all(flags_10)

    # explain control options





def _parse_ines(fd):
    i = 0
    header  = _parse_header(fd.read(16))




    return INesObj()


def read_ines(path):
    with open(path, 'rb') as f:
        ines_obj = _parse_ines(f)
        return ines_obj