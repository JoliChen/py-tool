# -*- coding: UTF-8 -*-
# 填充文件夹

import os
import random

from XcHelper.common.WordUtils import JWords
from XcHelper.common.RandUtils import JRand
from XcHelper.garbages.assets.filler.FillerFile import JFillerFile


class JFillerFolder:

    def __init__(self, path, size, children, ext_list):
        self._dir_path = path  # 文件夹路径
        self._dir_size = size  # 文件夹磁盘空间大小
        self._children = children  # 文件数量
        self._ext_list = ext_list  # 文件类型列表

    def get_dir_path(self):
        return self._dir_path

    def get_ext_list(self):
        return self._ext_list

    # 随机一个子路径
    def rand_child_path(self, ext=None, left=3, right=15):
        if ext is None:
            ext = random.choice(self._ext_list)
        while (True) :
            f = os.path.join(self._dir_path, JWords.hump(left, right)) + ext
            if not os.path.exists(f):  # 避免覆盖
                return f

    # 输出到磁盘
    def save_to_disk(self):
        files = []
        byte_size = self._dir_size
        for i in range(self._children):
            file_path = self.rand_child_path()
            file_size = JRand.rand_lave(byte_size, self._children, i)
            byte_size -= file_size
            stream = JFillerFile.get_bytes(file_size)

            f = open(file_path, 'wb')
            f.write(stream)
            f.flush()
            f.close()

            files.append(file_path)
        return files