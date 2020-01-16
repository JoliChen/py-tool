# -*- coding: UTF-8 -*-

import os
import sys
import time
import shutil


# 清理目录
def cleanDirectory(dir):
    if not os.path.exists(dir):
        return
    shutil.rmtree(dir)

# 导出ipa包
def doExportIpa(xcproject, xcscheme, outputDir):
    # 当前日期
    todayDate = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
    print 'todayIs : ' + todayDate
    # 配置目录
    configsDir = os.path.dirname(os.path.abspath(__file__)) + os.sep + 'configs'
    print 'configs : ' + configsDir

    # dev-coinfg
    devIpaConf = configsDir + os.sep + 'export_ipa_dev.plist'
    # dis-coinfg
    disIpaConf = configsDir + os.sep + 'export_ipa_dis.plist'
    # ipa输出目录
    ipaOutputs = outputDir + os.sep + 'ipa'
    # dev-ipa 输出路径
    devIpaPath = ipaOutputs + os.sep + xcscheme + '-dev'
    # dis-ipa 输出路径
    disIpaPath = ipaOutputs + os.sep + xcscheme + '-dis'
    # Archive包输出路径
    archivePath = outputDir + os.sep + 'archive' + os.sep + xcscheme + "-" + todayDate + '.xcarchive'

    # 清理发布目录
    cleanDirectory(ipaOutputs)

    # 构建命令
    cmdClean = 'xcodebuild clean -project %(project)s -scheme %(scheme)s -configuration Release' % \
               {'project': xcproject, 'scheme': xcscheme}

    cmdBuild = 'xcodebuild archive -project %(project)s -scheme %(scheme)s -configuration Release -archivePath %(output)s' % \
               {'project': xcproject, 'scheme': xcscheme, 'output': archivePath}

    cmdExDev = 'xcodebuild -exportArchive -exportOptionsPlist %(plist)s -archivePath %(archive)s -exportPath %(output)s' % \
               {'plist': devIpaConf, 'archive': archivePath, 'output': devIpaPath}

    cmdExDis = 'xcodebuild -exportArchive -exportOptionsPlist %(plist)s -archivePath %(archive)s -exportPath %(output)s' % \
               {'plist': disIpaConf, 'archive': archivePath, 'output': disIpaPath}

    # 执行命令
    os.system('python -V')
    os.system('xcodebuild -version')
    print '[clean] ================================================================='
    os.system(cmdClean)
    print '[archive] ==============================================================='
    os.system(cmdBuild)
    print '[export dev ipa] ========================================================'
    os.system(cmdExDev)
    print '[export dis ipa] ========================================================'
    os.system(cmdExDis)
    print '[action done] ==========================================================='

# 入口函数
def main():
    xcproject = sys.argv[1]
    xcscheme  = sys.argv[2]
    outputDir = sys.argv[3]

    print 'project : ' + xcproject
    print 'scheme  : ' + xcscheme
    print 'outputs : ' + outputDir

    doExportIpa(xcproject, xcscheme, outputDir)


if __name__ == '__main__':
    main()





