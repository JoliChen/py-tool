# -*- coding: utf-8 -*-
# @Time    : 2018/10/8 下午2:41
# @Author  : Joli
# @Email   : 99755349@qq.com
# File System
import math
import os
import shutil
import hashlib
import chardet
import json

from jonlin.utils import Log, Cross, Text

log = Log.Logger(__file__)

# 创建父目录
def make_parent(dp):
    dp = os.path.dirname(dp)
    if not os.path.isdir(dp):
        os.makedirs(dp)

# 清空文件夹（如果文件夹不存在则创建一个新的）
def cleanup_dir(dp):
    log.d('cleanup_dir:', dp)
    if os.path.isdir(dp):
        shutil.rmtree(dp)
    os.makedirs(dp)

# 获取文件名 (包含扩展名)
def basename(p, sep=None):
    return p[p.rfind(sep or os.sep) + 1:]

# 获取文件名 (不包含扩展名)
def filename(p, sep=None):
    return p[p.rfind(sep or os.sep)+1: p.rfind('.')]

# 获取文件扩展名 (.png，.jpg, ...)
def extensions(p):
    # return os.path.splitext(fp)[1]
    return p[p.rfind('.'):]

# 获取直接父级目录名称
def parentname(p, sep=None):
    sep = sep or os.sep
    end = len(p) - 1
    if p[end] == sep:
        end -= 1
    s = Text.last_find(p, sep, end)
    return p[Text.last_find(p, sep, s - 1) + 1: s]

# 删除目录下所有的空文件夹
def rm_empty_dirs(root):
    for (parent, dirs, _) in os.walk(dstdir):
        for fn in dirs:
            dirpath = os.path.join(parent, fn)
            if not os.listdir(dirpath):
                os.rmdir(dirpath)

# 移动文件
def moveto(src, dst):
    log.d('moveto:', src, dst)
    make_parent(dst)
    shutil.move(src, dst)

# 移动 A文件夹下的内容 到 B文件夹下
def moveto_dir(srcdir, dstdir, nwhites=None, nblacks=None):
    cut = len(srcdir) + 1
    for (par, _, files) in os.walk(srcdir):
        for name in files:
            path = os.path.join(par, name)
            name = path[cut:]
            if nblacks and (name in nblacks):
                continue
            if not nwhites or (name in nwhites):
                moveto(path, os.path.join(dstdir, name))

# 遍历目录下所有的文件，返回文件路径列表。
def walk_files(root, ewhites=None, eblacks=None, cut=0):
    array = []
    for (par, _, files) in os.walk(root):
        for name in files:
            ext = extensions(name)
            if eblacks and (ext in eblacks):
                continue
            if not ewhites or (ext in ewhites):
                path = os.path.join(par, name)
                if cut > 0:
                    path = path[cut:]
                array.append(path)
    return array

# 将 src_dir 合并到 dst_dir
def merge_tree(srcdir, dstdir, copy_file_func=shutil.copy2):
    if not os.path.isdir(dstdir):
        os.makedirs(dstdir)
    for name in os.listdir(srcdir):
        sp = os.path.join(srcdir, name)
        dp = os.path.join(dstdir, name)
        if os.path.isdir(sp):
            merge_tree(sp, dp, copy_file_func)
        else:
            copy_file_func(sp, dp)

# 将 src_dir 合并到 dst_dir （此函数只会拷贝发生变更的文件）
def fast_merge_tree(srcdir, dstdir):
    merge_tree(srcdir, dstdir, fast_replace)

# 快速替换文件 (检查文件元信息是否变更)
def fast_replace(src, dst):
    if os.path.isfile(dst) and not is_meta_modified(src, dst):
        return  # 文件未修改则忽略本次拷贝
    log.d('fast_copy:', src, dst)
    shutil.copy2(src, dst)  # copy file and stat

# 同步文件元数据的访问时间和修改时间
def sync_meta_utime(src, dst):
    meta = os.stat(src)
    os.utime(dst, (meta.st_ctime, meta.st_mtime))

# 通过文件元数据检查文件是否修改
def is_meta_modified(src, dst, ignore_size=False):
    st1 = os.stat(src)
    st2 = os.stat(dst)
    if not ignore_size and st1.st_size != st2.st_size:
        return True  # 文件大小不一致
    if math.floor(st1.st_mtime * 1000) != math.floor(st2.st_mtime * 1000):
        return True  # 文件修改时间不一致（精确到秒）
    return False  # 文件未修改

# 设置文件显示/隐藏
def set_file_visible(fp, visible):
    if not os.path.isfile(fp):
        return
    if Cross.IS_WINDOWS:
        try:
            import win32api
            import win32con
            if visible:
                win32api.SetFileAttributes(fp, win32con.FILE_ATTRIBUTE_ARCHIVE)
            else:
                win32api.SetFileAttributes(fp, win32con.FILE_ATTRIBUTE_HIDDEN)
        except ImportError:
            pass

# 打开文件或文件夹
def explorer(p):
    if Cross.IS_MACOSX or Cross.IS_LINUX:
        os.system('open ' + p)
    elif Cross.IS_WINDOWS:
        os.system('start explorer ' + p)

# 上传文件到ftp
def ftp_upload(src, dst, ip='', port=0, usr='', pwd=''):
    import ftplib
    with ftplib.FTP() as ftp:
        ftp.set_debuglevel(2)
        ftp.connect(ip, port)
        ftp.login(usr, pwd)  # 登录
        # print ftp.getwelcome()
        with open(src, 'rb') as fp:
            ftp.storbinary('STOR ' + dst, fp)
        log.d('ftp upload done', src)

# 写入文本，utf-8编码。
def write_text(fp, text):
    with open(fp, 'w') as f:
        f.write(text)

# 读取文本，utf-8编码。
def read_text(fp):
    with open(fp, 'r') as f:
        return f.read()

# 读取文本，自动识别编码。
def read_text_guess(fp):
    with open(fp, 'rb') as f:
        buffer = f.read()
        encoding = chardet.detect(buffer)["encoding"]
        return buffer.decode(encoding)

# 计算文件MD5值
def md5(fp):
    h = hashlib.md5()
    with open(fp, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()

# 文件状态记录
class FileStatManifest:
    def __init__(self, diskfile):
        self._newfest = {}
        self.reset(diskfile)

    def _cachenew(self, filepath, stat):
        item = {
            'size': stat.st_size,
            'time': self._mtime(stat)
        }
        self._newfest[filepath] = item

    @staticmethod
    def _mtime(stat):
        return math.floor(stat.st_mtime * 1000)  # 文件修改时间精确到毫秒

    def ismodified(self, filepath):
        stat = os.stat(filepath)
        if filepath not in self._manifest:
            self._cachenew(filepath, stat)
            return True
        last = self._manifest[filepath]
        if last['size'] != stat.st_size:
            self._cachenew(filepath, stat)
            return True
        if last['time'] != self._mtime(stat):
            self._cachenew(filepath, stat)
            return True
        self._newfest[filepath] = last
        return False

    def reset(self, filepath):
        self._diskfile = filepath
        if os.path.isfile(filepath):
            with open(filepath, 'r') as f:
                self._manifest = json.load(f)
        else:
            self._manifest = {}

    def flush(self):
        if self._diskfile is not None:
            with open(self._diskfile, 'w') as f:
                json.dump(self._newfest, f, ensure_ascii=False, indent='\t')