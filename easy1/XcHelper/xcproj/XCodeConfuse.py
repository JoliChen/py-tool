# -*- coding: UTF-8 -*-
# 提交垃圾内容

import os
import time
from XcHelper.xcproj.XCodeProj import JXCodeProj

class JXCodeConfuse:
    def __init__(self):
        self._proj_root = None
        self._proj_name = None
        self._target_name = None
        self._confuse_source_dir = None
        self._confuse_assets_dir = None
        self._xcode = None # xcode工程配置
        self._confuse_group = None # 混淆组

    def set_scheme(self, proj_root, proj_name, target_name, confuse_assets_dir, confuse_source_dir):
        self._proj_root = proj_root
        self._proj_name = proj_name
        self._target_name = target_name
        self._confuse_assets_dir = confuse_assets_dir
        self._confuse_source_dir = confuse_source_dir

    # 把混淆内容添加到xcode里
    def apply(self):
        print('loading xcodeproj')
        self._xcode = JXCodeProj(os.path.join(self._proj_root, '%s.xcodeproj' % self._proj_name))
        self._init_confuse_group(os.path.split(self._confuse_source_dir)[0])
        print('load xcodeproj done')
        print('--------------------------------------------')

        print('adding srouce files')
        self._add_source_files(self._confuse_source_dir)
        print('add srouce files done')
        print('--------------------------------------------')

        print('adding assets files')
        self._add_assets_files(self._confuse_assets_dir)
        print('add assets files done')
        print('--------------------------------------------')

        use_time = time.time()
        print('saving xcodeproj')
        self._xcode.safe_save()
        print('save xcodeproj done [%f]' % (time.time() - use_time))
        print('--------------------------------------------')

    # 初始化混淆目录
    def _init_confuse_group(self, confuse_root_dir):
        xc_vest_group = self._xcode.get_group_by_path(os.path.split(confuse_root_dir)[0])
        assert xc_vest_group is not None, 'vest group not exist'

        confuse_group = self._xcode.get_or_create_group(confuse_root_dir, xc_vest_group)
        assert confuse_group is not None, 'confuse group not exist'

        self._confuse_group = confuse_group

    # 添加混淆资源
    def _add_assets_files(self, confuse_assets_dir):
        is_ok = self._xcode.remove_group_by_path(confuse_assets_dir, self._confuse_group)
        assert is_ok, 'remove assets group failed'

        xc_assets_group = self._xcode.create_group(confuse_assets_dir, self._confuse_group)
        assert xc_assets_group is not None, 'create assets group failed'

        count = self._xcode.add_folder_reference(confuse_assets_dir, xc_assets_group, self._target_name)
        print('added assets to xcode : %d' % count)

    # 添加混淆代码
    def _add_source_files(self, confuse_source_dir):
        is_ok = self._xcode.remove_group_by_path(confuse_source_dir, self._confuse_group)
        assert is_ok, 'remove source group failed'

        count = self._xcode.add_folder_group(confuse_source_dir, self._confuse_group, self._target_name)
        print('added source to xcode : %d' % count)