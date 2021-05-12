# -*- coding: utf-8 -*-
# @Time    : 2019/4/8 5:59 PM
# @Author  : Joli
# @Email   : 99755349@qq.com
# Hardware

import platform

SYSTEM = platform.system()

IS_WINDOWS = IS_MACOSX = IS_LINUX = False
if 'Windows' in SYSTEM:
    IS_WINDOWS = True
elif 'Darwin' in SYSTEM:
    IS_MACOSX = True
elif 'Linux' in SYSTEM:
    IS_LINUX = True