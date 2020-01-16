# -*- coding: UTF-8 -*-
# 命名工具

import random
from XcHelper.common.RandUtils import JRand

class JWords:
    __forbidden = ('wx', 'weixin', 'wechat',
                   'alipay', 'alipays',
                   'facebook', 'google', 'android'
                   'pay', 'recharge', 'zhifu', 'money', 'rmb',
                   'http', 'https', 'ftp', 'cdn', 'remote', 'server', 'service',
                   'js', 'javascript', 'lua', 'py', 'python')

    # 检查屏蔽字
    @classmethod
    def _not_forbidden(cls, s):
        return s.lower() not in cls.__forbidden

    # 驼峰命名
    @classmethod
    def hump(cls, left, right, upper_first=False, rate_left=2, rate_right=4):
        f = ''
        n = JRand.rand_int(left, right)
        if upper_first:
            f = cls.uppers(1)
            n -= 1
            if n == 0:
                return f
        m = JRand.rand_int(0, int(n / JRand.rand_int(rate_left, rate_right)))
        if m == 0:
            if upper_first:
                return '%s%s' % (f, cls.lowers(n))
            else:
                return cls.lowers(n)
        s = ''
        for i in range(m):
            w = JRand.rand_lave(n, m, i)
            n -= w # 扣除当前分配的数额
            if i == 0:
                s = '%s%s' % (s, cls.lowers(w))
            else:
                s = '%s%s' % (s, cls.uppers(1))
                if w > 1:
                    s = '%s%s' % (s, cls.lowers(w-1))
        if upper_first:
            return '%s%s' % (cls.uppers(1), s)
        else:
            return s

    # 生成小写字母串
    @classmethod
    def lowers(cls, size):
        while True:
            s = ''
            for i in range(size):
                s = '%s%c' % (s, random.randint(97, 122))
            if cls._not_forbidden(s):
                return s

    # 生成大写字母串
    @classmethod
    def uppers(cls, size):
        while True:
            s = ''
            for i in range(size):
                s = '%s%c' % (s, random.randint(65, 90))
            if cls._not_forbidden(s):
                return s

    # 随机小写字母串
    @classmethod
    def rand_lowers(cls, left, right):
        return cls.lowers(JRand.rand_int(left, right))

    # 随机大写字母串
    @classmethod
    def rand_uppers(cls, left, right):
        return cls.uppers(JRand.rand_int(left, right))
