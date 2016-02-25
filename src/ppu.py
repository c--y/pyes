# coding=utf-8
import functools
from util import bit_range, bits_to_int, bit, u8, set_bit


def _setter(obj, b, idx = 0):
    obj.v.value = set_bit(obj.v.value, idx, b)


def _getter(obj, idx = 0):
    return bit(obj.v.value, idx)


class _RCtrl(object):
    """
    0x2000
    bits: (7-0) VPHB SINN
    """
    def __init__(self):
        self.v = u8()

        bit_map = {
            # 0: add 1, going across; 1: add 32,going down.
            'vram_increment': 2,
            # pt = pattern table
            # 0 : 0x1000; 1: 0x1000. ignored in 8*16 mode
            'sprite_pt_address': 3,
            # 0 : 0x000; 1: 0x1000.
            'background_pt_address': 4,
            # 0 : 8*8; 1 : 8*16.
            'sprite_size': 5,
            # 0 : read backdrop from ext pins; 1 : output color on ext pins.
            'master_slave': 6,
            # 0 : off; 1 : on. generate an NMI at the start of the vertical blanking interval.
            'nmi_vblank': 7
        }

        for k, v in bit_map.iteritems():
            self.__dict__['get_' + k] = functools.partial(_getter, idx=v)
            self.__dict__['set_' + k] = functools.partial(_setter, idx=v)

    def set_v(self, val):
        self.v.value = val

    def get_name_table_address(self):
        return bits_to_int(bit_range(self.v.value, 0, 1))

    def set_name_table_address(self, a):
        self.v.value = (self.v.value | 0x3) & (a & 0x3)


class _RMask(object):
    """
    0x2001
    bits: (7-0) BGRs bMmG
    """
    def __init__(self):
        self.v = u8()
        bit_map = {
            'gray_scale': 0,
            'show_background_left': 1,
            'show_sprites_left': 2,
            'show_background': 3,
            'show_sprites': 4,
            'emphasize_red': 5,
            'emphasize_green': 6,
            'emphasize_blue': 7
        }

        for k, v in bit_map.iteritems():
            self.__dict__['get_' + k] = functools.partial(_getter, idx=v)
            self.__dict__['set_' + k] = functools.partial(_setter, idx=v)

    def set_v(self, val):
        self.v.value = val


class _RStatus(object):
    """
    0x2002
    """
    def __init__(self):
        self.v = u8()

        bit_map = {
           'sprite_overflow': 5,
           'sprite_0_hit': 6,
           'vblank_in': 7
        }

        for k, v in bit_map.iteritems():
            self.__dict__['get_' + k] = functools.partial(_getter, idx=v)
            self.__dict__['set_' + k] = functools.partial(_setter, idx=v)

    def set_v(self, val):
        self.v.value = val


class OamSprite(object):
    def __init__(self, four_bytes):
        assert len(four_bytes) == 4
        self.bytes = four_bytes
        self.y = four_bytes[0]
        self.tile_index = four_bytes[1]
        attr = four_bytes[2]
        # palette(4 to 7) of sprite
        self.palette = bits_to_int(bit_range(attr, 0, 1))
        # 0: in front of background; 1: behind background
        self.priority = bit(attr, 5)
        # flip sprite horizontally
        self.flip_h = bit(attr, 6)
        # flip sprite vertically
        self.flip_v = bit(attr, 7)
        # x position of left side of sprite
        self.x_scroll = four_bytes[3]


class PatternTable(object):
    """
    Tile graphics for background and sprites.
    Each tile in the pattern table is 16 bytes, made of two planes.
    The first plane controls bit 0 of the color; the second plane controls bit 1.
    """
    def __init__(self, ppu):
        self.ppu = ppu
        # physical memory
        self.tables = [[]] * 2
        self.tables[0] = [0] * 4096
        self.tables[1] = [0] * 4096

    def read(self, a):
        pass

    def write(self, a, v):
        pass

    @staticmethod
    def render_tile(tile_bytes):
        assert len(tile_bytes) == 16
        ret = [] * 8
        for i in xrange(8):
            ret.append([])
            b0 = tile_bytes[i]
            b1 = tile_bytes[8 + i]
            for j in xrange(7, -1, -1):
                ret[i].append((((b1 >> j) & 0x1) << 1) + ((b0 >> j) & 0x1))
        return ret


class NameTable(object):
    """
        A nametable is a 1024 byte area of memory used by the PPU to lay out backgrounds.
    Each byte in the nametable controls one 8x8 pixel character cell,
    and each nametable has 30 rows of 32 tiles each,
    for 960 ($3C0) bytes; the rest is used by each nametable's attribute table.
        With each tile being 8x8 pixels, this makes a total of 256x240 pixels in one map,
    the same size as one full screen.
    """
    def __init__(self, ppu):
        self.ppu = ppu
        # physical memory
        self.tables = [[]] * 2
        self.tables[0] = [0] * 1024
        self.tables[1] = [0] * 1024
        # virtual memory, mirroring
        self.virtual_tables = [[]] * 4

    def read(self, a):
        pass

    def write(self, a, v):
        pass


class ObjAttrMemory(object):
    """
    OAM:
        The OAM (Object Attribute Memory) is internal memory inside the PPU that contains a display list of up to 64 sprites,
    where each sprite's information occupies 4 bytes.
    """
    def __init__(self):
        self.oam = [OamSprite] * 64

    def read(self, a):
        pass

    def write(self, a, v):
        pass


palettes = [
    [(3, 3, 3), (0, 1, 4), (0, 0, 6), (3, 2, 6), (4, 0, 3), (5, 0, 3), (5, 1, 0), (4, 2, 0), (3, 2, 0), (1, 2, 0), (0, 3, 1), (0, 4, 0), (0, 2, 2), (1, 1, 1), (0, 0, 3), (0, 2, 0)],
    [(5, 5, 5), (0, 3, 6), (0, 2, 7), (4, 0, 7), (5, 0, 7), (7, 0, 4), (7, 0, 0), (6, 3, 0), (4, 3, 0), (1, 4, 0), (0, 4, 0), (0, 5, 3), (0, 4, 4), (2, 2, 2), (2, 0, 0), (3, 1, 0)],
    [(7, 7, 7), (3, 5, 7), (4, 4, 7), (6, 3, 7), (7, 0, 7), (7, 3, 7), (7, 4, 0), (7, 5, 0), (6, 6, 0), (3, 6, 0), (0, 7, 0), (2, 7, 6), (0, 7, 7), (0, 0, 0), (0, 0, 0), (0, 0, 0)],
    [(7, 7, 7), (5, 6, 7), (6, 5, 7), (7, 5, 7), (7, 4, 7), (7, 5, 5), (7, 6, 4), (7, 7, 2), (7, 7, 3), (5, 7, 2), (4, 7, 3), (2, 7, 6), (4, 6, 7), (6, 6, 6), (6, 5, 3), (7, 6, 0)]]


class Palette(object):
    def __init__(self):
        pass


class PpuMemory(object):
    """
    Ppu Memory Map

    Address range	Size	Description
    $0000-$0FFF 	$1000	Pattern table 0
    $1000-$1FFF 	$1000	Pattern Table 1
    $2000-$23FF 	$0400	Nametable 0
    $2400-$27FF 	$0400	Nametable 1
    $2800-$2BFF 	$0400	Nametable 2
    $2C00-$2FFF 	$0400	Nametable 3
    $3000-$3EFF 	$0F00	Mirrors of $2000-$2EFF
    $3F00-$3F1F 	$0020	Palette RAM indexes
    $3F20-$3FFF 	$00E0	Mirrors of $3F00-$3F1F
    """
    def __init__(self, machine):
        self.m = machine
        self.ppu = machine.ppu

    def read(self, a):
        pass

    def write(self, a, v):
        pass


class Ppu(object):

    def __init__(self, machine):
        self.m = machine
        # registers
        self.r_ctrl = _RCtrl()
        self.r_mask = _RMask()
        self.r_status = _RStatus()

        # virtual devices
        self.oam = ObjAttrMemory(self)
