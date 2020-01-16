# -*- coding: UTF-8 -*-

import random
from XcHelper.common.WordUtils import JWords
from XcHelper.common.RandUtils import JRand

# 浮点数类型
OC_FLOA = ('float',)
# 数字类型
OC_DIGI = ('NSInteger',)
# 基础数据类型
OC_BASE = ('NSString*',) + OC_DIGI + ('BOOL', ) + OC_FLOA + \
          ('NSArray*', 'NSDictionary*', 'NSMutableArray*', 'NSMutableDictionary*', 'const char*')
# 函数返回值数据类型
OC_RET  = ('void',) + OC_BASE
# 布尔值
OC_BOOL = ('YES', 'NO')
# 函数类型
OC_METH = ('+', '-')
# 数学运算符号
OC_MATH = (' + ', ' - ', ' * ', ' / ')
# 逻辑符号
OC_SYML = (' || ', ' && ')
# 真假符号
OC_SYMB = ('', '!')
# 指针比较符号
OC_SYMP = (' == ', ' != ')
# 数值比较符号
OC_SYMN = (' > ', ' < ', ' >= ', ' <= ') + OC_SYMP
# 字符串长度范围
OC_LSTR = (3, 64)
# 集合长度范围
OC_LSET = (1, 5)
# 数字取值范围
OC_LNUM = (-999, 999)
# 链接词
# OC_CONJ = ('and', 'with', 'by', '', 'set', 'refresh', 'update', 'change', 'read', 'write', 'care', 'move',
#            'make', 'build', 'create', 'run', 'start', 'finish', 'restart', 'pause', 'stop',
#            'use', 'do', 'trans', 'to', 'for', 'of')

class JOcHelper:
    CPP_KW = (
        'alignas',
        'alignof',
        'and',
        'and_eq',
        'asm',
        'atomic_cancel',
        'atomic_commit',
        'atomic_noexcept',
        'auto',
        'bitand',
        'bitor',
        'bool',
        'break',
        'case',
        'catch',
        'char',
        'char16_t',
        'char32_t',
        'class',
        'compl',
        'concept',
        'const',
        'constexpr',
        'const_cast',
        'continue',
        'decltype',
        'default',
        'delete',
        'do',
        'double',

        'dynamic_cast',
        'else',
        'enum',
        'explicit',
        'export',
        'extern',
        'false',
        'float',
        'for',
        'friend',
        'goto',
        'if',
        'import',
        'inline',
        'int',
        'long',
        'module',
        'mutable',
        'namespace',
        'new',
        'noexcept',
        'not',
        'not_eq',
        'nullptr',
        'operator',
        'or',
        'or_eq',
        'private',
        'protected',
        'public',
        'register',

        'reinterpret_cast',
        'requires',
        'return',
        'short',
        'signed',
        'sizeof',
        'static',
        'static_assert',
        'static_cast',
        'struct',
        'switch',
        'synchronized',
        'template',
        'this',
        'thread_local',
        'throw',
        'true',
        'try',
        'typedef',
        'typeid',
        'typename',
        'union',
        'unsigned',
        'using',
        'virtual',
        'void',
        'volatile',
        'wchar_t',
        'while',
        'xor',
        'xor_eq',

        'nil', 'null'
        'self', 'super',
        'alloc', 'dealloc',
        'retain', 'release',
        'nonatomic', 'readwrite', 'readonly', 'assign', 'atomic', 'strong', 'copy',
    ) # /* KW */

    # 检查关键字
    @classmethod
    def isKW(cls, w):
        return w in cls.CPP_KW

    # 获取系统单例
    @classmethod
    def getOCSingleton(cls):
        r = random.randint(1, 10)
        if (r == 1):
            return '[[NSBundle mainBundle] infoDictionary]'
        if (r == 2):
            return '[NSUserDefaults standardUserDefaults]'
        if (r == 3):
            return '[NSThread currentThread]'
        if (r == 4):
            return '[NSRunLoop currentRunLoop]'
        if (r == 5):
            return '[NSProcessInfo processInfo]'
        if (r == 6):
            return '[NSFileManager defaultManager]'
        if (r == 7):
            return '[NSNotificationCenter defaultCenter]'
        if (r == 8):
            return '[UIApplication sharedApplication]'
        if (r == 9):
            return '[UIScreen mainScreen]'
        if (r == 10):
            return '[UIDevice currentDevice]'

    # 命名变量
    @classmethod
    def var(cls, ctx = None):
        while True :
            n = JWords.hump(4, 10, False)
            if ((ctx is None) or (n not in ctx)) and (not cls.isKW(n)):
                return n

    # 命名类
    @classmethod
    def cla(cls, ctx = None, prifix = '', suffix = ''):
        while True :
            n = prifix + JWords.hump(4, 10, True) + suffix
            if((ctx is None) or (n not in ctx)) and (not cls.isKW(n)):
                return n

    # 判断数据类型是否是数值类型
    @classmethod
    def isNumber(cls, t):
        return (t in OC_DIGI) or (t in OC_FLOA)

    # 判断是否是浮点数类型
    @classmethod
    def isFloat(cls, t):
        return t in OC_FLOA

    # 判断是否是指针
    @classmethod
    def isPointer(cls, t):
        return '*' in t

    # 获取默认值
    @classmethod
    def randValue(cls, t):
        # OC对象类型
        if t.startswith('NS'):
            if ('NSString*' == t):
                r = random.random()
                if (r < 0.03):
                    return 'nil'
                elif (r < 0.8):
                    s = '@"' + JWords.hump(OC_LSTR[0], OC_LSTR[1], False) + '"'
                    return s
                else:
                    s = '@"' + JWords.hump(OC_LSTR[0], OC_LSTR[1], False) + '"'
                    if (random.random() < 0.5):
                        d = str(random.random() * OC_LNUM[1] * 2 - OC_LNUM[0])
                        return '[NSString stringWithFormat:@"%@_(%f)",' + s + ',' + d + ']'
                    else:
                        d = str(random.randint(OC_LNUM[0], OC_LNUM[1]))
                        return '[NSString stringWithFormat:@"%@_(%d)",' + s + ',' + d + ']'
            if t.endswith('Dictionary*'):
                if (random.random() < 0.5):
                    return 'nil'
                else:
                    s = '[' + t[:-1] + ' dictionaryWithObjectsAndKeys:'
                    if (random.random() < 0.8):
                        for i in range(random.randint(OC_LSET[0], OC_LSET[1])):
                            s += '@(' + str(i) + '),'
                            s += '@"' + JWords.rand_lowers(1, 10) + '",'
                    else:
                        for i in range(random.randint(OC_LSET[0], OC_LSET[1])):
                            s += '@(' + str(i) + '),'
                            s += '@(' + str(i) + '),'
                    s += 'nil]'
                    return s
            if t.endswith('Array*'):
                if (random.random() < 0.5):
                    return 'nil'
                else:
                    s = '[' + t[:-1] + ' arrayWithObjects:'
                    if (random.random() < 0.8):
                        for i in range(random.randint(OC_LSET[0], OC_LSET[1])):
                            s += '@"' + JWords.rand_lowers(1, 10) + '",'
                    else:
                        for i in range(random.randint(OC_LSET[0], OC_LSET[1])):
                            s += '@(' + str(i) + '),'
                    s += 'nil]'
                    return s
        # 布尔值
        if ('BOOL' == t):
            return random.choice(OC_BOOL)
        # 字符数组
        if ('const char*' == t):
            if (random.random() < 0.03):
                return 'NULL'
            else:
                return '"' + JWords.hump(OC_LSTR[0], OC_LSTR[1], False) + '"'
        # 数值类型数据
        if (cls.isFloat(t)):
            f = random.random() * OC_LNUM[1] * 2 - OC_LNUM[0]
            return str(round(f, random.randint(1, 4)))
        else:
            return str(random.randint(OC_LNUM[0], OC_LNUM[1]))

    # 随机断言条件
    @classmethod
    def getMethodCondition(cls, method, onlyTrue = False):
        vars = [] #变量名称表
        cats = [] #变量类型表
        if (method.variables is not None):
            for v, t in method.variables.items():
                vars.append(v)
                cats.append(t[0])
        if (method.argNames is not None):
            vars.extend(method.argNames)
            cats.extend(method.argTypes)
        l = len(vars)
        if (l <= 0):
            if (onlyTrue):
                return 'nil != ' + cls.getOCSingleton()
            else:
                return 'nil' + random.choice(OC_SYMP) + cls.getOCSingleton()
        i = int(random.random() * l)
        v = vars[i]
        t = cats[i]
        if (onlyTrue):
            for i in range(len(vars)):
                if (cls.isPointer(cats[i])) and (random.random() < 0.7):
                    v = vars[i] # 优先使用指针参数作为断言依据
                    t = cats[i]
                    break
            return cls.getTrueCondition(v, t, vars, cats)
        else:
            return cls.getRandCondition(v, t, vars, cats)

    # 从参数中断言条件
    @classmethod
    def getRandCondition(cls, v, t, vars, cats):
        # 布尔参数作为条件
        if ('BOOL' == t):
            return random.choice(OC_SYMB) + v
        # 指针参数作为条件
        if (cls.isPointer(t)):
            if (t.startswith('NS')):
                if (random.random() < 0.2):
                    return 'nil == ' + v + ' || ' + \
                           random.choice(OC_SYMB) + '[%s isKindOfClass:[%s class]]' % (v, 'NSNull')
                else:
                    return 'nil' + random.choice(OC_SYMP) + v
            else:
                if (random.random() < 0.5):
                    return 'NULL ==' + v + ' || ' + \
                           '0' + random.choice(OC_SYMN) + 'strlen(' + v + ')'
                else:
                    return 'NULL' + random.choice(OC_SYMP) + v
        # 数值参数作为条件
        if (random.random() < 0.5):
            vls = []
            for j in range(len(vars)):
                if (vars[j] != v) and cls.isNumber(cats[j]):
                    vls.append(vars[j])
            if (len(vls) > 0):
                return v + random.choice(OC_SYMN) + random.choice(vls)
            else:
                return v + random.choice(OC_SYMN) + str(random.randint(OC_LNUM[0], OC_LNUM[1]))
        else:
            if (random.random() < 0.5):
                return '0' + random.choice(OC_SYMN) + v + \
                       random.choice(OC_SYML) + \
                       '1' + random.choice(OC_SYMN) + v
            else:
                return str(random.randint(-1, 1)) + random.choice(OC_SYMN) + v

    # 获取一个真的断言条件
    @classmethod
    def getTrueCondition(cls, v, t, vars, cats):
        return 'nil != ' + cls.getOCSingleton()

    # 随机一组变量
    @classmethod
    def randVars(cls, var_map, probability, base_num):
        if (base_num <= 0 or random.random() < probability):
            return None
        v_list = []
        for i in range(base_num):
            v = cls.var(v_list)
            v_list.append(v)
            t = random.choice(OC_BASE)
            var_map[v] = (t, cls.randValue(t))
        return var_map