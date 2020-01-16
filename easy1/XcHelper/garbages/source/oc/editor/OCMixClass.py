# -*- coding: UTF-8 -*-
# 混淆代码基类

import random
from XcHelper.common.RandUtils import JRand
from XcHelper.garbages.source.oc.OCGrammar import JOcClass
from XcHelper.garbages.source.oc.OCHelper import JOcHelper, OC_METH
from XcHelper.garbages.source.oc.editor.OCMixHelper import JOcMixHelper
from XcHelper.garbages.source.oc.editor.OCMixMethod import JOcMixMethod

class JOcMixClass(JOcClass):
    def __init__(self, className, baseClass = None, protocol = None):
        JOcClass.__init__(self, className, baseClass, protocol)
        self.imports = []
        self.variables = {}
        self._include_classes = None  # 引用的类数组
        JOcHelper.randVars(self.variables, 0.85, JRand.rand_nearest(8))# 初始化私有类变量

    # 设置引用的类
    def setIncludes(self, classes):
        self._include_classes = classes
        # 添加引用类的导入
        for cls in classes:
            self.imports.append(cls.className + '.h')
        # 添加私有变量
        if (random.random() < 0.3):
            for cls in classes:
                n = JOcHelper.var(self.variables.keys())
                self.variables[n] = (cls.className + '*', None)

    # 调用引用的类
    def useOtherClass(self, fromMeth):
        uses = self._include_classes
        if (uses is None):
            return None
        c = random.choice(uses)
        return JOcMixHelper.callClass(c, fromMeth)

    # 生成类声明
    def makeClsDeclare(self, radix):
        methods = self.methods
        if (methods is None):
            methods = []
            self.methods = methods
        flag = False # 是否有静态函数的标记
        size = radix - JRand.rand_nearest(radix) + 1
        for i in range(size):
            m = JOcMixMethod(self)
            m.index = i
            methods.append(m)
            scope = None
            if (i == size - 1) and (not flag):
                scope = '+' # 强制添加一个静态函数
            else:
                scope = random.choice(OC_METH)
                if (JOcMixHelper.isClassMethod(scope)):
                    flag = True
            m.makeDeclare(scope)

    # 生成类实现代码
    def makeClsMixCode(self):
        if (self._include_classes is not None):
            copyArray = None
            t = len(self._include_classes)
            n = len(self.methods)
            for i in range(n):
                m = self.methods[i]
                if (copyArray is None) or (len(copyArray) <= 0):
                    copyArray = self._include_classes[:]
                classes = JRand.rand_lave_list(copyArray, n, i, JRand.rand_int(1, t))
                m.makeBody(classes)
        else:
            for m in self.methods:
                m.makeBody()