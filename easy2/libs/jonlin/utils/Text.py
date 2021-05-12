# -*- coding: utf-8 -*-
# @Time    : 2019/4/10 11:26 AM
# @Author  : Joli
# @Email   : 99755349@qq.com

UNICODE_MIN_DIGIT = ord('0')
UNICODE_MAX_DIGIT = ord('9')
UNICODE_MIN_LOWER = ord('a')
UNICODE_MAX_LOWER = ord('z')
UNICODE_MIN_UPPER = ord('A')
UNICODE_MAX_UPPER = ord('Z')

def isdigit_unicode(code):
    return UNICODE_MIN_DIGIT <= code <= UNICODE_MAX_DIGIT

def islower_unicode(code):
    return UNICODE_MIN_LOWER <= code <= UNICODE_MAX_LOWER

def isupper_unicode(code):
    return UNICODE_MIN_UPPER <= code <= UNICODE_MAX_UPPER

def isabc_unicode(code):
    return islower_unicode(code) or isupper_unicode(code)

def isword_unicode(code):
    return isdigit_unicode(code) or isabc_unicode(code)

def islower_str(ss):
    for s in ss:
        if not s.islower():
            return False
    return True

def isupper_str(ss):
    for s in ss:
        if not s.isupper():
            return False
    return True

# 将数组合并成字符串
def join(array, sep=''):
    s = ''
    if len(array) > 0:
        for v in array:
            s += (v if isinstance(v, str) else str(v)) + sep
        s = s[0:len(s)-len(sep)]
    return s

# 根据分隔符解包字符串 a,b = Text.unpack('a.b')
def unpack(s, sep='.'):
    return (i for i in s.split(sep))

# 从后往前查找字符
def last_find(s, c, start=-1, end=0):
    if start < 0:
        start = len(s) + start
        if start < 0:
            return -1
    if end < 0:
        end = len(s) + end
        if end < 0:
            return -1
    for i in range(start, end - 1, -1):
        if s[i] == c:
            return i
    return -1

def unicodes2str(bs):
    return ''.join([chr(b) for b in bs])

def str2unicodes(ss):
    return [ord(s) for s in ss]