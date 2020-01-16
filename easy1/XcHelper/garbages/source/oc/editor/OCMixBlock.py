# -*- coding: UTF-8 -*-
# 混淆逻辑块

import random
from XcHelper.common.RandUtils import JRand
from XcHelper.garbages.source.oc.OCGrammar import JOcLineTree, ST
from XcHelper.garbages.source.oc.OCHelper import JOcHelper, OC_DIGI
from XcHelper.garbages.source.oc.editor.OCMixHelper import JOcMixHelper


class JOcMixBlock(JOcLineTree):
    def __init__(self, mMethod):
        JOcLineTree.__init__(self, mMethod)
        # self.index = None # 索引

    def randStatement(self, useClasses = None):
        r = JRand.rand_nearest(5)
        if (r == 0):
            self.__make__statement(useClasses)
        elif (r == 1):
            self.__make__if(useClasses)
        elif (r == 2):
            self.__make__while(useClasses)
        elif (r == 3):
            self.__make__for(useClasses)
        elif (r == 4):
            self.__make__switch(useClasses)

    def makeReturn(self):
        if (self.mMethod.ret != 'void'):
            r = JOcMixHelper.makeRet(self.mMethod)
            self.__push__statement('return ' + r + ';')
        else:
            self.__push__statement('return;')

    def __push__statement(self, statement):
        self.statements.append(statement)

    def __make__statement(self, useClasses):
        m = self.mMethod
        if (useClasses is not None):
            for c in useClasses:
                self.__push__statement(JOcMixHelper.callClass(c, m))
        else:
            self.__push__statement(JOcMixHelper.makeStatement(m))

    def __make__if(self, useClasses):
        c1 = JOcHelper.getMethodCondition(self.mMethod)
        s1 = JOcMixBlock(self.mMethod)
        s1.__make__statement(useClasses)
        if (random.random() < 0.3):
            s1.makeReturn()
        self.__push__if(c1, s1)

    def __make__while(self, useClasses):
        c1 = JOcHelper.getMethodCondition(self.mMethod)
        c2 = JOcHelper.getMethodCondition(self.mMethod, True)
        s1 = JOcMixBlock(self.mMethod)
        s2 = JOcMixBlock(self.mMethod)
        s1.__push__if(c2, s2)
        s2.__make__statement(useClasses)
        if (random.random() < 0.3):
            s2.makeReturn()
        else:
            s2.__push__statement('break;')
        self.__push__while(c1, s1)

    def __make__for(self, useClasses):
        c1 = None
        if (random.random() < 0.5):
            c1 = ';;'
        else:
            c1 = ';' + JOcHelper.getMethodCondition(self.mMethod) + ';'
        c2 = JOcHelper.getMethodCondition(self.mMethod, True)
        s1 = JOcMixBlock(self.mMethod)
        s2 = JOcMixBlock(self.mMethod)
        s1.__push__if(c2, s2)
        s2.__make__statement(useClasses)
        if (random.random() < 0.3):
            s2.makeReturn()
        else:
            s2.__push__statement('break;')
        self.__push__for(c1, s1)

    def __make__switch(self, useClasses):
        v1 = self.mMethod.addVarialbe(random.choice(OC_DIGI))
        c1 = '(int)' + v1
        cases = []
        nodes = []
        l = random.randint(2, 10)
        for n in range(l):
            s2 = JOcMixBlock(self.mMethod)
            s2.__make__statement(useClasses)
            cases.append(str(n))
            nodes.append(s2)
        self.__push__switch(c1, cases, nodes)

    def __push__if(self, condition, statement):
        self.__push__statement('if (' + condition + ') {')
        self.__push__statement(statement)
        self.__push__statement('}')

    def __push__while(self, condition, statement):
        self.__push__statement('while (' + condition + ') {')
        self.__push__statement(statement)
        self.__push__statement('}')

    def __push__for(self, condition, statement):
        self.__push__statement('for (' + condition + ') {')
        self.__push__statement(statement)
        self.__push__statement('}')

    def __push__switch(self, condition, cases, statements):
        self.__push__statement('switch (' + condition + ') {')
        case = JOcMixBlock(self.mMethod)
        for i in range(len(cases)):
            case.__push__statement('case ' + cases[i] + ':')
            case.__push__statement(statements[i])
            case.__push__statement(ST(1) + 'break;')
        self.__push__statement(case)
        self.__push__statement('}')