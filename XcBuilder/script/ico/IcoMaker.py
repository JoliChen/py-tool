#encoding=utf-8

import os
import shutil
import sys
import json
from PIL import Image
from script.mix import MixFileUtils, MixRandUtils

DIR_IOS_ICON = '/Users/joli/desktop/outputs/icon/ios'
DIR_IOS_SHOT = '/Users/joli/desktop/outputs/shot/ios'
DIR_ANDROID_ICON = '/Users/joli/desktop/outputs/icon/android'
DIR_ANDROID_SHOT = '/Users/joli/desktop/outputs/shot/android'

def fullSelfDir(fileName):
    return os.path.dirname(os.path.abspath(__file__)) + '/' + fileName

# 获取一个尚未存在名字，避免覆盖。
def randomName(mapping):
    while True :
        name = MixRandUtils.randomString(1, 12)
        if name not in mapping.keys() :
            mapping[name] = True
            return name

def makeAndroidLaunchImage(source):
    return

def makeAndroidAppIcon(source):
    return

def makeIosLaunchImage(source):
    return

def makeIosAppIcon(source):
    icon = Image.open(source).convert("RGBA")
    if icon.size[0] != icon.size[1]:
        print 'Icon file must be a rectangle!'
        return
    tempText = MixFileUtils.readText(fullSelfDir('template/ios/AppIconContents.json'))
    if (tempText == None) or (tempText.__len__() <= 0) :
        print 'ios icon templete is None'
        return
    template = json.loads(tempText)
    if (template == None) :
        print 'templete parse error'
        return
    #输出icon
    MixFileUtils.tryRmdir(DIR_IOS_ICON)
    MixFileUtils.tryMkdir(DIR_IOS_ICON)
    nameMapping = {}
    name1024 = None
    for item in template[u'images'] :
        scale = float(item['scale'].split('x')[0]) # scale:2x
        size = float(item['size'].split('x')[0]) # size:20x20
        size = int(size * scale)
        imageName = randomName(nameMapping) + '.png'
        item[u'filename'] = imageName
        if (size == 1024) :
            name1024 = imageName
        else :
            iconImage = icon.resize((size, size), Image.LANCZOS)
            iconImage.save(DIR_IOS_ICON + os.sep + imageName)
    #去除1024的alpha通道
    if (icon.size[0] != 1024) :
        icon = icon.resize((1024, 1024), Image.LANCZOS)
    icon1024 = Image.new("RGB", (1024, 1024), (255, 255, 255))
    icon1024.paste(icon, mask=icon.split()[3])
    icon1024.save(DIR_IOS_ICON + os.sep + name1024, 'PNG')
    #输出配置文件
    tempText = json.dumps(template)
    MixFileUtils.outputText(DIR_IOS_ICON + os.sep + 'Contents.json', tempText)
    print tempText

# 入口函数
def main(platform, action, source):
    p = platform.lower()
    a = action.lower()
    if p == 'android' :
        if a == 'icon' :
            makeAndroidAppIcon(source)
        elif a == 'screenshot' :
            makeAndroidLaunchImage(source)
    elif p == 'ios' :
        if a == 'icon' :
            makeIosAppIcon(source)
        elif a == 'screenshot' :
            makeIosLaunchImage(source)
