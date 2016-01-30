# coding=utf-8
"""
Dump the disassembled bytecode.
"""
from util import u8n, u16n, make_u16


def am_implied(c, pc):
    return [], ''


def am_indexed_indirect(c, pc):
    a0 = c.m_read(pc)
    a1 = u8n(a0 + c.x.value)

    h = c.m_read(u8n(a1 + 1))
    l = c.m_read(a1)
    r = make_u16(h, l)
    v = c.m_read(r)

    return [a0], '($%.2X,X) @ %.2X = %.4X = %.2X' % (a0, a1, r, v)


def am_zero_page(c, pc):
    v = c.m_read(pc)
    vv = c.m_read(u16n(v))
    return [v], '$%.2X = %.2X' % (v, vv)


def am_immediate(c, pc):
    v = c.m_read(pc)
    return [v], '#$%.2X' % (v,)


def am_accumulator(c, pc):
    return [], 'A'


def am_absolute(c, pc):
    h = c.m_read(pc + 1)
    l = c.m_read(pc)
    a = make_u16(h, l)
    return [l, h], '$%.4X' % (a,)


def am_absolute_value(c, pc):
    h = c.m_read(pc + 1)
    l = c.m_read(pc)
    a = make_u16(h, l)
    v = c.m_read(a)
    return [l, h], '$%.4X = %.2X' % (a, v)


def am_relative(c, pc):
    a1 = c.m_read(pc)
    pc += 1
    # a1: this value is signed, values #00-#7F are positive, and values #FF-#80 are negative
    a2 = u16n(pc + a1) if a1 < 0x80 else u16n(a1 + pc - 0x100)
    return [a1], '$%.4X' % (a2,)


def am_indirect_indexed(c, pc):
    a0 = c.m_read(pc)
    h = c.m_read(u8n(a0 + 1))
    l = c.m_read(a0)
    a = make_u16(h, l)
    r = u16n(a + c.y.value)
    v = c.m_read(r)

    return [a0], '($%.2X),Y = %.4X @ %.4X = %.2X' % (a0, a, r, v)


def am_zero_page_x(c, pc):
    a0 = c.m_read(pc)
    r = u8n(a0 + c.x.value)
    v = c.m_read(r)
    return [a0], '$%.2X,X @ %.2X = %.2X' % (a0, r, v)


def am_zero_page_y(c, pc):
    a0 = c.m_read(pc)
    r = u8n(a0 + c.y.value)
    v = c.m_read(r)
    return [a0], '$%.2X,Y @ %.2X = %.2X' % (a0, r, v)


def am_absolute_x(c, pc):
    h = c.m_read(u16n(pc + 1))
    l = c.m_read(pc)
    a = make_u16(h, l)
    r = u16n(a + c.x.value)
    v = c.m_read(r)
    return [l, h], '$%.4X,X @ %.4X = %.2X' % (a, r, v)


def am_absolute_y(c, pc):
    h = c.m_read(u16n(pc + 1))
    l = c.m_read(pc)
    a = make_u16(h, l)
    r = u16n(a + c.y.value)
    v = c.m_read(r)
    return [l, h], '$%.4X,Y @ %.4X = %.2X' % (a, r, v)


def am_indirect(c, pc):
    h = c.m_read(u16n(pc + 1))
    l = c.m_read(pc)
    al = make_u16(h, l)
    ah = make_u16(h, u8n(l + 1))
    h_high = c.m_read(ah)
    l_low = c.m_read(al)
    r = make_u16(h_high, l_low)
    return [l, h], '($%.4X) = %.4X' % (al, r)

opcodes = {
    0x00: ('BRK', am_implied, 7),
    0x01: ('ORA', am_indexed_indirect, 6),
    0x03: ('*SLO', am_indexed_indirect, 8),
    0x04: ('*NOP', am_zero_page, 3),
    0x05: ('ORA', am_zero_page, 2),
    0x06: ('ASL', am_zero_page, 5),
    0x07: ('*SLO', am_zero_page, 5),
    0x08: ('PHP', am_implied, 3),
    0x09: ('ORA', am_immediate, 2),
    0x0a: ('ASL', am_accumulator, 2),
    0x0c: ('*NOP', am_absolute_value, 4),
    0x0d: ('ORA', am_absolute_value, 4),
    0x0e: ('ASL', am_absolute_value, 6),
    0x0f: ('*SLO', am_absolute_value, 6),
    0x10: ('BPL', am_relative, 2),
    0x11: ('ORA', am_indirect_indexed, 5),
    0x13: ('*SLO', am_indirect_indexed, 8),
    0x14: ('*NOP', am_zero_page_x, 4),
    0x15: ('ORA', am_zero_page_x, 4),
    0x16: ('ASL', am_zero_page_x, 6),
    0x17: ('*SLO', am_zero_page_x, 6),
    0x18: ('CLC', am_implied, 2),
    0x19: ('ORA', am_absolute_y, 4),
    0x1a: ('*NOP', am_implied, 2),
    0x1b: ('*SLO', am_absolute_y, 7),
    0x1c: ('*NOP', am_absolute_x, 4),
    0x1d: ('ORA', am_absolute_x, 4),
    0x1e: ('ASL', am_absolute_x, 7),
    0x1f: ('*SLO', am_absolute_x, 7),
    0x20: ('JSR', am_absolute, 6),
    0x21: ('AND', am_indexed_indirect, 6),
    0x23: ('*RLA', am_indexed_indirect, 8),
    0x24: ('BIT', am_zero_page, 3),
    0x25: ('AND', am_zero_page, 3),
    0x26: ('ROL', am_zero_page, 5),
    0x27: ('*RLA', am_zero_page, 5),
    0x28: ('PLP', am_implied, 4),
    0x29: ('AND', am_immediate, 2),
    0x2a: ('ROL', am_accumulator, 2),
    0x2c: ('BIT', am_absolute_value, 4),
    0x2d: ('AND', am_absolute_value, 4),
    0x2e: ('ROL', am_absolute_value, 6),
    0x2f: ('*RLA', am_absolute_value, 6),
    0x30: ('BMI', am_relative, 2),
    0x31: ('AND', am_indirect_indexed, 5),
    0x33: ('*RLA', am_indirect_indexed, 8),
    0x34: ('*NOP', am_zero_page_x, 4),
    0x35: ('AND', am_zero_page_x, 4),
    0x36: ('ROL', am_zero_page_x, 6),
    0x37: ('*RLA', am_zero_page_x, 6),
    0x38: ('SEC', am_implied, 2),
    0x39: ('AND', am_absolute_y, 4),
    0x3a: ('*NOP', am_implied, 2),
    0x3b: ('*RLA', am_absolute_y, 7),
    0x3c: ('*NOP', am_absolute_x, 4),
    0x3d: ('AND', am_absolute_x, 4),
    0x3e: ('ROL', am_absolute_x, 7),
    0x3f: ('*RLA', am_absolute_x, 7),
    0x40: ('RTI', am_implied, 6),
    0x41: ('EOR', am_indexed_indirect, 6),
    0x43: ('*SRE', am_indexed_indirect, 8),
    0x44: ('*NOP', am_zero_page, 3),
    0x45: ('EOR', am_zero_page, 3),
    0x46: ('LSR', am_zero_page, 5),
    0x47: ('*SRE', am_zero_page, 5),
    0x48: ('PHA', am_implied, 3),
    0x49: ('EOR', am_immediate, 2),
    0x4a: ('LSR', am_accumulator, 2),
    0x4c: ('JMP', am_absolute, 3),
    0x4d: ('EOR', am_absolute_value, 4),
    0x4e: ('LSR', am_absolute_value, 6),
    0x4f: ('*SRE', am_absolute_value, 6),
    0x50: ('BVC', am_relative, 2),
    0x51: ('EOR', am_indirect_indexed, 5),
    0x53: ('*SRE', am_indirect_indexed, 8),
    0x54: ('*NOP', am_zero_page_x, 4),
    0x55: ('EOR', am_zero_page_x, 4),
    0x56: ('LSR', am_zero_page_x, 6),
    0x57: ('*SRE', am_zero_page_x, 6),
    0x58: ('CLI', am_implied, 2),
    0x59: ('EOR', am_absolute_y, 4),
    0x5a: ('*NOP', am_implied, 2),
    0x5b: ('*SRE', am_absolute_y, 7),
    0x5c: ('*NOP', am_absolute_x, 4),
    0x5d: ('EOR', am_absolute_x, 4),
    0x5e: ('LSR', am_absolute_x, 7),
    0x5f: ('*SRE', am_absolute_x, 7),
    0x60: ('RTS', am_implied, 6),
    0x61: ('ADC', am_indexed_indirect, 6),
    0x63: ('*RRA', am_indexed_indirect, 8),
    0x64: ('*NOP', am_zero_page, 3),
    0x65: ('ADC', am_zero_page, 3),
    0x66: ('ROR', am_zero_page, 5),
    0x67: ('*RRA', am_zero_page, 5),
    0x68: ('PLA', am_implied, 4),
    0x69: ('ADC', am_immediate, 2),
    0x6a: ('ROR', am_accumulator, 2),
    0x6c: ('JMP', am_indirect, 5),
    0x6d: ('ADC', am_absolute_value, 4),
    0x6e: ('ROR', am_absolute_value, 6),
    0x6f: ('*RRA', am_absolute_value, 6),
    0x70: ('BVS', am_relative, 2),
    0x71: ('ADC', am_indirect_indexed, 5),
    0x73: ('*RRA', am_indirect_indexed, 8),
    0x74: ('*NOP', am_zero_page_x, 4),
    0x75: ('ADC', am_zero_page_x, 4),
    0x76: ('ROR', am_zero_page_x, 6),
    0x77: ('*RRA', am_zero_page_x, 6),
    0x78: ('SEI', am_implied, 2),
    0x79: ('ADC', am_absolute_y, 4),
    0x7a: ('*NOP', am_implied, 2),
    0x7b: ('*RRA', am_absolute_y, 7),
    0x7c: ('*NOP', am_absolute_x, 4),
    0x7d: ('ADC', am_absolute_x, 4),
    0x7e: ('ROR', am_absolute_x, 7),
    0x7f: ('*RRA', am_absolute_x, 7),
    0x80: ('*NOP', am_immediate, 2),
    0x81: ('STA', am_indexed_indirect, 6),
    0x83: ('*SAX', am_indexed_indirect, 6),
    0x84: ('STY', am_zero_page, 3),
    0x85: ('STA', am_zero_page, 3),
    0x86: ('STX', am_zero_page, 3),
    0x87: ('*SAX', am_zero_page, 3),
    0x88: ('DEY', am_implied, 2),
    0x89: ('*NOP', am_immediate, 2),
    0x8a: ('TXA', am_implied, 2),
    0x8c: ('STY', am_absolute_value, 4),
    0x8d: ('STA', am_absolute_value, 4),
    0x8e: ('STX', am_absolute_value, 4),
    0x8f: ('*SAX', am_absolute_value, 4),
    0x90: ('BCC', am_relative, 2),
    0x91: ('STA', am_indirect_indexed, 6),
    0x94: ('STY', am_zero_page_x, 4),
    0x95: ('STA', am_zero_page_x, 4),
    0x96: ('STX', am_zero_page_y, 4),
    0x97: ('*SAX', am_zero_page_y, 4),
    0x98: ('TYA', am_implied, 2),
    0x99: ('STA', am_absolute_y, 5),
    0x9a: ('TXS', am_implied, 2),
    0x9d: ('STA', am_absolute_x, 5),
    0xa0: ('LDY', am_immediate, 2),
    0xa1: ('LDA', am_indexed_indirect, 6),
    0xa2: ('LDX', am_immediate, 2),
    0xa3: ('*LAX', am_indexed_indirect, 6),
    0xa4: ('LDY', am_zero_page, 3),
    0xa5: ('LDA', am_zero_page, 3),
    0xa6: ('LDX', am_zero_page, 3),
    0xa7: ('*LAX', am_zero_page, 3),
    0xa8: ('TAY', am_implied, 2),
    0xa9: ('LDA', am_immediate, 2),
    0xaa: ('TAX', am_implied, 2),
    0xac: ('LDY', am_absolute_value, 4),
    0xad: ('LDA', am_absolute_value, 4),
    0xae: ('LDX', am_absolute_value, 4),
    0xaf: ('*LAX', am_absolute_value, 4),
    0xb0: ('BCS', am_relative, 2),
    0xb1: ('LDA', am_indirect_indexed, 5),
    0xb3: ('*LAX', am_indirect_indexed, 5),
    0xb4: ('LDY', am_zero_page_x, 4),
    0xb5: ('LDA', am_zero_page_x, 4),
    0xb6: ('LDX', am_zero_page_y, 4),
    0xb7: ('*LAX', am_zero_page_y, 4),
    0xb8: ('CLV', am_implied, 2),
    0xb9: ('LDA', am_absolute_y, 4),
    0xba: ('TSX', am_implied, 2),
    0xbc: ('LDY', am_absolute_x, 4),
    0xbd: ('LDA', am_absolute_x, 4),
    0xbe: ('LDX', am_absolute_y, 4),
    0xbf: ('*LAX', am_absolute_y, 4),
    0xc0: ('CPY', am_immediate, 2),
    0xc1: ('CMP', am_indexed_indirect, 2),
    0xc3: ('*DCP', am_indexed_indirect, 8),
    0xc4: ('CPY', am_zero_page, 3),
    0xc5: ('CMP', am_zero_page, 3),
    0xc6: ('DEC', am_zero_page, 5),
    0xc7: ('*DCP', am_zero_page, 5),
    0xc8: ('INY', am_implied, 2),
    0xc9: ('CMP', am_immediate, 2),
    0xca: ('DEX', am_implied, 2),
    0xcc: ('CPY', am_absolute_value, 4),
    0xcd: ('CMP', am_absolute_value, 4),
    0xce: ('DEC', am_absolute_value, 6),
    0xcf: ('*DCP', am_absolute_value, 6),
    0xd0: ('BNE', am_relative, 2),
    0xd1: ('CMP', am_indirect_indexed, 5),
    0xd3: ('*DCP', am_indirect_indexed, 8),
    0xd4: ('*NOP', am_zero_page_x, 4),
    0xd5: ('CMP', am_zero_page_x, 4),
    0xd6: ('DEC', am_zero_page_x, 6),
    0xd7: ('*DCP', am_zero_page_x, 6),
    0xd8: ('CLD', am_implied, 2),
    0xd9: ('CMP', am_absolute_y, 4),
    0xda: ('*NOP', am_implied, 2),
    0xdb: ('*DCP', am_absolute_y, 7),
    0xdc: ('*NOP', am_absolute_x, 4),
    0xdd: ('CMP', am_absolute_x, 4),
    0xde: ('DEC', am_absolute_x, 7),
    0xdf: ('*DCP', am_absolute_x, 7),
    0xe0: ('CPX', am_immediate, 2),
    0xe1: ('SBC', am_indexed_indirect, 6),
    0xe3: ('*ISB', am_indexed_indirect, 8),
    0xe4: ('CPX', am_zero_page, 3),
    0xe5: ('SBC', am_zero_page, 3),
    0xe6: ('INC', am_zero_page, 5),
    0xe7: ('*ISB', am_zero_page, 5),
    0xe8: ('INX', am_implied, 2),
    0xe9: ('SBC', am_immediate, 2),
    0xea: ('NOP', am_implied, 2),
    0xeb: ('*SBC', am_immediate, 2),
    0xec: ('CPX', am_absolute_value, 4),
    0xed: ('SBC', am_absolute_value, 4),
    0xee: ('INC', am_absolute_value, 6),
    0xef: ('*ISB', am_absolute_value, 6),
    0xf0: ('BEQ', am_relative, 2),
    0xf1: ('SBC', am_indirect_indexed, 5),
    0xf3: ('*ISB', am_indirect_indexed, 8),
    0xf4: ('*NOP', am_zero_page_x, 4),
    0xf5: ('SBC', am_zero_page_x, 4),
    0xf6: ('INC', am_zero_page_x, 6),
    0xf7: ('*ISB', am_zero_page_x, 6),
    0xf8: ('SED', am_implied, 2),
    0xf9: ('SBC', am_absolute_y, 4),
    0xfa: ('*NOP', am_implied, 2),
    0xfb: ('*ISB', am_absolute_y, 7),
    0xfc: ('*NOP', am_absolute_x, 4),
    0xfd: ('SBC', am_absolute_x, 4),
    0xfe: ('INC', am_absolute_x, 7),
    0xff: ('*ISB', am_absolute_x, 7)
}


def dis(code, c, pc):
    if code not in opcodes:
        raise Exception('code[%.2X] not in opcodes' % (code,))

    cmd, address_fn, cycles = opcodes.get(code)
    raw_bytes, address_str = address_fn(c, pc)
    return '%.4X  %.2X %-5s %s %-27s' % (pc - 1, code, ' '.join(("%.2X" % (x,) for x in raw_bytes)), ' ' + cmd if len(cmd) == 3 else cmd, address_str)
