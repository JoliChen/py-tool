# -*- coding: UTF-8 -*-

import os
import time
import MixRandUtils, MixFileUtils, MixSound, MixCode, MixConfuse

# 资源的根节点
RES_ROOT = 'res'

# 混淆参数
class MixParams:
    def __init__(self):
        self.assetsSrc = None
        self.assetsDst = None
        self.assetsRes = None
        self.assetsName = None
        self.assetsFile = None
        self.codeMainPath = None
        self.codeMixRange = None
        self.packageFiles = None
        self.displayFiles = None
        self.fileSizeArea = None
        self.soundMapping = None

# 资源配置信息
class AssetsInfo:
    def __init__(self):
        self.sign = None
        self.version = None
        self.assetsName = None
        self.soundMapping = None

# 输出混淆代码文件
def outputCodeFile(filesDict, mixDir, appDir):
    cHeader = MixCode.randomClassHeader(1, 48)
    randDir = MixRandUtils.randomDir(1, 4)
    claFile = cHeader.className + '.h'
    fImport = appDir + '/' + randDir + claFile # "include xxx/xxx/xx.h"
    fParent = mixDir + os.sep + appDir + os.sep + randDir
    MixFileUtils.tryMkdir(fParent)
    MixFileUtils.outputText(fParent + claFile, MixCode.buildClassHeader(cHeader))
    filesDict[fImport] = cHeader

# 输出混淆代码壳
def outputMainFile(indexPath, assetsInfo, fileDict):
    MixFileUtils.tryMkdir(os.path.dirname(indexPath))
    MixFileUtils.outputText(indexPath, MixCode.makeMixIndex(indexPath, fileDict, assetsInfo))

# 生成混淆代码
def makeMixCodeFiles(mixDir, mixRange):
    appDir = 'app'
    # 清理混淆内容
    MixFileUtils.tryRmdir(mixDir + os.sep + appDir + os.sep)
    # 混淆代码 start
    filesDict = {}
    fileAmout = MixRandUtils.randNumber(mixRange)
    for i in range(fileAmout) :
        outputCodeFile(filesDict, mixDir, appDir)
        print 'create mix code:' + str(i) + '/' + str(fileAmout)
    # 混淆代码 end
    return filesDict

# 混淆代码
def mixCoding(mixParams, assetsInfo):
    outputMainFile ( # 生成混淆代码壳
        mixParams.codeMainPath,
        assetsInfo,
        # 生成混淆代码
        makeMixCodeFiles(os.path.dirname(mixParams.codeMainPath), mixParams.codeMixRange)
    )

# 打包资源
def packAssets(mixParams):
    # 生成隐藏的混淆文件
    MixConfuse.makePackFiles(mixParams)
    # 构造打包信息
    assetsInfo = AssetsInfo()
    assetsInfo.assetsName = mixParams.assetsName
    assetsInfo.assetsPath = mixParams.assetsDst + os.sep + mixParams.assetsName
    assetsInfo.sign = str(MixRandUtils.randNumber((1000000, 9999999)))
    assetsInfo.version = time.strftime('%Y%m%d%H', time.localtime(time.time()))
    # 打包资源
    os.system('exec %s %s %s %s %s %s' % (
        MixFileUtils.getPacker(),
        assetsInfo.sign,
        assetsInfo.version,
        mixParams.assetsSrc,
        assetsInfo.assetsPath,
        mixParams.assetsDst
    ))
    # 混淆声音文件
    MixSound.main(mixParams, assetsInfo)
    # 生成显示的混淆文件
    MixConfuse.makeShowFiles(mixParams, assetsInfo)
    return assetsInfo

# 入口函数
def main(mixParams):
    print '==================================== [Action START]'
    initTime = time.time()
    import random
    random.seed(initTime)

    print '==================================== [Assets START]'
    partTime = time.time()
    assetsInfo = packAssets(mixParams)
    print '==================================== [Assets END] time:' + str(time.time() - partTime)

    print '==================================== [Coding START]'
    partTime = time.time()
    mixCoding(mixParams, assetsInfo)
    print '==================================== [Coding END] time:' + str(time.time() - partTime)

    print '==================================== [Action END] time:' + str(time.time() - initTime)
