# -*- coding: utf-8 -*-
# @Time    : 2019/3/25 3:53 PM
# @Author  : Joli
# @Email   : 99755349@qq.com

import os
from jonlin.utils import Cross, Text

if Cross.IS_WINDOWS:
    import sys
    import ctypes

# log levels
NONE = 0
ERROR = 1
WARN = 2
INFO = 3
DEBUG = 4

DEFAULT_LEVEL = INFO  # 默认log等级
DEFAULT_SEP = ' '  # 默认拼接分隔符

class Logger:
    def __init__(self, file, level=None):
        self._tag = '[%%s][%s]' % os.path.splitext(os.path.split(file)[1])[0]
        self._level = DEFAULT_LEVEL if level is None else level
        if Cross.IS_WINDOWS:
            self._stdout = ctypes.windll.kernel32.GetStdHandle(-11)

    def _windows_print(self, msg, color=0x07):
        ctypes.windll.kernel32.SetConsoleTextAttribute(self._stdout, color)
        sys.stdout.write(msg + '\n')
        ctypes.windll.kernel32.SetConsoleTextAttribute(self._stdout, 0x07)

    def set_level(self, level):
        self._level = level

    def d(self, *args, sep=None):
        if self._level < DEBUG:
            return
        sep = DEFAULT_SEP if sep is None else sep
        tag = self._tag % 'D'
        print(tag, *args, sep=sep)

    def i(self, *args, sep=None):
        if self._level < INFO:
            return
        sep = DEFAULT_SEP if sep is None else sep
        tag = self._tag % 'I'
        print(tag, *args, sep=sep)

    def w(self, *args, sep=None):
        if self._level < WARN:
            return
        sep = DEFAULT_SEP if sep is None else sep
        tag = self._tag % 'W'
        msg = tag + sep + Text.join(args, sep)
        if Cross.IS_WINDOWS:
            self._windows_print(msg, 0x0e)
        else:
            print('\033[0;33m' + msg + '\033[0m', sep=sep)

    def e(self, *args, sep=None):
        if self._level < ERROR:
            return
        sep = DEFAULT_SEP if sep is None else sep
        tag = self._tag % 'E'
        msg = tag + sep + Text.join(args, sep)
        if Cross.IS_WINDOWS:
            self._windows_print(msg, 0x0c)
        else:
            print('\033[0;31m' + msg + '\033[0m', sep=sep)