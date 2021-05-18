# -*- coding: utf-8 -*-
# @Time    : 2021/5/18 4:29 PM
# @Author  : Joli
# @Email   : 99755349@qq.com

def bkdr(chars, seed=131):  # BKDRHash [31 131 1313 13131 131313]
    h = 0
    for c in chars:
        h = (h * seed + ord(c)) & 0xFFFFFFFF
    return h
