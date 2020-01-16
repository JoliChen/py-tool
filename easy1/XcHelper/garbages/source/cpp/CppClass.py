# -*- coding: UTF-8 -*-

import random
from XcHelper.garbages.source.oc.OCGrammar import SN, ST

HEADER_STYLE = ('h', 'H', 'hpp', 'HPP')

# CPP基类
class JCppClass:
    def __init__(self):
        self.fileSuffix = '.mm'
        self.head_desc = None  # 文件头说明
        self.className = None  # 类名
        self.interface_macros_map = {}  # 宏集
        self.implement_macros_map = {}  # 宏集
        self.functions = []  # 函数
        self.implement_includes = [] # 导入头文件到实现文件中
        self.interface_includes = [] # 导入头文件到声明文件中

    # 添加头文件
    def add_header_to_implement(self, header_name):
        self.implement_includes.append(header_name)

    # 添加头文件
    def add_header_to_interface(self, header_name):
        self.interface_includes.append(header_name)

    # 添加函数
    def add_function(self, func_name, func_implement):
        self.functions.append((func_name, func_implement))

    # 添加宏
    def add_interface_macros(self, macros_name, macros_define):
        self.interface_macros_map[macros_name] = macros_define

    # 添加宏
    def add_implement_macros(self, macros_name, macros_define):
        self.implement_macros_map[macros_name] = macros_define

    # 生成头文件
    def toStringInterface(self):
        s = ''
        if self.head_desc is not None:
            s += self.head_desc + SN
        pragma_once = self.className + '_' + random.choice(HEADER_STYLE)
        s += '#ifndef ' + pragma_once + SN
        s += '#define ' + pragma_once + SN
        s += SN
        for h in self.interface_includes:
            if h.startswith('<') and h.endswith('>'):
                s += '#include ' + h + SN
            else:
                s += '#include "' + h + '"' + SN
        s += SN

        for macros in self.interface_macros_map:
            s += '#define ' + macros + ' \\' + SN
            s += self.interface_macros_map[macros] + SN
        s += SN

        if len(self.functions) > 0:
            s += 'class ' + self.className + '{' + SN
            s += 'public:' + SN
            for f in self.functions:
                n = len(f) - 1
                s += ST(1) + 'static void ' + f[0] + '('
                if n > 1:
                    for i in range(1, n, 1):
                        s += (', ' if(i != 1) else '') + f[i][0] + ' ' + f[i][1]
                s += ');' + SN
            s += '};' + SN + SN
        s += '#endif /*' + pragma_once + '*/'
        return s

    # 生成实现文件
    def toStringImplement(self):
        s = ''
        if len(self.functions) > 0:
            s += '#include "' + self.className + '.h"' + SN
            for h in self.implement_includes:
                if h.startswith('<') and h.endswith('>'):
                    s += '#include ' + h + SN
                else:
                    s += '#include "' + h + '"' + SN
            s += SN

            for macros in self.implement_macros_map:
                s += '#define ' + macros + ' ' + self.implement_macros_map[macros] + SN
            s += SN

            for f in self.functions:
                n = len(f) - 1
                s += 'void ' + self.className + '::' + f[0] + '('
                if n > 1:
                    for i in range(1, n, 1):
                        s += (', ' if (i != 1) else '') + f[i][0] + ' ' + f[i][1]
                s += ') {' + SN
                s += f[n]
                s += '}' + SN + SN
        return s