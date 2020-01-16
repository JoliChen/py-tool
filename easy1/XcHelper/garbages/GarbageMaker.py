# -*- coding: UTF-8 -*-
# 混淆文件生成器

import os
import random
import time
from XcHelper.garbages.assets.AssetsMaker import JAssetsMaker
from XcHelper.garbages.source.SourceMaker import JSourceMaker
from XcHelper.xcproj.XCodeConfuse import JXCodeConfuse


class JGrabageSetting:
    assets_packages = 10  # 资源包数量
    assets_app_size = 7  # 安装包垃圾文件大小 (MB)
    assets_app_nums = 201  # 安装包的垃圾文件数量
    source_cls_nums = 500  # 混淆代码类数量

    source_methods = (1, 21)
    source_prefixs = ('', '') # 类名前缀
    source_subfixs = ('', '') # 类名后缀
    source_stack_depth = 5
    source_import_less = 1
    opt_swap_lua_api = True # 替换脚本API开关
    opt_pack_res_bin = True # 打包资源开关
    opt_xcode_exists = False # 把现有的资源添加到Xcode里面

class JGarbageMaker:
    def __init__(self, proj_root, proj_name, target_name, build_times, assets_name=None):
        self._proj_root = proj_root
        self._proj_name = proj_name
        self._target_name = target_name
        self._assets_name = assets_name

        self._build_times = build_times # 打包次数
        self._build_float = random.randint(4, 5) * 0.1 # 填充浮动系数

        self._assets_maker = JAssetsMaker()
        self._source_maker = JSourceMaker()
        self._submit_xcode = JXCodeConfuse()

    def build(self):
        self._prepare()
        if not JGrabageSetting.opt_xcode_exists:
            # 打包资源并生成填充文件
            assets_maker = self._assets_maker
            assets_maker.make()
            assets_info = assets_maker.get_assets_info()
            self._assets_maker = None
            # assets_info = None
            # 生成垃圾代码
            source_maker = self._source_maker
            source_maker.make(assets_info)
            self._source_maker = None
        # 将混淆文件添加到Xcode
        self._submit_xcode.apply()

    def _prepare(self):
        random.seed(int(round(time.time() * 1000)))

        vest_root_dir = os.path.join(self._proj_root, 'packing', self._proj_name + '_' + self._target_name)
        assert os.path.exists(vest_root_dir), '"%s" not exist' % vest_root_dir

        confuse_assets_dir = os.path.join(vest_root_dir, 'src', 'assets')  # 混淆资源目录
        confuse_source_dir = os.path.join(vest_root_dir, 'src', 'source')  # 混淆代码目录

        # 设置Xcode参数
        self._submit_xcode.set_scheme(self._proj_root, self._proj_name, self._target_name,
                                      confuse_assets_dir,
                                      confuse_source_dir)

        # 设置代码生成器
        source_maker = self._source_maker
        source_maker.set_dir(confuse_source_dir)
        source_maker.set_class_params(JGrabageSetting.source_prefixs,
                                      JGrabageSetting.source_subfixs,
                                      self._calc_filler_factor(JGrabageSetting.source_cls_nums),
                                      JGrabageSetting.source_methods,
                                      JGrabageSetting.source_stack_depth,
                                      JGrabageSetting.source_import_less,
                                      JGrabageSetting.opt_swap_lua_api)

        # 设置资源生成器
        assets_maker = self._assets_maker
        if JGrabageSetting.opt_pack_res_bin :
            res_dir = os.path.join(vest_root_dir, 'skin')  # 马甲资源目录（如果没有设置成None）
            all_dir = os.path.join(self._proj_root, '..', 'proj.assets')
            src_dir = os.path.join(all_dir, self._assets_name)  # 原始资源目录
            tmp_dir = os.path.join(all_dir, 'build', self._assets_name)  # 临时资源构建目录
            assets_maker.set_dirs(confuse_assets_dir, src_dir, tmp_dir, [res_dir])
            assets_maker.set_package(JGrabageSetting.assets_packages) # 设置资源包数量
        else:
            assets_maker.set_dirs(confuse_assets_dir) # 设置资源处理目录

        # 设置安装包填充资源系数
        assets_maker.set_app_filler(
            self._calc_filler_factor(JGrabageSetting.assets_app_nums),
            self._calc_filler_factor(JGrabageSetting.assets_app_size)
        )

    def _calc_filler_factor(self, base):
        factor = self._build_times * base
        return random.randint(factor, factor + int(self._build_float * base))