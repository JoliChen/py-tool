# -*- coding: UTF-8 -*-

import os
import shutil
import struct
import MixRandUtils, MixFileUtils


# 获取一个尚未存在文件
def randomFile(dir, ignors):
    while True :
        t = MixRandUtils.randomFile()
        if t in ignors :
            continue
        f = dir + MixRandUtils.randomString(3, 9) + t
        if not os.path.exists(f) :
            return f

# 随机文件字节
def randomBytes(bytes):
    fmts = ''
    vals = []
    bnum = 0
    while bnum < bytes :
        ctype = MixRandUtils.randomCtype()
        fmts += ctype[0]
        bnum += ctype[1]
        vals.append(MixRandUtils.randNumber(ctype[2]))
    packer = struct.Struct(fmts)
    return packer.pack(*tuple(vals))

# 输出混淆文件
def outputFile(bytes, dir, ignors):
    f = None
    try:
        p = randomFile(dir, ignors)
        f = open(p, 'wb')
        f.write(randomBytes(bytes))
        f.flush()
    finally:
        if f is not None :
            f.close()

# 获取子目录数量
def getChildrenNum() :
    baser = MixRandUtils.randNumber((0, 99))
    if baser < 30:
        return 0
    if baser < 40:
        return 1
    if baser < 50:
        return 2
    if baser < 60:
        return 3
    if baser < 70:
        return 4
    if baser < 80:
        return 5
    if baser < 90:
        return 6
    if baser < 94:
        return 7
    if baser < 97:
        return 8
    if baser < 100:
        return 9
    return 10

# 获取虚拟目录
def getVitruDirs(gendir, depths, nums) :
    predirs = None
    while (predirs is None) or (nums[0] > predirs.__len__()) or (predirs.__len__() > nums[1]) :
        predirs = [gendir]
        depth = MixRandUtils.randNumber(depths)
        for i in range(depth-1) :
            crrdirs = []
            for d in predirs :
                count = 0
                if i == 0 :
                    count = MixRandUtils.randNumber((5, 20))
                else:
                    count = getChildrenNum()
                if count > 0 :
                    for j in range(count) :
                        while True :
                            dir = d + os.sep + MixRandUtils.randomString(3, 9)
                            if dir not in crrdirs :
                                crrdirs.append(dir)
                                break
                else:
                    if d not in crrdirs :
                        crrdirs.append(d)
            predirs = crrdirs
    dirs = []
    for dir in predirs :
        dirs.append(dir + os.sep)
    return dirs

# 生成打包的混淆文件
def makePackFiles(mixParams):
    ignors = ['.mp3']
    dir = mixParams.assetsSrc
    count = MixRandUtils.randNumber(mixParams.packageFiles)
    for i in range(count):
        print "make mix file : %d/%d" % (i, count)
        fdir = dir + os.sep + MixRandUtils.randomDir(0, 2)
        word = MixRandUtils.randNumber(mixParams.fileSizeArea)
        MixFileUtils.tryMkdir(fdir)
        outputFile(word, fdir, ignors)

# 生成显示的混淆文件
def makeShowFiles(mixParams, assetsInfo):
    ignors = []
    # 生成虚拟目录结构
    dirlist = getVitruDirs(mixParams.assetsRes, (2, 4), (20, 60))
    dirnums = dirlist.__len__() - 1
    # 输出混淆文件
    count = MixRandUtils.randNumber(mixParams.displayFiles)
    for i in range(count):
        print "make mix file : %d/%d" % (i, count)
        fdir = dirlist[ MixRandUtils.randNumber((0, dirnums)) ]
        word = MixRandUtils.randNumber(mixParams.fileSizeArea)
        MixFileUtils.tryMkdir(fdir)
        outputFile(word, fdir, ignors)
    # 更换资源包名称
    assetsDir = dirlist[ MixRandUtils.randNumber((0, dirnums)) ]
    assetsPos = assetsDir + mixParams.assetsFile
    shutil.move(assetsInfo.assetsPath, assetsPos)
    assetName = assetsPos[ assetsPos.find('/res/')+1: ]
    assetsInfo.assetsName = assetName