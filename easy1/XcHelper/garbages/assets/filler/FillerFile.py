# -*- coding: UTF-8 -*-
# 填充文件

import math
import random
import struct

class JFillerFile:
    # 数据类型定义
    default_bit_map = (('B', 1, (0, math.pow(2, 8) - 1)),
                       ('H', 2, (0, math.pow(2, 16) - 1)),
                       ('I', 4, (0, math.pow(2, 32) - 1)),
                       ('f', 4, (0, math.pow(2, 32) - 1)),
                       ('Q', 8, (0, math.pow(2, 64) - 1)),
                       ('d', 8, (0, math.pow(2, 64) - 1)))

    # 获取字节序列
    @classmethod
    def _get_stream(cls, byte_size):
        b = []
        t = cls.default_bit_map
        m = len(t)
        d = None
        i = 0
        n = 0
        while (True):
            i = int(random.random() * m)
            d = t[i]
            n = n + d[1]
            if (n < byte_size):
                b.append(d)
            elif (n > byte_size):
                n = n - d[1]
                m = i  # 优化运算速度
            else:
                b.append(d)
                break
        return b

    @classmethod
    def get_bytes(cls, byte_size):
        stream = cls._get_stream(byte_size)
        format = ''
        v_list = []
        for i in range(len(stream)):
            d = stream[i]
            format += d[0]
            v_list.append(random.randint(d[2][0], d[2][1]))
        return struct.Struct(format).pack(*tuple(v_list))
