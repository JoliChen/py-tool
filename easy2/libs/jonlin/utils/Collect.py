# -*- coding: utf-8 -*-
# @Time    : 2019/4/22 12:28 PM
# @Author  : Joli
# @Email   : 99755349@qq.com

# 安全的删除key，即使key不存在也不会报错。
def safe_pop(d, k):
    if k in d:
        d.pop(k)

# 获取一个子级字典，若该节点为空则创建一个。
def gen_dict(d, k):
    v = d.get(k)
    if v is None:
        d[k] = v = {}
    return v

# 获取一个子级数组，若该节点为空则创建一个。
def gen_list(d, k):
    v = d.get(k)
    if v is None:
        d[k] = v = []
    return v

# 判断数组是否相同
def equal_list(a, b):
    size = len(a)
    if len(b) != size:
        return False
    for i in range(size):
        if a[i] != b[i]:
            return False
    return True