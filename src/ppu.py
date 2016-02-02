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


class Ppu(object):

    def __init__(self, machine):
        self.m = machine
        # registers
        self.r_ctrl = _RCtrl()
        self.r_mask = _RMask()
        self.r_status = _RStatus()
