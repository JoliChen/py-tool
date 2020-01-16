# -*- coding: UTF-8 -*-

import os
import sys

def doPublish(xcprojcet, xcscheme, outputDir):
    my__py = os.path.dirname(os.path.abspath(__file__)) + os.sep + 'script/PublishIPA.py'

    my_cmd = 'python %(py)s %(project)s %(scheme)s %(output)s' % \
             {'py': my__py, 'project': xcprojcet, 'scheme': xcscheme, 'output': outputDir}

    os.system(my_cmd)

# 入口函数
def main():
    # 输出目录
    outputDir = '/Users/joli/DeskTop/ipa_outputs'
    # 工程配置
    xcprojcet = '/Users/joli/proj/client_sgwww/trunk/project/xcode/game-sgwww.xcodeproj'
    # 打包目标
    xcscheme  = 'appstore-wltx' if (sys.argv.__len__() < 2) else sys.argv[1]

    doPublish(xcprojcet, xcscheme, outputDir)


if __name__ == '__main__':
    main()