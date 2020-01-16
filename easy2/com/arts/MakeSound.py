# -*- coding: utf-8 -*-
# @Time    : 2019/5/22 9:12 PM
# @Author  : Joli
# @Email   : 99755349@qq.com

import os
import random
import time
import eyed3
from jonlin.utils import Log

log = Log.Logger(__file__)

# eyed3.log.setLevel(logging.ERROR)
# eyed3.core.log.setLevel(logging.ERROR)
# eyed3.mp3.log.setLevel(logging.ERROR)
# eyed3.id3.tag.log.setLevel(logging.ERROR)

# 设置MP3标签
def set_mp3_tag(fp, title, artist, album, track, disc):
    try:
        audio = eyed3.load(fp)
        if audio is None:
            return False
        if audio.tag is None:
            audio.initTag()
        audio.tag.title = title
        audio.tag.album = album
        audio.tag.artist = artist
        audio.tag.album_artist = artist
        audio.tag.track_num = (0, track)
        audio.tag.disc_num = (0, disc)
        audio.tag.save()
        return True
    except eyed3.Error:
        return False

# 重签名MP3（签名后会在MP3头部插入或修改ID3段，导致输出略大于源文件。）
def sign_mp3(src, author):
    sn = 1
    disc = random.randint(10, 20)
    if os.path.isdir(src):
        for (root, _, files) in os.walk(src):
            for name in files:
                if name.endswith('.mp3') or name.endswith('.MP3'):
                    fp = os.path.join(root, name)
                    title = '%d%s%d' % (sn, author, disc)
                    album = time.strftime('%Y%m%d%H', time.localtime(time.time()))
                    if not set_mp3_tag(fp, title, author, album, sn, disc):
                        log.d('sign mp3 fail:', fp)
                    sn += 1
    else:
        title = '%d%s%d' % (sn, author, disc)
        album = time.strftime('%Y%m%d%H', time.localtime(time.time()))
        if not set_mp3_tag(src, title, author, album, sn, disc):
            log.d('sign mp3 fail:', src)

