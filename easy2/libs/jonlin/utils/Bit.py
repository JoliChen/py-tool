# -*- coding: utf-8 -*-
# @Time    : 2019/3/25 7:29 PM
# @Author  : Joli
# @Email   : 99755349@qq.com

import ctypes
import struct

BIG_ENDIAN = '>'
LITTLE_ENDIAN = '<'

# 大于n[0:2^32]的最近pow2
def u32_next_pow2(n):
    n -= 1
    n |= n >> 1
    n |= n >> 2
    n |= n >> 4
    n |= n >> 8
    n |= n >> 16
    return n + 1

# 小于n[0:2^32]的最近pow2
def u32_prev_pow2(n):
    return u32_next_pow2(n) >> 1

# 将u32拆分成4个字节
def u32_bytes(n, endian=LITTLE_ENDIAN):
    bits = [n & 0xFF, n >> 8 & 0xFF, n >> 16 & 0xFF, n >> 24 & 0xFF]
    return bytes(bits if endian == LITTLE_ENDIAN else bits.reverse())

# 将u16拆分成2个字节
def u16_bytes(n, endian=LITTLE_ENDIAN):
    bits = [n & 0xFF, n >> 8 & 0xFF]
    return bytes(bits if endian == LITTLE_ENDIAN else bits.reverse())

# 将4个字节还原成u32
def u32_from(b, endian=LITTLE_ENDIAN):
    return b[0] + (b[1] << 8) + (b[2] << 16) + (b[3] << 24) \
        if endian == LITTLE_ENDIAN else \
        b[3] + (b[2] << 8) + (b[1] << 16) + (b[0] << 24)

# 将2个字节还原成u16
def u16_from(b, endian=LITTLE_ENDIAN):
    return b[0] + (b[1] << 8) if endian == LITTLE_ENDIAN else b[1] + (b[0] << 8)

# 将字节数组转成16进制字符格式
def bytes2hex(buf):
    array = []
    for i in range(len(buf)):
        array.append('0x%x' % buf[i])
    return array

# 基于bit(0/1)的标志位存储器
class MaskFlag:
    def __init__(self, mask=0):
        self._mask = mask

    def get_mask(self):
        return self._mask

    def has(self, pos):
        return self._mask & (1 << pos) != 0

    def set(self, pos):
        self._mask |= (1 << pos)

    def erase(self, pos):
        self._mask &= ~(1 << pos)

# 二进制数组
class ByteArray:
    def __init__(self, endian=LITTLE_ENDIAN):
        self.set_endian(endian)

    def init_capacity(self, capacity):
        self._capacity = capacity
        self._buffer = ctypes.create_string_buffer(capacity)
        self.clear()
        return self

    def init_buffer(self, buffer, capacity=None, position=None, length=None):
        buffer_len = len(buffer)
        if capacity is None:
            capacity = buffer_len
        self._buffer = ctypes.create_string_buffer(capacity)
        ctypes.memmove(self._buffer, buffer, buffer_len)
        self._capacity = capacity
        self._position = 0 if position is None else position
        self._length = buffer_len if length is None else length
        return self

    def slim_buffer(self):
        buffer = ctypes.create_string_buffer(self._length)
        ctypes.memmove(buffer, self._buffer, self._length)
        return buffer

    def clear(self):
        self._length = 0
        self._position = 0

    # -------------------- [@、=、<、>、!] ------------------
    #   @     native                      native   凑够4个字节
    #   =     native                      standard 按原字节数
    #   <     little - endian             standard 按原字节数
    #   >     big - endian                standard 按原字节数
    #   !     network( = big - endian)    standard 按原字节数
    def set_endian(self, endian):
        self._endian = endian
        return self

    def set_position(self, position):
        self._position = position
        return self

    def get_position(self):
        return self._position

    def get_available(self):
        return self._length - self._position

    def _before_write(self, move):
        if self._position + move > self._capacity:
            self.init_buffer(self._buffer, self._capacity * 2, self._position, self._length)

    def _after_write(self, move):
        self._position += move
        if self._position > self._length:
            self._length = self._position

    def _fmt(self, sig):
        return self._endian + sig

    def write_bytes(self, buffer, size):
        self._before_write(size)
        if not isinstance(buffer, bytes):
            buffer = bytes(buffer)
        struct.pack_into(self._fmt('%ds' % size), self._buffer, self._position, buffer)
        self._after_write(size)

    def read_bytes(self, size):
        meta = struct.unpack_from(self._fmt('%ds' % size), self._buffer, self._position)
        self._position += size
        return meta[0]

    def write_utf8(self, value):
        buff = value.encode(encoding='utf8')
        size = len(buff)
        self._before_write(size + 2)
        struct.pack_into(self._fmt('H%ds' % size), self._buffer, self._position, size, buff)
        self._after_write(size + 2)

    def read_utf8(self, size=None):
        if size is None:
            size = struct.unpack_from(self._fmt('H'), self._buffer, self._position)[0]
        meta = struct.unpack_from(self._fmt('%ds' % size), self._buffer, self._position + 2)
        self._position += size + 2
        return meta[0].decode(encoding='utf8')

    def write_byte(self, value):
        self._before_write(1)
        struct.pack_into(self._fmt('b'), self._buffer, self._position, value)
        self._after_write(1)

    def read_byte(self):
        meta = struct.unpack_from(self._fmt('b'), self._buffer, self._position)
        self._position += 1
        return meta[0]

    def write_short(self, value):
        self._before_write(2)
        struct.pack_into(self._fmt('h'), self._buffer, self._position, value)
        self._after_write(2)

    def read_short(self):
        meta = struct.unpack_from(self._fmt('h'), self._buffer, self._position)
        self._position += 2
        return meta[0]

    def write_int(self, value):
        self._before_write(4)
        struct.pack_into(self._fmt('i'), self._buffer, self._position, value)
        self._after_write(4)

    def read_int(self):
        meta = struct.unpack_from(self._fmt('i'), self._buffer, self._position)
        self._position += 4
        return meta[0]

    def write_longlong(self, value):
        self._before_write(8)
        struct.pack_into(self._fmt('q'), self._buffer, self._position, value)
        self._after_write(8)

    def read_longlong(self):
        meta = struct.unpack_from(self._fmt('q'), self._buffer, self._position)
        self._position += 8
        return meta[0]

    def write_float(self, value):
        self._before_write(4)
        struct.pack_into(self._fmt('f'), self._buffer, self._position, value)
        self._after_write(4)

    def read_float(self):
        meta = struct.unpack_from(self._fmt('f'), self._buffer, self._position)
        self._position += 4
        return meta[0]

    def write_double(self, value):
        self._before_write(8)
        struct.pack_into(self._fmt('d'), self._buffer, self._position, value)
        self._after_write(8)

    def read_double(self):
        meta = struct.unpack_from(self._fmt('d'), self._buffer, self._position)
        self._position += 8
        return meta[0]

    def write_u8(self, value):
        self._before_write(1)
        struct.pack_into(self._fmt('B'), self._buffer, self._position, value)
        self._after_write(1)

    def read_u8(self):
        meta = struct.unpack_from(self._fmt('B'), self._buffer, self._position)
        self._position += 1
        return meta[0]

    def write_u16(self, value):
        self._before_write(2)
        struct.pack_into(self._fmt('H'), self._buffer, self._position, value)
        self._after_write(2)

    def read_u16(self):
        meta = struct.unpack_from(self._fmt('H'), self._buffer, self._position)
        self._position += 2
        return meta[0]

    def write_u32(self, value):
        self._before_write(4)
        struct.pack_into(self._fmt('I'), self._buffer, self._position, value)
        self._after_write(4)

    def read_u32(self):
        meta = struct.unpack_from(self._fmt('I'), self._buffer, self._position)
        self._position += 4
        return meta[0]

    def write_u64(self, value):
        self._before_write(8)
        struct.pack_into(self._fmt('Q'), self._buffer, self._position, value)
        self._after_write(8)

    def read_u64(self):
        meta = struct.unpack_from(self._fmt('Q'), self._buffer, self._position)
        self._position += 8
        return meta[0]