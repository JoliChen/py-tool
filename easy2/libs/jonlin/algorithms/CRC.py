# -*- coding: utf-8 -*-
# @Time    : 2021/5/18 3:51 PM
# @Author  : Joli
# @Email   : 99755349@qq.com

CRC32_TABLE = []

def crc32_init(table, poly):
    for i in range(256):
        x = i << 24
        y = 0
        for j in range(8):
            n = (x ^ y) & 0x80000000
            if n == 0:
                y = y << 1
            else:
                y = (y << 1) ^ poly
            x = x << 1
        table.append(y)

def crc32_datasum(data):
    if not CRC32_TABLE:
        crc32_init(CRC32_TABLE, 0x04C10DB7)
    accum = 0
    for i in range(len(data)):
        i = ((accum >> 24) ^ data[i]) & 0xFF
        accum = ((accum << 8) ^ CRC32_TABLE[i]) & 0xFFFFFFFF
    return accum

def crc32_filesum(path):
    with open(path, 'rb') as fp:
        return crc32_datasum(fp.read())