# -*- coding: UTF-8 -*-

import os
import time
from enum import Enum
from script.mix import MixSource, MixFileUtils, MixRandUtils

class Bundle(Enum):
    REAL_TEST = 'real_test' #写实测试
    REAL_ORIG = 'real_orig' #写实官版
    REAL_SIPU = 'real_sipu' #写实思璞
    REAL_SOHA = 'real_soha' #写实越南
    KATO_TEST = 'kato_test' #卡通测试
    KATO_ORIG = 'kato_orig' #卡通官版
    KATO_ORIG_SMALL = 'kato_orig_small' #卡通官版分包

# 拷贝马甲资源
def copySkinRes(skinName, projectDir, toDir, resDir):
    toDir = toDir + os.sep + resDir + os.sep
    fromDir = projectDir + '/packing/' + skinName + os.sep + resDir + os.sep

    if not os.path.exists(fromDir) :
        skinName = skinName.replace('-', '_')
        fromDir = projectDir + '/packing/' + skinName + os.sep + resDir + os.sep

    if not os.path.exists(fromDir) :
        raise IOError

    os.system('cp -a "%s" "%s"' % (fromDir, toDir))
    print 'override skin : ' + fromDir

# 开始任务
def start(bundle, projectDir, skinName, gIndexPath) :
    # 拷贝原始资源到构建目录
    orgDir = projectDir + '/../proj.assets/' + bundle
    srcDir = projectDir + '/../proj.assets/build/' + bundle
    dstDir = projectDir + '/assets/' + bundle
    MixFileUtils.tryRmdir(srcDir)
    MixFileUtils.tryCopyDir(orgDir, srcDir)
    # 拷贝非裸包资源
    if bundle is Bundle.REAL_TEST or bundle is Bundle.KATO_TEST :
        pass
    else:
        copySkinRes(skinName, projectDir, srcDir, MixSource.RES_ROOT)
    # 生成混淆代码
    mixParams = MixSource.MixParams()
    mixParams.assetsSrc = srcDir
    mixParams.assetsDst = dstDir
    mixParams.assetsRes = dstDir + os.sep + MixSource.RES_ROOT
    mixParams.assetsFile = MixRandUtils.randomString(10, 20) + MixRandUtils.randomFile()
    mixParams.assetsName = MixSource.RES_ROOT + os.sep + mixParams.assetsFile
    mixParams.codeMainPath = gIndexPath
    # mixParams.codeMixRange = (15000, 20000)
    # mixParams.packageFiles = (200, 800)
    # mixParams.displayFiles = (300, 1500)
    mixParams.codeMixRange = (8000, 10000)
    mixParams.packageFiles = (300, 500)
    mixParams.displayFiles = (400, 500)
    mixParams.fileSizeArea = (int(1024 * 0.1), int(1024 * 20))
    mixParams.soundMapping = True
    MixSource.main(mixParams)

# 入口函数
def main() :
    projectDir = '/Users/joli/proj/client_hssg/trunk/runtime-src/proj.ios_mac'
    gIndexPath = projectDir + '/ios/joli/GameIndex.mm'
    # projectDir = '/Users/joli/proj/client_hssg_quick/trunk/runtime-src/proj.ios_mac'
    # gIndexPath = projectDir + '/ios/joli/GameUzoneIOS.mm'

    scheme = 'cartoon_yxwz'
    bundle = Bundle.KATO_ORIG_SMALL
    start(bundle, projectDir, scheme, gIndexPath)

    print 'make《%s》resource [%s]' % (scheme, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))

if __name__ == '__main__':
    main()