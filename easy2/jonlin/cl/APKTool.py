# -*- coding: utf-8 -*-
# @Time    : 2019/4/11 4:26 PM
# @Author  : Joli
# @Email   : 99755349@qq.com
import os
import shutil
import zipfile
from jonlin.cl import Shell
from jonlin.utils import Log

log = Log.Logger(__file__)

APK2DIR = '/Users/joli/source/android/apktool'
# APK2JAR = os.path.join(APK2DIR, 'apktool_2.3.0.jar')
APK2JAR = os.path.join(APK2DIR, 'apktool_2.4.0.jar')

def dapk(apk, dist):  # 反编APK
    return Shell.run('java -Djava.awt.headless=true -jar %s d -f -o %s %s' % (APK2JAR, dist, apk))

def bapk(dist, apk):  # 回编APK
    return Shell.run('java -Djava.awt.headless=true -jar %s b -f -o %s %s' % (APK2JAR, apk, dist))

def sign(unsign_apk, signed_apk, sign_config=None):  # 签名APK
    if sign_config is None:
        sign_config = {
            'keystore': os.path.join(APK2DIR, 'sign/myapk.jks'),
            'storepwd': '666666',
            'keypwd': '666666',
            'alias': 'joli'
        }
    return Shell.run('jarsigner -verbose -keystore %s -storepass %s -keypass %s -signedjar %s %s %s' % (
        sign_config['keystore'],
        sign_config['storepwd'],
        sign_config['keypwd'],
        signed_apk,
        unsign_apk,
        sign_config['alias']
    ))

def unzapk(apk, dist):
    if os.path.isdir(dist):
        shutil.rmtree(dist)
    zf = zipfile.ZipFile(apk, 'r')
    zf.extractall(dist)
    zf.close()
    mi_dir = os.path.join(dist, 'META-INF')
    if os.path.isdir(mi_dir):
        for fn in os.listdir(mi_dir):
            if fn == 'MANIFEST.MF':
                continue
            fp = os.path.join(mi_dir, fn)
            log.d('remove', fp)
            if os.path.isdir(fp):
                shutil.rmtree(fp)
            else:
                os.remove(fp)
    return 0

def zipapk(dist, apk):
    zf = zipfile.ZipFile(apk, 'w', zipfile.ZIP_STORED)
    cut_pos = len(dist) + 1
    for root, _, files in os.walk(dist):
        for fn in files:
            fp = os.path.join(root, fn)
            zf.write(fp, fp[cut_pos:])
    zf.close()
    return 0