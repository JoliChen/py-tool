# -*- coding: UTF-8 -*-

import os
import random
from XcHelper.common.FileUtils import JFileUtils
from XcHelper.common.WordUtils import JWords
from XcHelper.common.RandUtils import JRand
from XcHelper.garbages.assets.filler.FillerFolder import JFillerFolder


class JFillerHelper:

    @staticmethod
    def rand_file_ext(left=2, min_right=3, right_float=3):
        return '.' + JWords.rand_lowers(left, min_right + JRand.rand_nearest(right_float))

    @staticmethod
    def list_file_ext(filters, left=4, right=12):
        # ext_list = []
        # for i in range(random.randint(left, right)):
        #     while (True):
        #         e = JFillerHelper.rand_file_ext()
        #         if (e not in ext_list) and (e not in filters):
        #             ext_list.append(e)
        #             break
        # return ext_list
        return ['.assetbundle']

    # 创建级联文件夹
    @staticmethod
    def rand_dir_path_by_depth(parent, depth, left=3, right=15):
        dir_path = parent
        for i in range(depth):
            while (True):
                f = os.path.join(dir_path, JWords.hump(left, right))
                if not os.path.exists(f):  # 避免覆盖
                    dir_path = f
                    break
        if (not os.path.exists(dir_path)):
            JFileUtils.mkdir(dir_path)
        return dir_path

    # 创建文件夹树结构
    @staticmethod
    def make_dir_tree(root_dir, depth, nums):
        dirs = []
        depth_map = {}
        for i in range(nums):
            d = JRand.rand_nearest(depth + 1)
            dir_path = None
            if (d > 1):
                levels = None
                if (d in depth_map):
                    levels = depth_map[d]
                    if (random.random() < 0.8):
                        parent = os.path.dirname(random.choice(levels))
                        dir_path = JFillerHelper.rand_dir_path_by_depth(parent, 1)
                        levels.append(dir_path)
                    else:
                        dir_path = JFillerHelper.rand_dir_path_by_depth(root_dir, d)
                        levels.append(dir_path)
                else:
                    dir_path = JFillerHelper.rand_dir_path_by_depth(root_dir, d)
                    levels = [dir_path]
                    depth_map[d] = levels
            else:
                dir_path = root_dir
            if dir_path is not None:
                dirs.append(dir_path)
        return dirs

    # 填充文件夹树
    @staticmethod
    def fill_dir_tree(dirs, byte_size, file_nums, file_ext_list):
        tree = []
        total_dirs = len(dirs)
        chose_flag = True
        copy_ext_list = file_ext_list[:]
        for i in range(total_dirs):
            ext_list = []
            if chose_flag:
                if (len(copy_ext_list) > 0):
                    ext = random.choice(copy_ext_list)
                    ext_list.append(ext)
                    copy_ext_list.remove(ext)
                else:
                    chose_flag = False
                    copy_ext_list = file_ext_list[:]
                    ext_list.append(JRand.chose_nearest(copy_ext_list))
            else:
                ext_list.append(JRand.chose_nearest(copy_ext_list))
            dir_size = JRand.rand_lave(byte_size, total_dirs, i)
            dir_sons = JRand.rand_lave(file_nums, total_dirs, i)
            byte_size -= dir_size
            file_nums -= dir_sons
            tree.append(JFillerFolder(dirs[i], dir_size, dir_sons, ext_list))
        return tree