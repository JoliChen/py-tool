# -*- coding: UTF-8 -*-
# 声音文件签名工具

import time
import random
import eyed3
from eyed3 import mp3
from eyed3 import core
from eyed3.id3 import tag
import logging

class JSoundsSigner:

    # 签名声音文件
    @classmethod
    def sign_sounds(cls, sound_list, author_name):
        mp3.log.setLevel(logging.ERROR)
        core.log.setLevel(logging.ERROR)
        tag.log.setLevel(logging.ERROR)

        error_list = [] # error list
        disc = random.randint(1, 10000)
        for i in range(len(sound_list)):
            path = sound_list[i]
            sn = i + 1
            title = author_name + str(disc) + str(sn)
            album = time.strftime('%Y%m%d%H', time.localtime(time.time()))
            if (not cls._set_audio_file(path, title, author_name, album, sn, disc)):
                error_list.append(path)
        if len(error_list) > 0:
            print('--------------------------------------')
            for path in error_list:
                print('sound sign error : %s' % (path))
            print('--------------------------------------')

    # 修改音频文件属性
    @classmethod
    def _set_audio_file(cls, path, title, artist, album, track, disc):
        is_ok = True
        try:
            audio_file = eyed3.load(path)
            if (audio_file is not None):
                title  = str(title)
                artist = str(artist)
                album  = str(album)
                cls._save_audio_tag(audio_file, title, artist, album, track, disc)
        except eyed3.Error:
            # print "%s 修改mp3:%s" % (track, path)
            is_ok = False
        return is_ok

    # 保存音频文件信息
    @classmethod
    def _save_audio_tag(cls, audio_file, title, artist, album, track, disc):
        tag = audio_file.tag
        if (tag is None):
            audio_file.initTag()
            tag = audio_file.tag
        tag.title = title
        tag.artist = artist
        tag.album = album
        tag.album_artist = artist
        tag.track_num = (0, track)
        tag.disc_num = (0, disc)
        tag.save()

    # 打印对象
    # @staticmethod
    # def print_object(obj):
    #     print "----------------------------------------------------"
    #     print '\n'.join(['%s:%s' % item for item in obj.__dict__.items()])

    # 打印声音文件信息
    # @staticmethod
    # def print_audio_tag(audio_file):
    #     tag = audio_file.tag
    #     print "----------------------------------------------------"
    #     print 'version:' + str(tag.version) + ', cmp:' + str(cmp(ID3_V2_3, tag.version) == 0)
    #     print 'title=' + str(tag.title)
    #     print 'artist=' + str(tag.artist)
    #     print 'album=' + str(tag.album)
    #     print 'album_artist=' + str(tag.album_artist)
    #     print 'track_num=' + str(tag.track_num)
    #     print 'disc_num=' + str(tag.disc_num)