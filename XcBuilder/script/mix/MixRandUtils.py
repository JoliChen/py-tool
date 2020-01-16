# -*- coding: UTF-8 -*-

import os
import random
import math

MIX_SYMBOLS = ['+', '-', '*', '/']
MIX_SYM_LEN = MIX_SYMBOLS.__len__() - 1

MIX_CATALOG = ['short', 'int', 'long', 'long long', 'float', 'double']
MIX_CAT_LEN = MIX_CATALOG.__len__() - 1

MIX_COMPARE = ['==', '!=']
MIX_COM_LEN = MIX_COMPARE.__len__() - 1

MIX_C_TYPES = [('B', 1, (0, math.pow(2, 8)-1)),
               ('H', 2, (0, math.pow(2,16)-1)),
               ('I', 4, (0, math.pow(2,32)-1)),
               ('Q', 8, (0, math.pow(2,64)-1)),
               ('f', 4, (0, math.pow(2,32)-1)),
               ('d', 8, (0, math.pow(2,64)-1))]
MIX_C_T_LEN = MIX_C_TYPES.__len__() - 1

MIX_FORMATS = ['.jpg', '.png', '.mp3', '.mp4', '.txt', '.json', '.xml', '.csv', '.zip']
MIX_FOR_LEN = MIX_FORMATS.__len__() - 1

# 随机运算符号
def randomMathSymbol():
    return MIX_SYMBOLS[ random.randint(0, MIX_SYM_LEN) ]

# 随机数字类型
def randomValueType():
    return MIX_CATALOG[ random.randint(0, MIX_CAT_LEN) ]

# 随机文件格式
def randomFile():
    return MIX_FORMATS[ random.randint(0, MIX_FOR_LEN) ]

# 随机一个C类型
def randomCtype():
    return MIX_C_TYPES[random.randint(0, MIX_C_T_LEN)]

# 随机比较符号
def randomCompare():
    return '!=' if random.randint(0, 9) < 6 else '=='

# 随机出一个数字
def randNumber(ranges):
    return random.randint(ranges[0], ranges[1])

# 随机不重复选择
def randomSelect(srouce, recodes):
    while True :
        p = random.randint(0, len(srouce) - 1)
        f = srouce[p]
        if f not in recodes :
            srouce.remove(f)
            return f

# 随机名称
def randomString(minSize, maxSize):
    ret = ''
    for i in range( random.randint(minSize, maxSize) ) :
        ret += chr(random.randint(97, 122))
    return ret


# 随机目录
def randomDir(minDepth, maxDepth):
    dir = ''
    for i in range( random.randint(minDepth, maxDepth) ) :
        dir += randomString(3, 9) + os.sep
    return dir

# 获取随机数字
def randomValue():
    return random.randint(1, 30000)

# 随机数组元素
def randomItem(arraySrc):
    return arraySrc[ random.randint(0, len(arraySrc)-1) ]

# 将数组分割成N等份
def div_list(ls, n):
    if not isinstance(ls,list) or not isinstance(n,int):
        return []
    ls_len = len(ls)
    if n<=0 or 0==ls_len :
        return []
    if n > ls_len :
        return []
    elif n == ls_len :
        return [[i] for i in ls]
    else :
        j = ls_len / n
        k = ls_len % n
        ### j,j,j,...(前面有n-1个j),j+k
        #步长j,次数n-1
        ls_return = []
        for i in xrange(0,(n-1)*j,j) :
            ls_return.append(ls[i:i+j])
        #算上末尾的j+k
        ls_return.append(ls[(n-1)*j:])
        return ls_return

# 随机汉字
def randHans():
    return unichr( random.randint(0x4E00, 0x9FBF) )
