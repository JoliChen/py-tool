# -*- coding: UTF-8 -*-

# format encode
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import eyed3 as eyed3
from eyed3.id3 import ID3_V2_3

import os
import time
import shutil
import MixFileUtils, MixRandUtils

SOUND_DIR_NAME = 'music'

def prn_obj(obj):
    print "----------------------------------------------------"
    print '\n'.join(['%s:%s' % item for item in obj.__dict__.items()])

def printAudio(audiofile):
    print "----------------------------------------------------"
    print 'version:'        + str(audiofile.tag.version) + ', cmp:' + str(cmp(ID3_V2_3, audiofile.tag.version) == 0)
    print 'title='          + str(audiofile.tag.title)
    print 'artist='         + str(audiofile.tag.artist)
    print 'album='          + str(audiofile.tag.album)
    print 'album_artist='   + str(audiofile.tag.album_artist)
    print 'track_num='      + str(audiofile.tag.track_num)
    print 'disc_num='       + str(audiofile.tag.disc_num)

# 设置音频文件信息
def setAudioTag(audiofile, title, artist, album, track, disc):
    tag = audiofile.tag
    if (tag is None):
        audiofile.initTag()
        tag = audiofile.tag
    tag.title  = title
    tag.artist = artist
    tag.album  = album
    tag.album_artist = artist
    tag.track_num = (0, track)
    tag.disc_num  = (0, disc)
    tag.save()

# 修改属性
def setProperty(f, track, signName) :
    audiof = eyed3.load(f)
    if audiof == None :
        return
    album = time.strftime('%Y%m%d%H', time.localtime(time.time()))
    try:
        setAudioTag(audiof, unicode(signName + str(track)), unicode(signName), unicode(album), track, 1)
    except AttributeError:
        print "Error: 修改MP3属性失败"


# 获取一个尚未存在名字，避免覆盖。
def randomName(upsetDirName, mapping):
    while True :
        nodePath = upsetDirName + MixRandUtils.randomString(5, 12) + '.mp3'
        if nodePath not in mapping :
            return nodePath

# 修改名字
def renameSound(soundPath, upsetDirName, mapping):
    resPos = soundPath.rfind(SOUND_DIR_NAME)
    if -1 == resPos :
        return
    resPath = soundPath[0:resPos]
    srcSearchPath = soundPath[resPos:]
    dstSearchPath = randomName(upsetDirName, mapping)
    dstPath = resPath + dstSearchPath
    MixFileUtils.tryMkdir(os.path.dirname(dstPath))
    shutil.move(soundPath, dstPath)
    mapping[dstSearchPath] = srcSearchPath

# 批量修改声音文件
def bitchMix(resDir, signName, mapping):
    # 签名
    soundDir = resDir + os.sep + SOUND_DIR_NAME
    files = []
    MixFileUtils.listfiles(soundDir, files)
    track = 0
    for f in files:
        if '.mp3' != os.path.splitext(f)[1] :
            continue
        track += 1
        print 'mix sound : %d-%s' % (track, f)
        setProperty(f, track, signName) # 签名MP3
    # 打乱文件
    if mapping != None :
        upsetDir = None
        while True:
            upsetDir = MixRandUtils.randomDir(1, 3)
            if upsetDir.find(SOUND_DIR_NAME) != 0:
                break
        for f in files:
            renameSound(f, upsetDir, mapping)
        MixFileUtils.tryRmdir(soundDir)

def main(mixParams, assetsInfo):
    mapping  = None
    if mixParams.soundMapping :
        mapping = {}
        assetsInfo.soundMapping = mapping
    signName = MixFileUtils.getFileName(mixParams.assetsName)
    bitchMix(mixParams.assetsRes, signName, mapping)

