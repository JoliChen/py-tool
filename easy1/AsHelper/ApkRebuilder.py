# -*- coding: UTF-8 -*-

import sys
import getopt
import os
import platform
import re
import shutil

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree  as ET

class JUtils:
    AndroidManifestXML = 'AndroidManifest.xml'
    WXPayEntryActivity = 'WXPayEntryActivity'
    hasRegistNameSpace = False

    @staticmethod
    def mergeDir(src, dst, symlinks=False):
        names = os.listdir(src)
        if not os.path.isdir(dst):
            os.makedirs(dst)
        errors = []
        for name in names:
            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)
            try:
                if symlinks and os.path.islink(srcname):
                    linkto = os.readlink(srcname)
                    os.symlink(linkto, dstname)
                elif os.path.isdir(srcname):
                    JUtils.mergeDir(srcname, dstname, symlinks)
                else:
                    if os.path.isfile(dstname):
                        os.remove(dstname)
                    shutil.copy2(srcname, dstname)
                    # XXX What about devices, sockets etc.?
            except (IOError, os.error) as why:
                errors.append((srcname, dstname, str(why)))
            # catch the Error from the recursive copytree so that we can
            # continue with other files
            except OSError as err:
                errors.extend(err.args[0])
        if errors:
            raise shutil.Error(errors)

    # 0: equal
    # 1: path1 is sub folder of path2
    # -1:path2 is sub folder of path1
    # 2: unrelated
    @staticmethod
    def comparePath(path1, path2):
        if not path1 or not path1:
            return 2

        path1Len = len(path1)
        path2Len = len(path2)

        if path1Len > path2Len:
            longPath = path1
            shortPath = path2
            cmpFator = 1
        else:
            longPath = path2
            shortPath = path1
            cmpFator = -1

        shortPathLen = len(shortPath)
        longPathLen = len(longPath)
        i = 0
        j = 0
        while i < shortPathLen and j < longPathLen:
            c1 = shortPath[i]
            c2 = longPath[j]
            if JUtils.isSlash(c1):
                if not JUtils.isSlash(c2):
                    return 2
                while i < shortPathLen and JUtils.isSlash(shortPath[i]):
                    i += 1
                while j < longPathLen  and JUtils.isSlash(longPath[j]):
                    j += 1
            else:
                if c1 != c2:
                    if i == shortPathLen:
                        return cmpFator
                    else:
                        return 2
                i += 1
                j += 1

        if i == shortPathLen:
            if j == longPathLen:
                return 0
            while j < longPathLen:
                if not JUtils.isSlash(longPath[j]):
                    return cmpFator
                j += 1
            return 0
        else:
            return 2

    @staticmethod
    def isSlash(c):
        return c == '/' or c == '\\'

    @staticmethod
    def readFileString(path):
        f = None
        try:
            f = open(path, 'r')
            return f.read()
        finally:
            if (f is not None):
                f.close()
    @staticmethod
    def writeFileString(path, str):
        f = None
        try:
            f = open(path, 'w')
            f.write(str)
        finally:
            if (f is not None):
                f.close()

    @staticmethod
    def findWxPayEntryPath(dir):
        names = os.listdir(dir)
        for name in names:
            path = os.path.join(dir, name)
            if os.path.isdir(path):
                p = JUtils.findWxPayEntryPath(path)
                if (p is not None):
                    return p
            else:
                if (name.startswith(JUtils.WXPayEntryActivity)):
                    return path
    @staticmethod
    def delWxPayEntryFile(file):
        if os.path.isdir(file):
            childs = os.listdir(file)
            if (childs is None or childs.__len__() <= 0):
                os.rmdir(file)
                JUtils.delWxPayEntryFile(os.path.dirname(file))
        else:
            if os.path.exists(file):
                os.remove(file)
                JUtils.delWxPayEntryFile(os.path.dirname(file))

    @staticmethod
    def readAndroidManifest(file):
        if (not JUtils.hasRegistNameSpace):
            ET.register_namespace('android', "http://schemas.android.com/apk/res/android")
            JUtils.hasRegistNameSpace = True
        return ET.parse(file)
    @staticmethod
    def writeAndroidManifest(etree, file):
        etree.write(file, encoding="utf-8", xml_declaration=True)
    @staticmethod
    def setAndroidManifestPackage(eroot, packageName):
        eroot.set(u'package', packageName)
    @staticmethod
    def getAndroidAttributeName(attribute):
        return '{http://schemas.android.com/apk/res/android}' + attribute
    @staticmethod
    def setAndroidManifestMetadata(eroot, key, value):
        isOk = False
        attK = JUtils.getAndroidAttributeName(u'name')
        attV = JUtils.getAndroidAttributeName(u'value')
        nodelist = eroot.findall(u'application/meta-data')
        for node in nodelist:
            if (node.get(attK) == key):
                node.set(attV, value)
                isOk = True
                break
        if (not isOk) :
            appnode = eroot.find(u'application')
            if (appnode is not None):
                metadata = ET.Element(u'meta-data', {attK:key, attV:value})
                metadata.tail = '\n'
                appnode.append(metadata)
    @staticmethod
    def setAndroidManifestWxPayActivity(eroot, packageName):
        isOk = False
        activity = packageName + '.wxapi.' + JUtils.WXPayEntryActivity
        andrname = JUtils.getAndroidAttributeName(u'name')
        nodelist = eroot.findall(u'application/activity')
        for node in nodelist:
            if (node.get(andrname).endswith(JUtils.WXPayEntryActivity)):
                node.set(andrname, activity)
                isOk = True
                break
        if (not isOk):
            appnode = eroot.find(u'application')
            if (appnode is not None):
                attrs = {
                    andrname:activity,
                    JUtils.getAndroidAttributeName(u'exported'):u'true',
                    JUtils.getAndroidAttributeName(u'launchMode'): u'singleTop',
                    JUtils.getAndroidAttributeName(u'screenOrientation'): u'sensorLandscape',
                    JUtils.getAndroidAttributeName(u'theme'): u'@android:style/Theme.Translucent',
                }
                actnode = ET.Element(u'activity', attrs)
                actnode.tail = '\n'
                appnode.append(actnode)

class JRebuilder:

    apktool = '' # apktool
    jsigner = '' # 签名程序

    def __init__(self):
        self.orgApkFile = None
        self.outApkFile = None
        self.compileDir = None
        self.signConfig = None
        self.repeatFrom = None
        self.apkPackage = None
        self.gameID = None
        self.gameKey = None
        self.gameChan = None
        self.weixinID = None
        self.wxPayEntry = None

    # 开始执行二次打包任务
    def start(self):
        unsignedApk = self.compileDir + os.sep + 'dist' + os.sep + 'unsigned.apk'
        self.decompileApk(self.orgApkFile, self.compileDir) # 反编apk
        self.modifyApk(self.compileDir) # 修改apk
        self.recompileApk(unsignedApk, self.compileDir) # 回编apk
        self.signApk(unsignedApk, self.outApkFile) # 签名apk
        # zipalign对齐apk
        print "rebuild done"

    # 反编apk
    def decompileApk(self, apkfile, outdir):
        cmdstr = None
        sysname = platform.system()
        if (sysname == "Windows"):
            cmdstr = '%s d -f -o %s %s' % (self.apktool, outdir, apkfile)
        else :
            cmdstr = 'source %s d -f -o %s %s' % (self.apktool, outdir, apkfile)

        if (cmdstr is not None) :
            tempDir = os.getcwd()
            os.chdir(os.path.dirname(self.apktool))
            os.system(cmdstr)
            os.chdir(tempDir)
    # 回编apk
    def recompileApk(self, unsignedApk, inputDir):
        cmdstr = None
        sysname = platform.system()
        if (sysname == "Windows"):
            cmdstr = '%s b -f -o %s %s' % (self.apktool, unsignedApk, inputDir)
        else:
            cmdstr = 'source %s b -f -o %s %s' % (self.apktool, unsignedApk, inputDir)

        if (cmdstr is not None):
            tempDir = os.getcwd()
            os.chdir(os.path.dirname(self.apktool))
            os.system(cmdstr)
            os.chdir(tempDir)
        pass
    # 签名apk
    def signApk(self, unsignApk, signedApk):
        signConfig = self.signConfig
        cmdstr = '%s -verbose -keystore %s -storepass %s -keypass %s -signedjar %s %s %s' % (
            self.jsigner,
            signConfig['file'],
            signConfig['storepass'],
            signConfig['keypass'],
            signedApk,
            unsignApk,
            signConfig['alias'])
        os.system(cmdstr)

    # 修改apk
    def modifyApk(self, apkdir):
        self.repeatResource(self.repeatFrom, apkdir) # 替换资源
        self.configManifest(apkdir) # 配置 AndroidManifest.xml
        self.configWxPay(apkdir) # 配置 微信支付
        pass
    # 替换资源
    def repeatResource(self, srcDir, dstDir):
        JUtils.mergeDir(srcDir, dstDir)
    # 配置 AndroidManifest.xml
    def configManifest(self, apkdir):
        amfile = apkdir + os.sep + JUtils.AndroidManifestXML
        etree = JUtils.readAndroidManifest(amfile)
        eroot = etree.getroot()
        if (self.apkPackage is not None):
            JUtils.setAndroidManifestPackage(eroot, self.apkPackage)
        if (self.gameID is not None):
            JUtils.setAndroidManifestMetadata(eroot, 'CC52_GAME_ID',      self.gameID)
        if (self.gameKey is not None):
            JUtils.setAndroidManifestMetadata(eroot, 'CC52_APP_KEY',      self.gameKey)
        if (self.gameChan is not None):
            JUtils.setAndroidManifestMetadata(eroot, 'CC52_CHANNELID',    self.gameChan)
        if (self.weixinID is not None):
            JUtils.setAndroidManifestMetadata(eroot, 'CC52_WEIXIN_APPID', self.weixinID)
            JUtils.setAndroidManifestWxPayActivity(eroot, self.apkPackage)
        JUtils.writeAndroidManifest(etree, amfile)
    # 配置 微信支付配置
    def configWxPay(self, apkdir):
        if (self.apkPackage is None):
            return
        # find origApk wxPayEntry
        smalisDir = apkdir + os.sep + 'smali'
        origFile = JUtils.findWxPayEntryPath(smalisDir)
        if (origFile is None):
            return
        origPack = os.path.dirname(origFile.split(os.sep + "smali" + os.sep)[-1])
        # make wxPayEntry
        wxPackage = self.apkPackage.replace('.', '/') + '/wxapi'
        wxpayNode = smalisDir + os.sep + wxPackage
        wxpayPath = wxpayNode + os.sep + JUtils.WXPayEntryActivity + '.smali'
        # replace
        wxpayText = JUtils.readFileString(origFile)
        wxpayText = re.compile(origPack).sub(wxPackage, wxpayText)
        if not os.path.exists(wxpayNode):
            os.makedirs(wxpayNode)
        JUtils.writeFileString(wxpayPath, wxpayText)
        # print wxpayText
        if ((JUtils.comparePath(origFile, wxpayPath)) != 0):
            JUtils.delWxPayEntryFile(origFile)

def test():
    # apktool 命令行位置
    JRebuilder.apktool = '/Users/joli/source/android/apktool/apktool'
    # 签名程序位置
    JRebuilder.jsigner = 'jarsigner'

    builder = JRebuilder()
    # 原始包位置
    builder.orgApkFile = '/Users/joli/desktop/test/cc52Demo-release.apk'
    # 输出包位置
    builder.outApkFile = '/Users/joli/desktop/test/cc52Demo-signed.apk'
    # 签名配置
    builder.signConfig = {
        'file': '/Users/joli/proj/master/cc25/com.cc25.game.as/sign/gamesign.jks',
        'alias': 'joli',
        'keypass': '666666',
        'storepass': '666666'
    }
    # 编译处理的位置，反编译后的文件存放在这里。
    builder.compileDir = '/Users/joli/desktop/test/apkdir'
    # 替换资源的源位置，直接复制资源覆盖"builder.compileDir"。
    builder.repeatFrom = '/Users/joli/desktop/test/repeat'
    # 包名
    builder.apkPackage = 'com.joli.test'
    # 游戏参数
    builder.gameID = '1'
    builder.gameKey = 'bilibili'
    builder.gameChan = None
    # 微信参数
    builder.weixinID = 'wechatID'
    # 开始执行
    builder.start()

def main():
    temp = ['apktool=', 'jarsigner=', 'dstdir=', 'srcdir=', 'apkid=', 'gid=', 'gkey=', 'gchannel=', 'wxid=', 'keystore=', 'keypass=', 'signalias=', 'signpass=']
    opts, args = getopt.getopt(sys.argv[1:],'o:', temp)
    if (args is None or args.__len__() <= 0):
        print 'please input apk path'
        return

    builder = JRebuilder()
    signConfig = {}
    for i, v in opts:
        if (i == '-o'):
            builder.outApkFile = v
        elif (i == '--apktool'):
            JRebuilder.apktool = v
        elif (i == '--jarsigner'):
            JRebuilder.jsigner = v
        elif (i == '--dstdir'):
            builder.compileDir = v
        elif (i == '--srcdir'):
            builder.repeatFrom = v
        elif (i == '--apkid'):
            builder.apkPackage = v
        elif (i == '--gid'):
            builder.gameID = v
        elif (i == '--gkey'):
            builder.gameKey = v
        elif (i == '--gchannel'):
            builder.gameChan = v
        elif (i == '--wxid'):
            builder.weixinID = v
        elif (i == '--keystore'):
            signConfig['file'] = v
        elif (i == '--keypass'):
            signConfig['keypass'] = v
        elif (i == '--signalias'):
            signConfig['alias'] = v
        elif (i == '--signpass'):
            signConfig['storepass'] = v
    builder.signConfig = signConfig

    for v in args:
        if (False):
            pass
        else:
            builder.orgApkFile = v

    builder.start()

if __name__ == '__main__':
    main()