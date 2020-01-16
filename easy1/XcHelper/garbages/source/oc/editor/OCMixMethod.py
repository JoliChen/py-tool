# -*- coding: UTF-8 -*-
# 混淆函数

import random
from XcHelper.common.RandUtils import JRand
from XcHelper.garbages.source.oc.OCGrammar import JOcMethod
from XcHelper.garbages.source.oc.OCHelper import JOcHelper, OC_RET, OC_BASE
from XcHelper.garbages.source.oc.editor.OCMixBlock import JOcMixBlock

class JOcMixMethod(JOcMethod):
    def __init__(self, mClass):
        JOcMethod.__init__(self, mClass)
        # self.index = None # 索引
        self.variables = {}

    # 生成函数声明
    def __make__declare(self):
        var_list = self.variables.keys()
        # 生成指令表
        msgNums = 1 + JRand.rand_nearest(4)  # [1, 5]
        for i in range(msgNums):
            while (True):
                n = JOcHelper.var(self.messages)
                if (n not in var_list):
                    self.messages.append(n)
                    break
        # 生成参数表
        argNums = msgNums if (msgNums != 1) else (0 if (random.random() < 0.5) else 1)
        if (argNums > 0):
            self.argTypes = []
            self.argNames = []
            for i in range(argNums):
                self.argTypes.append(JRand.chose_nearest(OC_BASE))
                while (True):
                    n = JOcHelper.var(self.argNames)
                    if (n not in var_list):
                        self.argNames.append(n)
                        break

    # 生成函数声明
    def makeDeclare(self, scope):
        self.scope = scope
        self.ret = JRand.chose_nearest(OC_RET)
        self.__make__declare()

    # 添加一个局部变量
    def addVarialbe(self, type=None):
        var_list = []
        var_list.extend(self.variables.keys())
        if (self.argNames is not None):
            var_list.extend(self.argNames)
        v = JOcHelper.var(var_list)
        if (type is None):
            type = random.choice(OC_BASE)
        d = JOcHelper.randValue(type)
        self.variables[v] = [type, d]
        return v

    # 生成函数逻辑代码块
    def makeBody(self, refClasses = None):
        # 初始化局部变量
        if (self.argNames is None):
            JOcHelper.randVars(self.variables, 0.00, random.randint(0, 5))
        else:
            JOcHelper.randVars(self.variables, 0.85, JRand.rand_nearest(5))
        # 生成逻辑
        tree = JOcMixBlock(self)
        self.lineTree = tree
        if (refClasses is not None):
            others = refClasses[:]
            n = JRand.rand_int(1, len(refClasses))
            for i in range(n):
                cls = JRand.rand_lave_list(others, n, i, 1)
                tree.randStatement(cls)
        else:
            n = random.randint(1, 3)
            for i in range(n):
                tree.randStatement()
        if (self.ret != 'void'):
            tree.makeReturn()