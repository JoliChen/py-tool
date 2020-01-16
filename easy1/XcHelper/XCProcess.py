# -*- coding: UTF-8 -*-
# 构建-IPA

import os
import random
from XcHelper.garbages.GarbageMaker import JGarbageMaker, JGrabageSetting
from XcHelper.xcproj.XCodeBuilder import JXcodeBuilder

class JApp:
    SGWWW = '/Users/joli/proj/sdk_uzone/trunk/projects/sgwww/sgwww_xc/xcode'
    HSSG = '/Users/joli/proj/client_hssg/trunk/runtime-src/proj.ios_mac'
    CC52 = '/Users/joli/proj/master/cc25/com.cc25.h5.xc/cc52'

class JRes:
    TEST = 'test'  # 写实测试
    REAL = 'real'  # 写实官版
    SIPU = 'sipu'  # 写实思璞
    SIPU_FANTI = 'sipu_fanti'  # 写实思璞多语言
    SOHA_SG173 = 'soha_173'  # 写实越南
    SOHA_SG211 = 'soha_211'  # 写实越南
    KATONG = 'katong'  # 卡通官版
    KATONG_MINI = 'katong_mini'  # 卡通官版分包
    KATONG_FANTI = 'katong_fanti'  # 卡通官版多语言

class JXCProcess:
    def __init__(self, proj_root, assets_name, proj_name, target_name, build_times):
        self._proj_root = proj_root
        self._proj_name = proj_name
        self._target_name = target_name
        self._assets_name = assets_name
        self._build_times = build_times

        if assets_name is not None :
            JGrabageSetting.opt_pack_res_bin = True
            JGrabageSetting.opt_swap_lua_api = True
        else:
            JGrabageSetting.opt_pack_res_bin = False
            JGrabageSetting.opt_swap_lua_api = False

    # 打包
    def build_signed_ipa(self):
        build_root = os.path.join(os.environ['HOME'], 'desktop/outputs/xcode')
        xb = JXcodeBuilder(self._proj_root, self._proj_name, self._target_name, build_root)
        # xb.build_ipa(os.path.join(build_root, 'archives', '201804172341_app-huowu_ahlm.xcarchive'))
        xb.build_ipa()

    # 混淆
    def build_confuse(self):
        self.configure()
        # JGrabageSetting.opt_xcode_exists = True # 把现有的资源添加到Xcode工程里
        JGarbageMaker(self._proj_root, self._proj_name, self._target_name, self._build_times, self._assets_name).build()

    def configure(self):
        JGrabageSetting.assets_packages = random.randint(1, 3)  # (self._build_times - 1) * 9 + random.randint(1, 9)
        JGrabageSetting.assets_app_size = random.randint(1, 10)
        JGrabageSetting.assets_app_nums = random.randint(50, 200)
        JGrabageSetting.source_cls_nums = random.randint(30, 100)
        JGrabageSetting.source_stack_depth = random.randint(3, 8)
        JGrabageSetting.source_import_less = random.randint(1, 3)
        JGrabageSetting.source_prefixs = ('', '')
        JGrabageSetting.source_subfixs = ('', '')

def get_process():
    # return JXCProcess(JApp.CC52, None, 'cc52', 'fxlove', 2)
    # return JXCProcess(JApp.SGWWW, '29you', 'zskpj', 1, None)
    return JXCProcess(JApp.HSSG, JRes.SIPU_FANTI, 'xiaoqihk', 'zhansanguo', 1)