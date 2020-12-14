# -*- coding: utf-8 -*-
# @Time    : 2019/8/3 5:14 PM
# @Author  : Joli
# @Email   : 99755349@qq.com
import xxtea

from jonlin.utils import Text, FS

unicode_sep = ord('/')
unicode_und = ord('_')
unicode_dot = ord('.')
unicode_gan = ord('-')
unicode_spa = ord(' ')
special_unis = (unicode_sep, unicode_und, unicode_dot, unicode_gan, unicode_spa)
default_exts = (b'jpg', b'png', b'json', b'mp3', b'ogg', b'csb', b'ccb', b'skel', b'ttf', b'fnt', b'vsh', b'fsh')

PNG_BEG = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])
PNG_END = b'IEND'
PNG_HDR = bytes([0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52])
JPG_BEG = bytes([0xFF, 0xD8])
JPG_HDR = bytes([0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01, 0x01, 0x01])
JPG_END = bytes([0xFF, 0xD9])
XML_BEG = b'<?xml version="1.0" encoding="UTF-8"?>'

# 从二进制文件中查找文件后缀 ".xxx"
def find_binary_exts(buffer):
    size = len(buffer)
    if size <= 0:
        return
    array = []
    end = size - 1
    pos = 0
    while pos < end:
        pos += 1  # 从第二个直接开始检查
        if buffer[pos] != unicode_dot:
            continue
        if not Text.isword_unicode(buffer[pos - 1]):
            continue
        b = buffer[pos + 1]
        if not Text.isabc_unicode(b):
            continue
        s = chr(b)
        for i in range(2, min(6, end - pos)):  # 后缀长度不超过5
            b = buffer[pos + i]
            if Text.isword_unicode(b):
                s += chr(b)
            else:
                pos += i - 1
                break
        array.append(s)
    if not array:
        return
    ndict = {}
    for s in array:
        if s in ndict:
            ndict[s] += 1
        else:
            ndict[s] = 1
    return ndict

# 从二进制文件中查找文件路径 "xxx/xxx.xxx"
def find_binary_paths(buffer, exts):
    size = len(buffer)
    if size <= 0:
        return
    array = []
    end = size - 1
    pos = 0
    while pos < end:
        pos += 1  # 从第二个直接开始检查
        if buffer[pos] != unicode_dot:
            continue
        for ebs in exts:
            isext = True
            for i in range(len(ebs)):
                if buffer[pos + i + 1] != ebs[i]:
                    isext = False
                    break
            if not isext:
                continue
            s, p = '', -1
            for i in range(pos - 1, -1, -1):
                b = buffer[i]
                if b in special_unis or Text.isword_unicode(b):
                    s = chr(b) + s
                else:
                    p = i + 1
                    break
            if p > 0:
                array.append((p, '%s.%s' % (s, Text.unicodes2str(ebs))))
            pos += len(ebs)
            break
    return array


class XXTEA:

    @staticmethod
    def fmt_key(sig_buffer):
        size = len(sig_buffer)
        if size < 16:
            return sig_buffer + bytes(16 - size)
        elif size > 16:
            return sig_buffer[:16]
        return sig_buffer

    @staticmethod
    def decrypt(buffer, bsig, bkey):
        if bsig:
            sig_len = len(bsig)
            if buffer[0: sig_len] != bsig:
                print("sign error")
                return buffer
            buffer = buffer[sig_len:]
        return xxtea.decrypt(buffer, bkey, padding=False)

    @staticmethod
    def defile(src, dst, bsig, bkey):
        with open(src, 'rb') as fp:
            buffer = XXTEA.decrypt(fp.read(), bsig, bkey)
        FS.make_parent(dst)
        with open(dst, 'wb') as fp:
            fp.write(buffer)