# -*- coding: UTF-8 -*-
# 随机工具

from __future__ import division
import random
import math

class JRand:

    # 随机一个数字 [b, t]
    @staticmethod
    def rand_int(b, t):
        if b < t :
            return random.randint(b, t)
        return t

    # 浮动分配算法（类似于发红包）
    # lave 剩余总额
    # nums 总人数
    # time 分配序号（从0开始）
    # less 最小分配额度
    # rate 斜率
    @staticmethod
    def rand_lave(lave, nums, time, less=1, rate=3):
        time = time + 1
        if (time == nums):
            return lave
        safe = min(lave - (nums - time) * less, int((lave / nums) * rate))
        return JRand.rand_int(less, safe)

    # 分配数组
    @staticmethod
    def rand_lave_list(array, n, i, less=0):
        if (array is None):
            return None
        size = len(array)
        n = JRand.rand_lave(size, n, i, less)
        if (n == 0) or (n > size):
            return None
        s = []
        for i in range(n):
            s.append(array.pop())
        return s

    # 就近随机（数字越小出现机会越大）[0, base-1]
    # base 基础值
    # rate 斜率
    @staticmethod
    def rand_nearest(base, rate=2):
        return int(math.pow(random.random(), rate) * base)

    # 就近选择
    @staticmethod
    def chose_nearest(seq):
        return seq[JRand.rand_nearest(len(seq))]