# -*- coding: UTF-8 -*-
# 代码生成器

import os
import random

from XcHelper.common.FileUtils import JFileUtils
from XcHelper.common.RandUtils import JRand
from XcHelper.garbages.source.cpp.reference.SourceCheater import JSourceCheater
from XcHelper.garbages.source.cpp.reference.SourceMacros import JSourceMacros
from XcHelper.garbages.source.oc.configuration.ConfigureScript import JConfigureScript
from XcHelper.garbages.source.oc.editor.OCMixClass import JOcMixClass
from XcHelper.garbages.source.oc.OCHelper import JOcHelper

class JSourceMaker:
    def __init__(self):
        # dirs
        self._source_dir = None # 代码根目录
        self._mix_dirs = None
        self._refs_dir = None
        # make classes params
        self._prifixs = None
        self._subfixs = None
        self._class_nums = 0
        self._method_range = None
        self._swap_lua_api = False
        self._stack_depth = 5
        self._import_less = 1
        self._assets_info = None
        # classes
        self._class_names = []
        self._lnk_classes = []
        self._mix_classes = []
        self._ref_classes = []

    def set_dir(self, source_dir):
        self._source_dir = source_dir

    def set_class_params(self, prifixs, subfixs, class_nums, method_range, stack_depth, import_less, swap_lua_api):
        self._prifixs = prifixs
        self._subfixs = subfixs
        self._class_nums   = class_nums
        self._method_range = method_range
        self._stack_depth  = stack_depth
        self._import_less  = import_less
        self._swap_lua_api = swap_lua_api
        print('ClassPrifixs:%s' % str(prifixs))
        print('ClassSubfixs:%s' % str(subfixs))

    # 开始生成代码
    def make(self, assets_info=None):
        self._assets_info = assets_info
        self._prepare()
        self._build_mix()
        self._build_ref()
        self._flush_to_disk()

    # 准备工作
    def _prepare(self):
        JFileUtils.rmdir(self._source_dir)

        mix_dirs = []
        for i in range(random.randint(1, 21)):
            d = os.path.join(self._source_dir, JOcHelper.var(self._mix_dirs))
            JFileUtils.mkdir(d)
            mix_dirs.append(d)
        self._mix_dirs = mix_dirs

        refs_dir = os.path.join(self._source_dir, JOcHelper.var())
        JFileUtils.mkdir(refs_dir)
        self._refs_dir = refs_dir

    # 随机类名
    def _rand_cls_name(self):
        p = random.choice(self._prifixs)
        s = random.choice(self._subfixs)
        n = JOcHelper.cla(self._class_names, p, s)
        self._class_names.append(n)
        return n

    # 随机代码
    def _build_mix(self):
        cls_num = self._class_nums
        import_less = self._import_less
        stack_depth = self._stack_depth
        cls_phase_set = []
        for i in range(stack_depth, 0, -1):
            slice_num = 0
            if i == 0:
                slice_num = cls_num
            else:
                slice_num = JRand.rand_int(import_less, min(int(cls_num / i * 2 - import_less), cls_num))
            if slice_num > 0:
                slice_cls_set = []
                for n in range(slice_num):
                    cls = JOcMixClass(self._rand_cls_name())
                    self._mix_classes.append(cls)
                    slice_cls_set.append(cls)
                cls_phase_set.append(slice_cls_set)
                # print('slice_num=%d' % slice_num)
            cls_num -= slice_num

        lnk_set = cls_phase_set[0]
        self._lnk_classes.extend(lnk_set)
        for i in range(1, stack_depth, 1):
            ref_set = cls_phase_set[i]
            if len(ref_set) < len(lnk_set):
                self._duplicate_includes(lnk_set, ref_set)
            else:
                self._averaging_includes(lnk_set, ref_set)
            lnk_set = ref_set

        method_range = self._method_range
        for cls in self._mix_classes:
            cls.makeClsDeclare(JRand.rand_int(method_range[0], method_range[1]))
        for cls in self._mix_classes:
            cls.makeClsMixCode()

    # 随机复用引用
    def _duplicate_includes(self, lnk_set, ref_set):
        dup_ref_set = ref_set[:]
        for n in range(len(lnk_set)):
            lnk_ref_num = JRand.rand_int(1, min(len(dup_ref_set), 19))
            lnk_ref_set = []
            for m in range(lnk_ref_num):
                cls = random.choice(dup_ref_set)
                dup_ref_set.remove(cls)
                lnk_ref_set.append(cls)
            lnk_set[n].setIncludes(lnk_ref_set)
            if len(dup_ref_set) == 0:
                dup_ref_set = ref_set[:]

    # 均等分配引用
    def _averaging_includes(self, lnk_set, ref_set):
        dup_ref_set = ref_set[:]
        for n in range(len(lnk_set), 0, -1):
            lnk_ref_set = []
            ref_num = 0
            dup_num = len(dup_ref_set)
            if n == 0 :
                ref_num = dup_num
            else:
                ref_num = JRand.rand_int(1, min(int(dup_num / n * 2 - 1), dup_num))
            for m in range(ref_num):
                cls = random.choice(dup_ref_set)
                dup_ref_set.remove(cls)
                lnk_ref_set.append(cls)
            if (ref_num < 5) and (random.random() < 0.5):
                sel_set = []
                for cls in ref_set:
                    if cls not in lnk_ref_set:
                        sel_set.append(cls)
                sel_num = len(sel_set)
                if sel_num > 0:
                    for m in range(JRand.rand_int(1, min(sel_num, 9))):
                        cls = random.choice(sel_set)
                        sel_set.remove(cls)
                        lnk_ref_set.append(cls)
            lnk_set[n-1].setIncludes(lnk_ref_set)

    # 引用代码
    def _build_ref(self):
        oc_bridge_cls = None
        if (self._swap_lua_api):
            oc_bridge_cls = JConfigureScript(self._rand_cls_name())
            self._mix_classes.append(oc_bridge_cls)
        cheater_cls = JSourceCheater(self._assets_info, oc_bridge_cls)
        self._ref_classes.append(cheater_cls)
        macros_cls  = JSourceMacros(self._lnk_classes, cheater_cls)
        self._ref_classes.append(macros_cls)

    def _flush_to_disk(self):
        total_nums = len(self._ref_classes) + len(self._mix_classes)
        save_index = 0
        # 输出混淆代码
        for cls in self._mix_classes:
            mix_dir = random.choice(self._mix_dirs)
            f = os.path.join(mix_dir, cls.className)
            self.save_file(f + '.h', cls.toStringInterface())
            self.save_file(f + cls.fileSuffix, cls.toStringImplement())
            save_index += 1
            # print('%04d/%04d MixClass:%s' % (save_index, total_nums, cls.className))
        print('%04d/%04d MixClass' % (save_index, total_nums))
        # 输出引用代码
        for cls in self._ref_classes:
            f = os.path.join(self._refs_dir, cls.className)
            self.save_file(f + '.h', cls.toStringInterface())
            implement = cls.toStringImplement()
            if len(implement) > 0:
                self.save_file(f + cls.fileSuffix, implement)
            save_index += 1
            print('%04d/%04d RefClass:%s' % (save_index, total_nums, cls.className))
        print('ref_dir:%s' % self._refs_dir)

    @staticmethod
    def save_file(path, content):
        f = open(path, 'w')
        f.write(content)
        f.flush()
        f.close()