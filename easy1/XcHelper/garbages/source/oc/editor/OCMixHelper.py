# -*- coding: UTF-8 -*-
# 编辑器辅助工具

import random
from XcHelper.garbages.source.oc.OCHelper import JOcHelper, OC_MATH

class JOcMixHelper:
    # 判断是否类函数
    @staticmethod
    def isClassMethod(scope):
        return scope == '+'

    # 调用类中的任意静态函数
    @staticmethod
    def callClass(cl, fromMeth = None):
        if (cl.methods is None):
            return ''
        statics = []
        for meth in cl.methods:
            if (JOcMixHelper.isClassMethod(meth.scope)):
                statics.append(meth)
        meth = statics[int(random.random() * len(statics))]
        return JOcMixHelper.callMethod(meth, cl, fromMeth)

    # 调用函数
    @staticmethod
    def callMethod(meth, cl = None, fromMeth = None):
        s = ('[' + cl.className) if (cl is not None) else ''
        vard = None if (fromMeth is None) else JOcMixHelper.getVisibleVars(fromMeth)
        msgs = meth.messages
        args = meth.argTypes
        for i in range(len(msgs)):
            s += ' ' + msgs[i]
            if (args is not None):
                t = args[i]
                if (vard is not None):
                    vars = vard.get(t)
                    if (vars is not None):
                        s += ':' + vars[int(random.random() * len(vars))]
                        continue
                s += ':' + JOcHelper.randValue(t)
        s += '];'
        return s

    # 查找返回的数据
    @staticmethod
    def makeRet(meth):
        vars = []
        r = meth.ret
        if (meth.variables is not None):
            for v in meth.variables:
                t = meth.variables[v][0]
                if (t == r):
                    vars.append(v)
                elif (JOcHelper.isNumber(r) and JOcHelper.isNumber(t)):
                    vars.append('(' + r + ')' + v)
        if (meth.argNames is not None):
            for i in range(len(meth.argNames)):
                t = meth.argTypes[i]
                if (t == r):
                    vars.append(meth.argNames[i])
                elif (JOcHelper.isNumber(r) and JOcHelper.isNumber(t)):
                    vars.append('(' + r + ')' + meth.argNames[i])
        if len(vars) > 0:
            return random.choice(vars)
        else:
            return JOcHelper.randValue(r)

    # 生成普通逻辑
    @staticmethod
    def makeStatement(meth):
        # 赋值语句
        s = JOcMixHelper.makeAssignState(meth)
        if (s is not None):
            return s
        # 数学运算
        s = JOcMixHelper.mekeMathState(meth)
        if (s is not None):
            return s
        # 调用引用的类
        s = meth.mClass.useOtherClass(meth)
        if (s is not None):
            return s
        # 永远不报错
        return JOcHelper.getOCSingleton() + ';'

    # 生成数学运算式
    @staticmethod
    def mekeMathState(meth):
        vars = []
        cats = []
        if (meth.variables is not None):
            for v in meth.variables:
                t = meth.variables[v][0]
                if (JOcHelper.isNumber(t)):
                    vars.append(v)
                    cats.append(t)
        if (meth.argNames is not None):
            for i in range(len(meth.argNames)):
                t = meth.argTypes[i]
                if (JOcHelper.isNumber(t)):
                    vars.append(meth.argNames[i])
                    cats.append(t)
        if (len(vars) == 1):
            v = vars[0]
            r = random.random()
            if (r < 0.2):
                return v + random.choice(('++', '--')) + ';'
            elif (r < 0.5):
                return random.choice(('++', '--')) + v + ';'
            elif (r < 0.8):
                return v + ' ' + random.choice(('+', '-', '*')) + '= ' + v + ';'
            else:
                return v + ' = ' + v + random.choice(OC_MATH) + str(random.randint(2, 10)) + ';'
        elif (len(vars) > 1):
            i = int(random.random() * len(vars))
            v = vars[i]
            s = v + ' = (' + cats[i] + ') ('
            for i in range(len(vars)):
                v = vars[i]
                s += v if (i == 0) else (random.choice(OC_MATH) + v)
            s += ');'
            return s

    # 生成赋值语句
    @staticmethod
    def makeAssignState(meth):
        r = random.random() * 10
        if (r < 2):
            # 参数赋值
            if (meth.argNames is not None):
                i = int(random.random() * len(meth.argNames))
                v = meth.argNames[i]
                d = JOcHelper.randValue(meth.argTypes[i])
                return v + ' = ' + d + ';'
        elif (r < 4):
            # 局部变量赋值
            var_map = meth.variables
            if (var_map is not None) and (len(var_map) > 0):
                v = random.choice(list(var_map.keys()))
                d = JOcHelper.randValue(var_map[v][0])
                # meth.variables[v][1] = d
                return v + ' = ' + d + ';'
        elif (r < 6):
            # 类变量赋值
            var_map = meth.mClass.variables
            if (var_map is not None) and (len(var_map) > 0) and (not JOcMixHelper.isClassMethod(meth.scope)):
                v = random.choice(list(var_map.keys()))
                d = JOcHelper.randValue(var_map[v][0])
                # meth.mClass.variables[v][1] = d
                return v + ' = ' + d + ';'
        elif (r < 9):
            # 变量互相赋值
            tdict = JOcMixHelper.getVisibleVars(meth)
            # for t in tdict:
            #     if (t.startswith('const')):
            #         tdict[t] = [] # 去除常量，因为常量不能赋值。
            vls = list(tdict.values())
            for i in range(len(vls)-1, -1, -1):
                if (vls[i] is None) or (len(vls[i]) < 2):
                    del vls[i]
            if (len(vls) > 0):
                vls = vls[int(random.random() * len(vls))]
                i = int(random.random() * len(vls))
                v1 = vls[i]
                del vls[i]
                i = int(random.random() * len(vls))
                v2 = vls[i]
                return v1 + ' = ' + v2 + ';'

    # 获取函数可见变量表
    @staticmethod
    def getVisibleVars(meth):
        tdict = {}
        if (meth.argNames is not None):
            for i in range(len(meth.argNames)):
                t = meth.argTypes[i]
                if (tdict.get(t) is None):
                    tdict[t] = []
                tdict[t].append(meth.argNames[i])
        if (meth.variables is not None):
            for v in meth.variables:
                t = meth.variables[v][0]
                if (tdict.get(t) is None):
                    tdict[t] = []
                tdict[t].append(v)
        if (meth.mClass.variables is not None) and (not JOcMixHelper.isClassMethod(meth.scope)):
            for v in meth.mClass.variables:
                t = meth.mClass.variables[v][0]
                if (tdict.get(t) is None):
                    tdict[t] = []
                tdict[t].append(v)
        return tdict