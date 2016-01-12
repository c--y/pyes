# coding=utf-8


def am_implied():
    pass


def am_indexed_indirect():
    pass


def am_zero_page():
    pass


def am_immediate():
    pass


def am_accumulator():
    pass


def am_absolute():
    pass


def am_relative():
    pass


def am_indirect_indexed():
    pass


def am_zero_page_x():
    pass


def am_zero_page_y():
    pass


def am_absolute_x():
    pass


def am_absolute_y():
    pass


def am_indirect():
    pass


opcodes = {
    0x00: ('brk', am_implied, 7),
    0x01: ('ora', am_indexed_indirect, 6),
    0x05: ('ora', am_zero_page, 2),
    0x06: ('asl', am_zero_page, 5),
    0x08: ('php', am_implied, 3),
    0x09: ('ora', am_immediate, 2),
    0x0a: ('asl_acc', am_accumulator, 2),
    0x0d: ('ora', am_absolute, 4),
    0x0e: ('asl', am_absolute, 6),
    0x10: ('bpl', am_relative, 2),
    0x11: ('ora', am_indirect_indexed, 5),
    0x15: ('ora', am_zero_page_x, 4),
    0x16: ('asl', am_zero_page_x, 6),
    0x18: ('clc', am_implied, 2),
    0x19: ('ora', am_absolute_y, 4),
    0x1d: ('ora', am_absolute_x, 4),
    0x1e: ('asl', am_absolute_x, 7),
    0x20: ('jsr', am_absolute, 6),
    0x21: ('and_', am_indexed_indirect, 6),
    0x24: ('bit', am_zero_page, 3),
    0x25: ('and_', am_zero_page, 3),
    0x26: ('rol', am_zero_page, 5),
    0x28: ('plp', am_implied, 4),
    0x29: ('and_', am_immediate, 2),
    0x2a: ('rol_acc', am_accumulator, 2),
    0x2c: ('bit', am_absolute, 4),
    0x2d: ('and_', am_absolute, 4),
    0x2e: ('rol', am_absolute, 6),
    0x30: ('bmi', am_relative, 2),
    0x31: ('and_', am_indirect_indexed, 5),
    0x35: ('and_', am_zero_page_x, 4),
    0x36: ('rol', am_zero_page_x, 6),
    0x38: ('sec', am_implied, 2),
    0x39: ('and_', am_absolute_y, 4),
    0x3d: ('and_', am_absolute_x, 4),
    0x3e: ('rol', am_absolute_x, 7),
    0x40: ('rti', am_implied, 6),
    0x41: ('eor', am_indexed_indirect, 6),
    0x45: ('eor', am_zero_page, 3),
    0x46: ('lsr', am_zero_page, 5),
    0x48: ('pha', am_implied, 3),
    0x49: ('eor', am_immediate, 2),
    0x4a: ('lsr_acc', am_accumulator, 2),
    0x4c: ('jmp', am_absolute, 3),
    0x4d: ('eor', am_absolute, 4),
    0x4e: ('lsr', am_absolute, 6),
    0x50: ('bvc', am_relative, 2),
    0x51: ('eor', am_indirect_indexed, 5),
    0x55: ('eor', am_zero_page_x, 4),
    0x56: ('lsr', am_zero_page_x, 6),
    0x58: ('cli', am_implied, 2),
    0x59: ('eor', am_absolute_y, 4),
    0x5d: ('eor', am_absolute_x, 4),
    0x5e: ('lsr', am_absolute_x, 7),
    0x60: ('rts', am_implied, 6),
    0x61: ('adc', am_indexed_indirect, 6),
    0x65: ('adc', am_zero_page, 3),
    0x66: ('ror', am_zero_page, 5),
    0x68: ('pla', am_implied, 4),
    0x69: ('adc', am_immediate, 2),
    0x6a: ('ror_acc', am_accumulator, 2),
    0x6c: ('jmp', am_indirect, 5),
    0x6d: ('adc', am_absolute, 4),
    0x6e: ('ror', am_absolute, 6),
    0x70: ('bvs', am_relative, 2),
    0x71: ('adc', am_indirect_indexed, 5),
    0x75: ('adc', am_zero_page_x, 4),
    0x76: ('ror', am_zero_page_x, 6),
    0x78: ('sei', am_implied, 2),
    0x79: ('adc', am_absolute_y, 4),
    0x7e: ('ror', am_absolute_x, 7),
    0x81: ('sta', am_indexed_indirect, 6),
    0x84: ('sty', am_zero_page, 3),
    0x85: ('sta', am_zero_page, 3),
    0x86: ('stx', am_zero_page, 3),
    0x88: ('dey', am_implied, 2),
    0x8a: ('txa', am_implied, 2),
    0x8c: ('sty', am_absolute, 4),
    0x8d: ('sta', am_absolute, 4),
    0x8e: ('stx', am_absolute, 4),
    0x90: ('bcc', am_relative, 2),
    0x91: ('sta', am_indirect_indexed, 6),
    0x94: ('sty', am_zero_page_x, 4),
    0x95: ('sta', am_zero_page_x, 4),
    0x96: ('stx', am_zero_page_y, 4),
    0x98: ('tya', am_implied, 2),
    0x99: ('sta', am_absolute_y, 5),
    0x9a: ('txs', am_implied, 2),
    0x9d: ('sta', am_absolute_x, 5),
    0xa0: ('ldy', am_immediate, 2),
    0xa1: ('lda', am_indexed_indirect, 6),
    0xa2: ('ldx', am_immediate, 2),
    0xa4: ('ldy', am_zero_page, 3),
    0xa5: ('lda', am_zero_page, 3),
    0xa6: ('ldx', am_zero_page, 3),
    0xa8: ('tay', am_implied, 2),
    0xa9: ('lda', am_immediate, 2),
    0xaa: ('tax', am_implied, 2),
    0xac: ('ldy', am_absolute, 4),
    0xad: ('lda', am_absolute, 4),
    0xae: ('ldx', am_absolute, 4),
    0xb0: ('bcs', am_relative, 2),
    0xb1: ('lda', am_indirect_indexed, 5),
    0xb4: ('ldy', am_zero_page_x, 4),
    0xb5: ('lda', am_zero_page_x, 4),
    0xb6: ('ldx', am_zero_page_y, 4),
    0xb8: ('clv', am_implied, 2),
    0xb9: ('lda', am_absolute_y, 4),
    0xba: ('tsx', am_implied, 2),
    0xbc: ('ldy', am_absolute_x, 4),
    0xbd: ('lda', am_absolute_x, 4),
    0xbe: ('ldx', am_absolute_y, 4),
    0xca: ('dex', am_implied, 2),
    0xcc: ('cpy', am_absolute, 4),
    0xcd: ('cmp', am_absolute, 4),
    0xce: ('dec', am_absolute, 6),
    0xd0: ('bne', am_relative, 2),
    0xd1: ('cmp', am_indirect_indexed, 5),
    0xd5: ('cmp', am_zero_page_x, 4),
    0xd6: ('dec', am_zero_page_x, 6),
    0xd8: ('cld', am_implied, 2),
    0xd9: ('cmp', am_absolute_y, 4),
    0xdd: ('cmp', am_absolute_x, 4),
    0xde: ('dec', am_absolute_x, 7),
    0xe0: ('cpx', am_immediate, 2),
    0xe1: ('sbc', am_indexed_indirect, 6),
    0xe4: ('cpx', am_zero_page, 3),
    0xe5: ('sbc', am_zero_page, 3),
    0xe6: ('inc', am_zero_page, 5),
    0xe8: ('inx', am_implied, 2),
    0xe9: ('sbc', am_immediate, 2),
    0xea: ('nop', am_implied, 2),
    0xeb: ('cpx', am_absolute, 4),
    0xed: ('sbc', am_absolute, 4),
    0xf0: ('beq', am_relative, 2),
    0xf1: ('sbc', am_indirect_indexed, 5),
    0xf5: ('sbc', am_zero_page_x, 4),
    0xf6: ('inc', am_zero_page_x, 6),
    0xf8: ('sed', am_implied, 2),
    0xf9: ('sbc', am_absolute_y, 4),
    0xfd: ('sbc', am_absolute_x, 4),
    0xfe: ('inc', am_absolute_x, 7)
}


def dis(code, pc):
    pass