# -*- coding: utf-8 -*-
# @Time    : 2019/5/23 4:58 PM
# @Author  : Joli
# @Email   : 99755349@qq.com
import hashlib

def xor_bytes(buf, key):  # 异或处理二进制数据
    klen = len(key)
    ibuf = [(buf[i] ^ key[i % klen]) for i in range(len(buf))]
    return bytes(ibuf)

def xor_file(src, dst, key):  # 异或处理文件
    with open(src, 'rb') as fp:
        buf = xor_bytes(fp.read(), key)
    with open(dst, 'wb') as fp:
        fp.write(buf)

def md5_bytes(buf):  # 计算字符串的MD5值
    h = hashlib.md5()
    h.update(buf)
    return h.hexdigest()

def md5_file(filepath):  # 计算文件的MD5值
    with open(filepath, 'rb') as fp:
        return md5_bytes(fp.read())