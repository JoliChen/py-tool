# -*- coding: UTF-8 -*-

import os
import shutil

# 尝试创建文件夹
def tryMkdir(dir):
    if not os.path.exists(dir) :
        os.makedirs(dir)

# 尝试删除文件夹
def tryRmdir(dir):
    if os.path.exists(dir) :
        shutil.rmtree(dir)

# 清空文件夹
def tryCleanDir(dir):
    if not os.path.exists(dir):
        return
    filelist = os.listdir(dir)
    for f in filelist:
        filepath = os.path.join(dir, f)
        if os.path.isfile(filepath):
            os.remove(filepath)
        elif os.path.isdir(filepath):
            shutil.rmtree(filepath, True)

# 拷贝目录
def tryCopyDir(src, dst):
    if not os.path.exists(src):
        return
    shutil.copytree(src, dst)

# 获取文件夹下的文件列表
def listfiles(dir, flist):
    files = os.listdir(dir)
    for f in files :
        child = dir + os.sep + f
        if (os.path.isdir(child)) :
            listfiles(child, flist)
        elif (os.path.isfile(child)) :
            flist.append(child)

# 获取文件名称，不包括后缀。
def getFileName(path):
    fname = os.path.basename(path)
    ptpos = fname.rfind('.')
    return (fname if ptpos == -1 else fname[0:ptpos])

# 获取执行程序目录
def getExecDir():
    return os.path.dirname(os.path.abspath(__file__)) + os.sep + 'executable'

# 获取资源打包程序路径
def getPacker():
    return getExecDir() + os.sep + 'AssetsBinTools'

# 输出文本
def outputText(filePath, content):
    f = None
    try:
        f = open(filePath, 'w')
        f.write(content)
        f.flush()
    finally:
        if f is not None :
            f.close()

# 读取文本
def readText(filePath):
    t = None
    f = None
    try:
        f = open(filePath)
        t = f.read()
    finally:
        if f is not None :
            f.close()
    return t
