# -*- coding: UTF-8 -*-

# 1 生成资源包里的垃圾文件
# 2 打包资源
# 3 MP3签名
# 4 重命名文件
# 5 生成安装包里的垃圾文件

import os
import random
import shutil
from XcHelper.common.FileUtils import JFileUtils
from XcHelper.common.WordUtils import JWords
from XcHelper.garbages.assets.filler.FillerHelper import JFillerHelper
from XcHelper.garbages.assets.filler.FillerMaker import JFillerMaker
from XcHelper.garbages.assets.tools.SoundsSigner import JSoundsSigner

class JPackageInfo:
    ASSETS_PACKAGE_EXT = '.assetspackage'
    def __init__(self):
        self.pack_bin_path = None  # 资源包路径
        self.pack_bin_sign = None  # 资源包签名串
        self.pack_bin_version = None  # 资源包解析库版本号
        self.pack_bin_compress = 0  # 是否压缩

class JAssetsInfo:
    def __init__(self):
        self.package_list = None # [JPackageInfo]
        self.garbage_list = None # 垃圾文件列表
        self.mapping_dict = None # 资源改名映射表

class JAssetsMaker:
    def __init__(self):
        self._dst_dir = None # 输出目录
        self._src_dir = None # 输入目录
        self._tmp_dir = None # 临时目录

        self._merge_dirs = None
        self._package_nums = None
        self._app_filler_nums = None
        self._app_filler_size = None

        self._junks_maker = JFillerMaker()
        self._assets_info = JAssetsInfo()

    def set_dirs(self, dst_dir, src_dir=None, tmp_dir=None, merge_dirs=None):
        self._dst_dir = dst_dir
        self._src_dir = src_dir
        self._tmp_dir = tmp_dir
        self._merge_dirs = merge_dirs

    def set_app_filler(self, filler_nums, filler_size):
        self._app_filler_nums = filler_nums
        self._app_filler_size = filler_size

    def set_package(self, package_nums):
        self._package_nums = package_nums

    def get_assets_info(self):
        return self._assets_info

    # 开始构建
    def make(self):
        self._prepare()
        self._marge_assets()
        self._pack_assets()
        self._sign_sounds()
        self._rename_assets()
        self._make_filler()

    def _prepare(self):
        JFileUtils.rmdir(self._dst_dir)
        JFileUtils.mkdir(self._dst_dir)

    # 合并资源
    def _marge_assets(self):
        if (self._src_dir is None) or (self._tmp_dir is None):
            return
        print('... coping resource')
        JFileUtils.rmdir(self._tmp_dir)
        JFileUtils.copy_dirs(self._src_dir, self._tmp_dir)
        # 合并马甲资源
        if self._merge_dirs is not None:
            print('... merging resource')
            for res_dir in self._merge_dirs:
                # JFileUtils.merge_dir(res_dir, os.path.join(self._tmp_dir, os.path.basename(res_dir)))
                JFileUtils.merge_dir(res_dir, self._tmp_dir)

    # 包装资源
    def _pack_assets(self):
        if (self._tmp_dir is None) or (self._package_nums is None):
            return
        print('... packaging, nums:', self._package_nums)

        packageInfos = []
        for i in range(self._package_nums):
            pi = JPackageInfo()
            pi.pack_bin_path = JFileUtils.rand_path(self._dst_dir, JPackageInfo.ASSETS_PACKAGE_EXT)
            pi.pack_bin_sign = random.randint(1, 9999999)
            pi.pack_bin_version = random.randint(1, 9999999)
            pi.pack_bin_compress = 0
            packageInfos.append(pi)
        self._assets_info.package_list = packageInfos

        # 把.mp3文件先抽出来
        ignor_count = 0
        root_node_p = len(self._tmp_dir) + 1
        for (root, dirs, files) in os.walk(self._tmp_dir):
            for f in files:
                if (os.path.splitext(f)[1].lower() == '.mp3'):
                    file_path = os.path.join(root, f)
                    dest_node = file_path[root_node_p:]
                    dest_path = os.path.join(self._dst_dir, dest_node)
                    dest_dir = os.path.dirname(dest_path)
                    if not os.path.exists(dest_dir):
                        os.makedirs(dest_dir)
                    shutil.move(file_path, dest_path)
                    ignor_count += 1
        print('packaging strip file:', ignor_count)

        # 生成资源包
        bin_exec = os.path.dirname(os.path.abspath(__file__)) + '/execs/AssetsBinTools'
        cmd = 'exec %s %d %s' % (bin_exec, 1, self._tmp_dir)
        for pi in packageInfos:
            cmd += (' %s %d %d %d' % (pi.pack_bin_path, pi.pack_bin_version, pi.pack_bin_sign, pi.pack_bin_compress))
        print('CMD:', cmd)
        exit_code = os.system(cmd)
        assert exit_code == 0, 'pack assets error:%d' % exit_code

    # 签名声音文件
    def _sign_sounds(self):
        sound_list = []
        JFileUtils.find_files(self._dst_dir, sound_list, ['.mp3'])
        if len(sound_list) < 1:
            return
        author = JWords.hump(5, 10)
        print('... sign sounds, author:', author)
        JSoundsSigner.sign_sounds(sound_list, author)

    # 重命名资源
    def _rename_assets(self):
        # 获取文件列表
        root_dir = self._dst_dir
        file_list = []
        JFileUtils.find_files(root_dir, file_list)
        if len(file_list) < 1:
            return
        print('... renaming')

        # 生成垃圾文件夹结构
        use_junk_tree = False
        file_ext_list = None
        junks_maker = self._junks_maker
        if (self._app_filler_nums > 0) and (self._app_filler_size > 0):
            junks_maker.make_app_filler(root_dir, self._app_filler_nums, self._app_filler_size)
            use_junk_tree = True
        else:
            file_ext_list = []
            for i in range(random.randint(2, 5)):
                file_ext_list.append(JFillerHelper.rand_file_ext())

        # 重命名资源
        name_pos = len(root_dir) + 1
        name_map = {}
        for file in file_list:
            new_path = None
            if use_junk_tree :
                new_ext = junks_maker.rand_file_ext()
                new_dir = junks_maker.find_folder_by_ext(new_ext)
                new_path = new_dir.rand_child_path(new_ext)
            else:
                new_path = JFileUtils.rand_path(root_dir, random.choice(file_ext_list))
            shutil.move(file, new_path)
            new_name = new_path[name_pos:] # 保存引用索引
            if os.path.splitext(file)[1] == JPackageInfo.ASSETS_PACKAGE_EXT:
                for pi in self._assets_info.package_list:
                    if 0 == JFileUtils.compare_path(file, pi.pack_bin_path):
                        pi.pack_bin_path = new_name
                        # print('package: %s' % new_name)
                        break
            else:
                old_name = file[name_pos:]
                name_map[old_name] = new_name
        JFileUtils.delete_gap_dir(root_dir)# 删除空的文件夹
        self._assets_info.mapping_dict = name_map
        print('rename done [%d]' % len(name_map))

    # 生成垃圾文件
    def _make_filler(self):
        if (self._app_filler_nums <= 0) or (self._app_filler_size <= 0):
            return
        print('... filling')
        # 检查是否已生成文件夹结构
        junks_maker = self._junks_maker
        if junks_maker.get_fill_dir_tree() is None:
            junks_maker.make_app_filler(self._dst_dir, self._app_filler_nums, self._app_filler_size)
        # 输出填充文件
        split_pos = len(self._dst_dir) + 1
        file_list = junks_maker.flush_tree_files()
        name_list = []
        for f in file_list:
            if (os.path.getsize(f) > 0):
                name_list.append(f[split_pos:])
            else:
                print('empty file:', f)
        self._assets_info.garbage_list = name_list
