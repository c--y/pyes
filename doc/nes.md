# Pyes

## 机器概述



## 6502


| name | type |  desc |
|--------|--------| ---- |
|   pc     |  u16      | 程序计数器 |
|  acc |  



## mapper与rom


### ines格式

`.nes`后缀.

组成:
- Header (16 bytes)
- Trainer, if present (0 or 512 bytes)
- PRG ROM data (16384 * x bytes)
- CHR ROM data, if present (8192 * y bytes)
- PlayChoice INST-ROM, if present (0 or 8192 bytes)
- PlayChoice PROM, if present (16 bytes Data, 16 bytes CounterOut) (this is often missing, see PC10 ROM-Images for details)

