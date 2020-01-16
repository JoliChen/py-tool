# -*- coding: UTF-8 -*-
# 文件工具

import os
import shutil
from XcHelper.common.WordUtils import JWords

class JFileUtils:

    # 比较路径是否一致
    # 0: equal
    # 1: path1 is sub folder of path2
    # -1:path2 is sub folder of path1
    # 2: unrelated
    @staticmethod
    def compare_path(path1, path2):
        if not path1 or not path1:
            return 2
        path1Len = len(path1)
        path2Len = len(path2)
        if path1Len > path2Len:
            longPath = path1
            shortPath = path2
            cmpFator = 1
        else:
            longPath = path2
            shortPath = path1
            cmpFator = -1
        shortPathLen = len(shortPath)
        longPathLen = len(longPath)
        i = 0
        j = 0
        while i < shortPathLen and j < longPathLen:
            c1 = shortPath[i]
            c2 = longPath[j]
            if JFileUtils.is_slash(c1):
                if not JFileUtils.is_slash(c2):
                    return 2
                while i < shortPathLen and JFileUtils.is_slash(shortPath[i]):
                    i += 1
                while j < longPathLen  and JFileUtils.is_slash(longPath[j]):
                    j += 1
            else:
                if c1 != c2:
                    if i == shortPathLen:
                        return cmpFator
                    else:
                        return 2
                i += 1
                j += 1
        if i == shortPathLen:
            if j == longPathLen:
                return 0
            while j < longPathLen:
                if not JFileUtils.is_slash(longPath[j]):
                    return cmpFator
                j += 1
            return 0
        else:
            return 2

    # 判断是否是分隔符
    @staticmethod
    def is_slash(c):
        return c == '/' or c == '\\'

    # 创建文件夹
    @staticmethod
    def mkdir(dir):
        if not os.path.exists(dir):
            os.makedirs(dir)

    # 删除文件夹及所有子文件
    @staticmethod
    def rmdir(dir):
        if os.path.exists(dir):
            shutil.rmtree(dir)

    # 拷贝文件夹及所有子文件
    @staticmethod
    def copy_dirs(src, dst):
        if os.path.exists(src):
            shutil.copytree(src, dst)

    # 随机路径
    @staticmethod
    def rand_path(dir, ext='', left=3, right=9):
        while (True):
            f = os.path.join(dir, JWords.hump(left, right)) + ext
            if not os.path.exists(f):  # 避免覆盖
                return f

    # 合并文件夹
    # src
    # dst
    # symlinks 是否合并符号链接
    @staticmethod
    def merge_dir(src, dst, symlinks=False, ignorHidden=True):
        if not os.path.exists(src):
            print('src dir not exists on mergeing')
            return
        names = os.listdir(src)
        if not os.path.isdir(dst):
            os.makedirs(dst)
        errors = []
        for name in names:
            if ignorHidden and name[0] == '.':
                continue
            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)
            try:
                if symlinks and os.path.islink(srcname):
                    os.symlink(os.readlink(srcname), dstname)
                elif os.path.isdir(srcname):
                    JFileUtils.merge_dir(srcname, dstname, symlinks)
                else:
                    if os.path.isfile(dstname):
                        os.remove(dstname)
                    shutil.copy2(srcname, dstname)
            except (IOError, os.error) as why:
                errors.append((srcname, dstname, str(why)))
            except OSError as err:
                errors.extend(err.args[0])
        if errors:
            raise shutil.Error(errors)

    # 查找文件
    # dir   根目录
    # files 存储列表
    # filters 文件类型
    @staticmethod
    def find_files(dir, files, filters=None):
        if not os.path.exists(dir):
            return
        for f in os.listdir(dir):
            p = os.path.join(dir, f)
            if (os.path.isdir(p)):
                JFileUtils.find_files(p, files, filters)
            elif (os.path.isfile(p)):
                if (filters is not None):
                    if ((os.path.splitext(f)[1]).lower() in filters):
                        files.append(p)
                else:
                    files.append(p)

    # 删除所有空的文件夹
    @staticmethod
    def delete_gap_dir(dir):
        if os.path.isdir(dir):
            for d in os.listdir(dir):
                JFileUtils.delete_gap_dir(os.path.join(dir, d))
            if not os.listdir(dir):
                os.rmdir(dir)
                # print('移除空目录: ' + dir)

    # 输出字节数组到文件
    # @staticmethod
    # def writeBytes(path, bytes):
    #     f = open(path, 'wb')
    #     f.write(bytes)
    #     f.flush()
    #     f.close()

    # 输出字符串
    # @staticmethod
    # def writeString(path, text):
    #     f = open(path, 'w')
    #     f.write(text)
    #     f.flush()
    #     f.close()