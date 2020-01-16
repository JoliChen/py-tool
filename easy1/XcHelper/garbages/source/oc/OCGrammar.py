# -*- coding: UTF-8 -*-
# Objective-C 语法定义

import random
import math

# 超类UIButton
SUPERS = ('NSObject', 'UIViewController', 'UINavigationController',
          'UIView', 'UIImageView', 'UIScrollView', 'UIWindow',
          'UITextField', 'UIButton', 'UILabel', 'UIImage',
          'UIPanGestureRecognizer', 'UITapGestureRecognizer', 'UIColor',
          'CAAnimationGroup', 'CAShapeLayer')
# 换行符号
SN = '\r\n'
# 缩进符号
def ST(indent=0):
    if (indent == 0):
        return ''
    t = ''
    for i in range(indent):
        t += '\t'
    return t

# OC语句树
class JOcLineTree:
    def __init__(self, mMethod):
        self.mMethod = mMethod #所属函数
        self.statements = [] #语句块

    # 字符串化
    def toString(self, indent = 0):
        s = ''
        for b in self.statements:
            if (isinstance(b, JOcLineTree)):
                s += b.toString(indent + 1)
            else:
                s += ST(indent) + b + SN
        return s


# OC函数
class JOcMethod:
    def __init__(self, mClass):
        self.mClass = mClass    # 属类
        self.scope = None       # 类函数或对象函数 ('+', '-')
        self.ret = None         # 返回数据类型 (NSString*, NSInteger, int, short, long)
        self.messages = []      # 指令元组
        self.argTypes = None    # 参数类型数组
        self.argNames = None    # 参数名称数组
        self.lineTree = None    # 语句树 (JOcLineTree)
        self.variables = None   # 局部变量列表

    # 函数定义复制
    def copyDef(self, tClass=None):
        meth = JOcMethod(tClass)
        meth.scope = self.scope
        meth.ret = self.ret
        meth.messages = self.messages[:]
        if (self.argTypes is not None):
            meth.argTypes = self.argTypes[:]
        if (self.argNames is not None):
            meth.argNames = self.argNames[:]
        return meth

    # 声明字符串化
    def toStringInterface(self, indent=0):
        # header
        s = self.scope + ' (' + self.ret + ') '
        # selector
        l = self.messages.__len__()
        for i in range(l):
            s += self.messages[i]
            if (self.argTypes is not None):
                s += ':(' + self.argTypes[i] + ')' + self.argNames[i]
            s += ' '
        return s

    # 实现字符串化
    def toStringImplement(self, indent=0):
        s = self.toStringInterface(indent)
        # logic
        s += '{' + SN
        # varialbe
        var_map = self.variables
        if (var_map is not None) and (len(var_map) > 0):
            for n in var_map:
                v = var_map[n]
                s += ST(indent + 1) + v[0] + ' ' + n
                if (v[1] is None):
                    s += ';' + SN
                else:
                    s += ' = ' + str(v[1]) + ';' + SN
        if (self.lineTree is not None):
            s += self.lineTree.toString(indent + 1)
        s += '}' + SN
        return s

# OC类
class JOcClass:
    def __init__(self, className, baseClass=None, protocol=None):
        self.baseClass = baseClass  # 父类
        self.protocol  = protocol  # 接口
        self.className = className  # 类名
        self.imports = None  # 导入头文件
        self.variables = None  # 变量元组
        self.methods = None  # 函数数组
        self.fileSuffix = '.m' # 文件后缀（.m, .mm）,默认是:.m

    # # 设置接口
    # def __setProtocol(self, protocol):
    #     if (self.methods is None):
    #         self.methods = []
    #     functions = protocol.requireds
    #     if (functions is not None):
    #         for meth in functions:
    #             self.methods.append( meth.copyDef(self.mClass) )
    #     functions = protocol.optionals
    #     if (functions is not None):
    #         for meth in functions:
    #             self.methods.append( meth.copyDef(self.mClass) )

    # 头文件串化
    def toStringInterface(self, indent=0):
        s = ''
        # header
        s += ST(indent) + '@interface' + ' ' + self.className + ' : '
        # super class
        if (self.baseClass is not None):
            s += self.baseClass
        else:
            s += SUPERS[int(math.pow(random.random(), 3) * len(SUPERS))]
        # protocol
        if (self.protocol is not None):
            s += ' ' + '<' + self.protocol + '>' + SN
        else:
            s += SN
        # method
        s += SN
        if (self.methods is not None):
            for m in self.methods:
                s += ST(indent) + m.toStringInterface(indent) + ';' + SN + SN
        s += ST(indent) + '@end'
        return s

    # 实现文件串化
    def toStringImplement(self, indent=0):
        s = ''
        # import
        s += ST(indent) + '#import "' + self.className + '.h"' + SN
        if (self.imports is not None):
            for head in self.imports:
                if head.startswith('<') and head.endswith('>'):
                    s += ST(indent) + '#import ' + head + SN
                else:
                    s += ST(indent) + '#import "' + head + '"' + SN
        s += SN
        # header
        s += ST(indent) + '@implementation' + ' ' + self.className
        # varialbe
        var_map = self.variables
        if (var_map is not None) and (len(var_map) > 0):
            s += ' ' + '{' + SN
            for n in var_map:
                t = var_map[n]
                s += ST(indent + 1) + t[0] + ' ' + n + ';' + SN
                # if (t[1] is None):
                #     s += ';' + SN
                # else:
                #     s += ' = ' + str(t[1]) + ';' + SN
            s += ST(indent) + '}' + SN
        else:
            s += SN
        # method
        s += SN
        if (self.methods is not None):
            for m in self.methods:
                s += ST(indent) + m.toStringImplement(indent) + SN + SN
        s += ST(indent) + '@end'
        return s


# OC接口
# class JOcProtocol:
#     def __init__(self):
#         self.protocolName = None # 接口名称
#         self.imports = None  # 导入头文件
#         self.requireds = None # 必须的函数数组
#         self.optionals = None # 可选的函数数组
#
#     # 字符串化
#     def toString(self, indent = 0):
#         s = ''
#         # import
#         if (self.imports is not None):
#             for head in self.imports:
#                 s += ST(indent) + head + SN
#         # class name
#         s += SN
#         s += ST(indent) + '@protocol' + ' ' + self.protocolName + SN
#         # interface
#         if (self.requireds is not None):
#             s += ST(indent) + '@required' + SN
#             for meth in self.requireds:
#                 s += ST(indent) + meth.toStringInterface() + ';' + SN + SN
#         if (self.optionals is not None):
#             s += ST(indent) + '@optional' + SN
#             for meth in self.optionals:
#                 s += ST(indent) + meth.toStringInterface() + ';' + SN + SN
#         s += ST(indent) + '@end'
#         return s