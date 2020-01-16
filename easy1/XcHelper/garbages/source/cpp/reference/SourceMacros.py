# -*- coding: UTF-8 -*-
# 混淆代码替换宏

import random
from XcHelper.common.RandUtils import JRand
from XcHelper.garbages.source.cpp.CppClass import JCppClass
from XcHelper.garbages.source.cpp.reference.cheat.CheatMaker import JCheatMaker
from XcHelper.garbages.source.oc.OCGrammar import ST, SN
from XcHelper.garbages.source.oc.editor.OCMixHelper import JOcMixHelper

class JSourceMacros(JCppClass):
    def __init__(self, lnk_classes, cheater_cls):
        JCppClass.__init__(self)
        self.head_desc = '// 殊途同归'
        self.className = 'JTeacup'
        # 导入头文件
        self.add_header_to_interface(cheater_cls.className + '.h')
        for cls in lnk_classes:
            self.add_header_to_interface(cls.className + '.h')
        # 链接垃圾代码
        self._cheater_cls = cheater_cls
        self._lnk_classes = lnk_classes
        self._ref_link_classes()

    def _ref_link_classes(self):
        self._make_macros_simple('TEA_FinishLaunching_1')
        self._make_macros_simple('TEA_FinishLaunching_2')
        self._make_macros_simple('TEA_WillResignActive_1')
        self._make_macros_simple('TEA_WillResignActive_2')
        self._make_macros_simple('TEA_BecomeActive_1')
        self._make_macros_simple('TEA_BecomeActive_2')
        self._make_macros_simple('TEA_EnterBackground_1')
        self._make_macros_simple('TEA_EnterBackground_2')
        self._make_macros_simple('TEA_WillEnterForeground_1')
        self._make_macros_simple('TEA_WillEnterForeground_2')
        self._make_macros_simple('TEA_ReceiveLocalNotification_1')
        self._make_macros_simple('TEA_ReceiveLocalNotification_2')
        self._make_macros_simple('TEA_ReceiveMemoryWarning_1', 1, 3)
        self._make_macros_simple('TEA_ReceiveMemoryWarning_2', 1, 3)

        self._make_macros_simple('TEA_RootOrientation')
        self._make_macros_simple('TEA_RootShouldAutorotate')
        self._make_macros_simple('TEA_RotateFromInterfaceOrientation_1')
        self._make_macros_simple('TEA_RotateFromInterfaceOrientation_2')

        self._make_macros_simple('TEA_unite_operation_init_1')
        self._make_macros_simple('TEA_unite_operation_init_2')
        self._make_macros_simple('TEA_unite_operation_login_1')
        self._make_macros_simple('TEA_unite_operation_login_2')
        self._make_macros_simple('TEA_unite_operation_logout_1')
        self._make_macros_simple('TEA_unite_operation_logout_2')
        self._make_macros_simple('TEA_unite_operation_pppp_1')
        self._make_macros_simple('TEA_unite_operation_pppp_2')
        self._make_macros_simple('TEA_unite_operation_enter_1')
        self._make_macros_simple('TEA_unite_operation_enter_2')

        self._make_macros_catalogs('TEA_link_catalogs')
        self._make_macros_resource('TEA_init_resource')
        self._make_macros_disk_cheat('TEA_excute_io_stream')
        self._make_macros_net_cheat('TEA_excute_net_stream')


    def _rand_lnk_classes(self, left=1, right=16):
        classes = []
        classes_copy = self._lnk_classes[:]
        weight = JRand.rand_int(left, min(len(classes_copy), right))
        for i in range(weight):
            cls = random.choice(classes_copy)
            classes_copy.remove(cls)
            classes.append(cls)
        return classes

    def _make_macros_simple(self, macros_name, left=1, right=16, indent=1):
        s = ''
        classes = self._rand_lnk_classes(left, right)
        for cls in classes:
            s += ST(indent) + JOcMixHelper.callClass(cls) + ' \\' + SN
        s += ST(indent) + 'NSLog(@"perform ' + macros_name + ' done");' + SN
        self.add_interface_macros(macros_name, s)

    def _make_macros_catalogs(self, macros_name, indent=1):
        s = ''
        s += ST(indent) + 'dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{' + ' \\' + SN
        for cls in self._lnk_classes:
            s += ST(indent+1) + JOcMixHelper.callClass(cls) + ' \\' + SN
        s += ST(indent+1) + 'NSLog(@"perform ' + macros_name + ' done");' + ' \\' + SN
        s += ST(indent) + '});' + SN
        self.add_interface_macros(macros_name, s)

    def _make_macros_resource(self, macros_name, indent=1):
        classes = self._rand_lnk_classes(2)
        pos = JRand.rand_int(0, len(classes)-2)
        s = ''
        for i in range(len(classes)):
            cls = classes[i]
            s += ST(indent) + JOcMixHelper.callClass(cls) + ' \\' + SN
            if i == pos:
                s += ST(indent) + self._cheater_cls.className + '::' + JCheatMaker.get_assets_func() + '();' + ' \\' + SN
        s += ST(indent) + 'NSLog(@"perform ' + macros_name + ' done");' + SN
        self.add_interface_macros(macros_name, s)

    def _make_macros_disk_cheat(self, macros_name, indent=1):
        classes = self._rand_lnk_classes(2)
        pos = JRand.rand_int(0, len(classes) - 2)
        s = ''
        for i in range(len(classes)):
            cls = classes[i]
            s += ST(indent + 1) + JOcMixHelper.callClass(cls) + ' \\' + SN
            if i == pos:
                s += ST(indent) + 'dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{' + ' \\' + SN
                s += ST(indent+1) + self._cheater_cls.className + '::' + JCheatMaker.get_disk_i_func() + '();' + ' \\' + SN
                s += ST(indent+1) + self._cheater_cls.className + '::' + JCheatMaker.get_disk_o_func() + '();' + ' \\' + SN
                s += ST(indent) + '});' + ' \\' + SN
        s += ST(indent + 1) + 'NSLog(@"perform ' + macros_name + ' done");' + SN
        self.add_interface_macros(macros_name, s)

    def _make_macros_net_cheat(self, macros_name, indent=1):
        classes = self._rand_lnk_classes(2)
        pos = JRand.rand_int(0, len(classes) - 2)
        s = ''
        for i in range(len(classes)):
            cls = classes[i]
            s += ST(indent) + JOcMixHelper.callClass(cls) + ' \\' + SN
            if i == pos:
                s += ST(indent) + self._cheater_cls.className + '::' + JCheatMaker.get_net_io_func() + '();' + ' \\' + SN
        s += ST(indent) + 'NSLog(@"perform ' + macros_name + ' done");' + SN
        self.add_interface_macros(macros_name, s)