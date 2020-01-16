# -*- coding: utf-8 -*-
# @Time    : 2018/10/17 下午6:25
# @Author  : Joli
# @Email   : 99755349@qq.com

import os
from jonlin.utils import FS

class LuacBuilder:
    def __init__(self):
        self._compiler = '/Users/joli/proj/master/xcode/lua/lua_exec/make/luac'

    def compile(self, src_dir, dst_dir, is_debug=False):
        tamplate = '%s -o %s %s' if is_debug else '%s -s -o %s %s'
        tail_pos = len(src_dir) + 1
        for (root, _, files) in os.walk(src_dir):
            for file_name in files:
                if not file_name.endswith('.lua'):
                    continue
                src_file = os.path.join(root, file_name)
                lua_file = src_file[tail_pos:]
                dst_file = os.path.join(dst_dir, lua_file)
                print('compile', lua_file)
                FS.make_parent(dst_file)
                os.system(tamplate % (self._compiler, dst_file, src_file))
        print('compile lua done')
