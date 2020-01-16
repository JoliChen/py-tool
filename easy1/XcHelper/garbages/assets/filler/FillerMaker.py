# -*- coding: UTF-8 -*-
# 填充文件生成器

import random
from XcHelper.garbages.assets.filler.FillerHelper import JFillerHelper

class JFillerMaker:

    def __init__(self):
        self._fill_size = None  # 资源包的垃圾文件大小默认值 (1024 * 1024 * 10)
        self._fill_filters = None  # 文件类型过滤表
        self._fill_dir_depth = None  # 垃圾文件夹深度
        self._fill_file_nums = None  # 垃圾文件数默认值
        self._fill_dir_tree = None
        self._file_ext_list = None

    def _clean_up(self):
        self._fill_size = None
        self._fill_filters = None
        self._fill_dir_depth = None
        self._fill_file_nums = None
        self._fill_dir_tree = None
        self._file_ext_list = None

    def make_tree(self, fill_dir_path):
        file_ext_list = JFillerHelper.list_file_ext(self._fill_filters, 3, 9)
        print('file_ext_list:%s' % file_ext_list)
        self._file_ext_list = file_ext_list

        fill_dir_nums = random.randint(len(file_ext_list) * random.randint(1, 2), 50)
        fill_dirs = JFillerHelper.make_dir_tree(fill_dir_path, self._fill_dir_depth, fill_dir_nums)
        fill_tree = JFillerHelper.fill_dir_tree(fill_dirs, self._fill_size, self._fill_file_nums, file_ext_list)
        self._fill_dir_tree = fill_tree

    def flush_tree_files(self):
        file_list = []
        fill_tree = self._fill_dir_tree
        if fill_tree is not None:
            dir_count = len(fill_tree)
            for i in range(dir_count):
                folder = fill_tree[i]
                print('%02d/%02d %s\t\t\t\t"%s"' % (i, dir_count, folder.get_ext_list(), folder.get_dir_path()))
                file_list.extend(folder.save_to_disk())
        self._clean_up()
        return file_list

    def rand_file_ext(self):
        return random.choice(self._file_ext_list)

    def get_fill_dir_tree(self):
        return self._fill_dir_tree

    def find_folder_by_ext(self, ext):
        folders = []
        for folder in self._fill_dir_tree:
            if (ext in folder.get_ext_list()):
                folders.append(folder)
        if len(folders) > 0:
            return random.choice(folders)

    def make_bin_filler(self, fill_dir_path, fill_file_nums, fill_size):
        self._fill_size = 1024 * 1024 * fill_size  # 资源包的垃圾文件大小默认值
        self._fill_dir_depth = random.randint(2, 3)  # 垃圾文件夹深度
        self._fill_file_nums = fill_file_nums  # 垃圾文件数默认值
        self._fill_filters = ('', '.mp3')  # 文件类型过滤表 (不要生成mp3类型的文件)

        self.make_tree(fill_dir_path)
        self.flush_tree_files()

    def make_app_filler(self, fill_dir_path, fill_file_nums, fill_size):
        self._fill_dir_depth = random.randint(2, 3)  # 垃圾文件夹深度
        self._fill_file_nums = fill_file_nums  # 垃圾文件数默认值
        self._fill_size = 1024 * 1024 * fill_size  # 资源包的垃圾文件大小默认值
        self._fill_filters = ('', '.cp', '.mi', '.lm', '.lp', '.cl', '.mm', '.py', '.js', '.lua', '.os')  # 文件类型过滤表

        self.make_tree(fill_dir_path)
        # self.flush_tree_files() # don't save on this time