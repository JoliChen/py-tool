# -*- coding: utf-8 -*-
# @Time    : 2019/6/17 7:15 PM
# @Author  : Joli
# @Email   : 99755349@qq.com

import random

def scaling(maximum, ratio):  # 按比例缩小最大值，再去缩小值与最大值之间的随机数。
    return random.randint(int(maximum * ratio), maximum)

# 从列表中选取N个不同的元素
def sampling(array, n):
    if array and n > 0:
        array = list(array)
        random.shuffle(array)
        return array[0: min(n, len(array))]
    return []

# 自动取样
def auto_sampling(array, minimum=1, maximum=None):
    if maximum is None:
        maximum = len(array)
    return sampling(array, random.randint(min(minimum, maximum), maximum))

# 二倍均值随机分配（类似发红包算法）
# lave 剩余总额
# nums 剩余人数
# less 最小分配额度
def bonus(lave, nums, less=1):
    return lave if 1 == nums else random.randint(less, int(lave / nums) * 2)