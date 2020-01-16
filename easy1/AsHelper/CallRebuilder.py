# -*- coding: UTF-8 -*-
import os
import random
import math

def callRebuilder():
    cmdstr = 'python ApkRebuilder.py'
    # 依赖环境设置
    cmdstr += ' --apktool ' + '/Users/joli/source/android/apktool/apktool'
    cmdstr += ' --jarsigner ' + 'jarsigner'
    # 反编译后的文件夹
    cmdstr += ' --dstdir ' + '/Users/joli/desktop/test/apkdir'
    # 需要替换资源（srcdir最终会与dstdir合并）
    cmdstr += ' --srcdir ' + '/Users/joli/desktop/test/repeat'
    # 包名
    cmdstr += ' --apkid ' + 'com.joli.test'
    # 游戏参数
    cmdstr += ' --gid ' + '111111'
    cmdstr += ' --gkey ' + 'bilibili'
    # cmdstr += ' --gchannel '    + 'None' #渠道ID没有就不传
    # 微信参数
    cmdstr += ' --wxid ' + 'wx12031042r812934810234'
    # 签名配置
    cmdstr += ' --keystore ' + '/Users/joli/proj/master/cc25/com.cc25.game.as/sign/gamesign.jks'
    cmdstr += ' --keypass ' + '666666'
    cmdstr += ' --signalias ' + 'joli'
    cmdstr += ' --signpass ' + '666666'
    # 输出包位置
    cmdstr += ' -o ' + '/Users/joli/desktop/test/cc52Demo-signed.apk'
    # 原始包位置
    cmdstr += ' ' + '/Users/joli/desktop/test/cc52Demo-release.apk'
    os.system(cmdstr)

def main():
    # callRebuilder()
    times = {}
    for i in range(100):
        r = random.random()
        d = int(math.pow(r, 2) * 12)
        if d in times:
            times[d] = times[d] + 1
        else:
            times[d] = 1
        print str(r) + ' - ' + str(d)
    print times

if __name__ == '__main__':
    main()