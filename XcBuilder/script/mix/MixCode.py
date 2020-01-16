# -*- coding: UTF-8 -*-

# format encode
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import random
import MixRandUtils, MixFileUtils, MixCppHelper

# 行尾符号
LINE_END = '\r\n'

# 函数信息
class MethodInfo:
    def __init__(self):
        self.indent = None
        self.static = None
        self.returnType = None
        self.methodName = None
        self.argsAmount = 0
        self.argumentTypes = []
        self.argumentNames = []
        self.body = None

# 批量函数块
class MethodBlock:
    def __init__(self):
        self.size = None
        self.methods = []

# 类头文件信息
class ClassHeadInfo:
    def __init__(self):
        self.className = None
        self.includes = []
        self.outerBlocks = []
        self.innerBlocks = []

# 类实现文件信息
class ClassImplInfo:
    def __init__(self):
        self.className = None
        self.includes = []
        self.methods = []

# 获取缩进占位符
def indentPlace(indent):
    symbol = ''
    for i in range(indent) :
        symbol += '\t'
    return symbol

# 获取合法的CPP变量名称
def getCppVarName(minLength, maxLength, existVars):
    while True :
        var = MixRandUtils.randomString(minLength, maxLength)
        if MixCppHelper.isNotCppWord(var) :
            if existVars is None :
                return var
            if var not in existVars:
                existVars.append(var)
                return var

# 构建参数内容
def buildArguments(method):
    codeStr = ''
    for i in range(method.argsAmount) :
        argType = method.argumentTypes[i]
        argName = method.argumentNames[i]
        codeStr += ('' if i == 0 else ', ') + argType + ' ' + argName
    return codeStr

# 构建函数代码
def buildMehtod(method):
    codeStr = ''
    codeStr += indentPlace(method.indent) + method.static + ' ' + method.returnType + ' ' + \
               method.methodName + '(' + buildArguments(method) + ')' + '{' + LINE_END
    codeStr += method.body
    codeStr += indentPlace(method.indent) + '}' + LINE_END
    return codeStr

# 构建函数块代码
def buildBlockMethods(blockMethods):
    codeStr = ''
    for i in range(blockMethods.__len__()):
        codeStr += buildMehtod(blockMethods[i])
    return codeStr

# 构建类头文件代码
def buildClassHeader(classHeadInfo):
    codeStr = ''
    codeStr += '#ifndef' + ' ' + classHeadInfo.className.upper() + '_H' + LINE_END
    codeStr += '#define' + ' ' + classHeadInfo.className.upper() + '_H' + LINE_END
    # include start
    for i in range(classHeadInfo.includes.__len__()):
        linkHeader = classHeadInfo.includes[i]
        if cmp(linkHeader[0:2], '//') == 0 :
            codeStr += linkHeader + LINE_END # this line is doc message
        else:
            codeStr += '#include' + ' ' + '\"'  + linkHeader + '\"' + LINE_END
    # include end
    codeStr += 'class' + ' ' + classHeadInfo.className + '{' + LINE_END
    if len(classHeadInfo.outerBlocks) > 0 :
        codeStr += 'public:' + LINE_END
        codeStr += buildBlockMethods(classHeadInfo.outerBlocks)
    if len(classHeadInfo.innerBlocks) > 0 :
        codeStr += 'private:' + LINE_END
        codeStr += buildBlockMethods(classHeadInfo.innerBlocks)
    codeStr += '};' + LINE_END
    codeStr += '#endif'
    return codeStr.encode("utf-8")

# 构建类实现代码
def buildClassImplement(classImplInfo):
    codeStr = ''
    # include start
    for i in range(classImplInfo.includes.__len__()):
        linkHeader = classImplInfo.includes[i]
        if cmp(linkHeader[0:2], '//') == 0 :
            codeStr += linkHeader + LINE_END  # this line is doc message
        else :
            codeStr += '#include' + ' ' +  '\"'  + linkHeader + '\"' + LINE_END
    # include end
    codeStr += '@implementation ' +  classImplInfo.className + LINE_END
    methodAmout = len(classImplInfo.methods)
    if methodAmout > 0 :
        for i in range(methodAmout) :
            method = classImplInfo.methods[i]
            codeStr += method.static + ' (' + method.returnType + ') ' + method.methodName + '{' + LINE_END
            codeStr += method.body
            codeStr += '}' + LINE_END
    codeStr += '@end'
    return codeStr.encode("utf-8")

# 生成随机函数
def randomMethod(minArgs, maxArgs, static, indent):
    varlist = []
    info = MethodInfo()
    info.indent = indent
    info.static = ('static' if static else '')
    info.returnType = MixRandUtils.randomValueType()
    info.methodName = getCppVarName(10, 28, varlist)
    info.argsAmount = random.randint(minArgs, maxArgs)

    for i in range(info.argsAmount):
        argType = MixRandUtils.randomValueType()
        argName = getCppVarName(3, 12, varlist)
        info.argumentTypes.append(argType)
        info.argumentNames.append(argName)

    codeStr = ''
    indent = indent + 1
    varName = getCppVarName(3, 20, varlist)
    # number var = random
    codeStr += randomNumberStatement(indent, varName, info.returnType)
    # var = a + b - c * d / e
    codeStr += randomProcessLogic(indent, varName, randomMathStatement(varName, info));
    # return (number) (a + b - c * d / e)
    codeStr += indentPlace(indent) + 'return ' + varName + ';' + LINE_END

    info.body = codeStr
    return info

# 随机生成逻辑控制
def randomProcessLogic(indent, variable, statement):
    codeStr = ''

    ctrType = MixRandUtils.randNumber((0, 9))
    if (ctrType < 5) :
        codeStr += indentPlace(indent) + 'if (' + variable + MixRandUtils.randomCompare() + \
                   str(MixRandUtils.randNumber((0, 10000))) + ') {' + LINE_END
        codeStr += indentPlace(indent + 1) + statement
    elif (ctrType < 7) :
        codeStr += indentPlace(indent) + 'while (' + variable + MixRandUtils.randomCompare() + \
                   str(MixRandUtils.randNumber((0, 10000))) + ') {' + LINE_END
        codeStr += indentPlace(indent + 1) + statement
        codeStr += indentPlace(indent + 1) + randomEndStatement(variable) + LINE_END
    elif (ctrType < 8):
        codeStr += indentPlace(indent) + 'for(int i=0; i<' + \
                   str(MixRandUtils.randNumber((1, 100))) + '; ++i) {' + LINE_END
        codeStr += indentPlace(indent + 1) + statement
    else:
        codeStr += indentPlace(indent) + 'for (;;) {' + LINE_END
        codeStr += indentPlace(indent + 1) + statement
        codeStr += indentPlace(indent + 1) + randomEndStatement(variable) + LINE_END

    codeStr += indentPlace(indent) + '}' + LINE_END
    return codeStr

# 随机生成 break or return
def randomEndStatement(variable):
    rate = MixRandUtils.randNumber((0, 9))
    if (rate < 6) :
        return 'break;'
    else:
        return 'return ' + variable + ';'

# 生成随机数字初始化语句
def randomNumberStatement(indent, varName, numberType):
    return indentPlace(indent) + numberType + ' ' + varName + ' = ' + \
           str(MixRandUtils.randNumber((0, 10000))) + ';' + LINE_END

# 生成随机数学语句 (var = a + b - c * d / e)
def randomMathStatement(varName, methodInfo):
    codeStr = varName + ' = '
    for i in range(methodInfo.argsAmount):
        codeStr += (MixRandUtils.randomMathSymbol() if i != 0 else '') + methodInfo.argumentNames[i]
    codeStr += ';' + LINE_END
    return codeStr

# 批量生成随机函数
def betchRandMethods(min, max, minArgs, maxArgs):
    block = MethodBlock()
    block.size = random.randint(min, max)
    for i in range(block.size) :
        block.methods.append( randomMethod(minArgs, maxArgs, True, 1) )
    return block

# 生成随机类头文件信息
def randomClassHeader(minMethod, maxMethod):
    headInfo = ClassHeadInfo()
    headInfo.className = getCppVarName(8, 30, None).capitalize()
    headInfo.outerBlocks.append(randomMethod(2, 8, True, 1))
    headInfo.innerBlocks.append(randomMethod(2, 8, True, 1))
    for i in range( random.randint(minMethod, maxMethod) ):
        if random.randint(1, 5) < 4:
            headInfo.outerBlocks.append(randomMethod(2, 8, True, 1))
        else:
            headInfo.innerBlocks.append(randomMethod(2, 8, True, 1))
    return headInfo

############################################## 以下是具体业务实现 ###################################################
# 生成 "初始化AssetsBinManager" 的代码
def makeAssetsConfigs(assetsInfo):
    code = ''
    abmgVar = getCppVarName(3, 12, None)
    pathVar = getCppVarName(3, 12, None)
    code += indentPlace(1) + \
            'AssetsBinManager * ' + abmgVar + ' = AssetsBinManager::getInstance();' + LINE_END
    code += indentPlace(1) + \
            'NSString * ' + pathVar + ' = [[NSBundle mainBundle] pathForResource:' + \
            '@\"' + assetsInfo.assetsName + '\"' + ' ofType:nil];' + LINE_END
    code += indentPlace(1) + 'if (' + pathVar + ' != nil) {' + LINE_END
    code += indentPlace(2) + abmgVar + '->initPackage(' + \
            '[' + pathVar + ' UTF8String], ' + assetsInfo.sign + ', ' + assetsInfo.version + \
            ');' + LINE_END
    code += indentPlace(1) + '}' + LINE_END
    # 写入声音文件名映射
    soundMapping = assetsInfo.soundMapping
    if soundMapping != None :
        for sound in soundMapping:
            code += indentPlace(1) + abmgVar + '->addFileMapping(' + \
                    '\"' + soundMapping[sound] + '\"' + ', ' + '\"' + sound + '\"' + \
                    ');' + LINE_END
    return code

# 调用类的函数
def makeReferHeaderMethod(header, indent):
    code = ''
    method = MixRandUtils.randomItem(header.outerBlocks)
    code += indentPlace(indent) + header.className + '::' + method.methodName + '('
    if method.argsAmount > 0:
        for n in range(method.argsAmount):
            code += ('' if n == 0 else ', ') + str(MixRandUtils.randomValue())
    code += ');' + LINE_END
    return code

# 生成初始化的代码
def makeInitGameContent(assetsInfo, fileDict):
    body = ''
    # 主线程同步调用
    files = fileDict.keys()
    references = []
    referAmount = random.randint(128, 1024)
    assetsIndex = random.randint(int(referAmount*2/7), int(referAmount*5/7))
    for i in range(referAmount) :
        # 随机位置插入资源包初始化
        if i == assetsIndex:
            body += makeAssetsConfigs(assetsInfo)
        # 引用混淆代码
        f = MixRandUtils.randomSelect(files, references)
        references.append(f)
        body += makeReferHeaderMethod(fileDict[f], 1)
    # 从线程串行调用
    phaseAmount = random.randint(66, 666)
    phasesArray = MixRandUtils.div_list(fileDict.keys(), phaseAmount)
    queueVar = getCppVarName(3, 12, None)
    queueNic = getCppVarName(20, 40, None)
    body += indentPlace(1) + 'dispatch_queue_t ' + queueVar + \
            ' = dispatch_queue_create("' + queueNic + '", DISPATCH_QUEUE_SERIAL);' + LINE_END
    for j in range(phaseAmount) :
        phaseLines = phasesArray[j]
        body += indentPlace(1) + 'dispatch_async(' + queueVar + ', ^{' + LINE_END
        for m in range(len(phaseLines)):
            body += makeReferHeaderMethod(fileDict[phaseLines[m]], 2)
        body += indentPlace(1) + '});' + LINE_END
    return body

# 生成混淆代码壳
def makeMixIndex(indexPath, fileDict, assetsInfo):
    indexInfo = ClassImplInfo()
    indexInfo.className = MixFileUtils.getFileName(indexPath)

    # include start
    indexInfo.includes.append(indexInfo.className + '.h')
    mixAmount = len(fileDict)
    if mixAmount > 0:
        abmanagerPos = random.randint(1, mixAmount-1)
        for fpath in fileDict:
            # 随机位置插入
            abmanagerPos -= 1
            if 0 == abmanagerPos:
                indexInfo.includes.append('AssetsBinManager.h')
            # 导入混淆代码
            indexInfo.includes.append(fpath)
    else :
        indexInfo.includes.append('AssetsBinManager.h')
    # include end

    # init method start
    initMethod = MethodInfo()
    initMethod.static = '+'
    initMethod.methodName = 'startGameApp'
    initMethod.returnType = 'void'
    if mixAmount > 0:
        initMethod.body = makeInitGameContent(assetsInfo, fileDict)
    else :
        initMethod.body = makeAssetsConfigs(assetsInfo)
    indexInfo.methods.append(initMethod)
    # init method end

    return buildClassImplement(indexInfo)
