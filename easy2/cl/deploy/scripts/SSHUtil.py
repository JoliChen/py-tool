# -*- coding: utf-8 -*-
# @Time    : 2021/5/11 11:22 AM
# @Author  : Joli
# @Email   : 99755349@qq.com

# dependences
# pip install pycrypto
# pip install paramiko
import datetime
import os
import stat

import paramiko
from paramiko import SFTPClient

def sftp_isfile(sftp: SFTPClient, path):
    try:
        info = sftp.stat(path)
    except:
        info = None
    if not info:
        return False
    mode = info.st_mode
    if not isinstance(mode, int):
        return False
    return stat.S_ISREG(mode)

def sftp_isdir(sftp: SFTPClient, path):
    try:
        info = sftp.stat(path)
    except:
        info = None
    if not info:
        return False
    mode = info.st_mode
    if not isinstance(mode, int):
        return False
    return stat.S_IFMT(mode) == stat.S_IFDIR

def sftp_mkdir(sftp: SFTPClient, path):
    if sftp_isdir(sftp, path):
        return
    try:
        sftp.mkdir(path)
    except Exception as e:
        print("sftp mkdir:%s, error:%s" % (path, e))

def sftp_cleardir(sftp: SFTPClient, rootdir):
    try:
        remotefiles = sftp.listdir(rootdir)
    except Exception as e:
        print("sftp listdir:%s, error:%s" % (rootdir, e))
        remotefiles = []
    for fn in remotefiles:
        fp = rootdir + '/' + fn
        try:
            sftp.remove(fp)
        except Exception as e:
            print("sftp remove:%s, error:%s" % (fp, e))

def upload(conf, localdir, remotedir, allowlist: list):
    print('%s upload file start' % datetime.datetime.now())
    relatpos = len(localdir) + 1
    pt = paramiko.Transport((conf['host'], conf['port']))
    try:
        pt.connect(username=conf['username'], password=conf['password'])
        sftp = SFTPClient.from_transport(pt)
        sftp_mkdir(sftp, remotedir)
        if not allowlist:
            sftp_cleardir(sftp, remotedir)
        for root, dirs, files in os.walk(localdir):
            for dn in dirs:
                localpath = os.path.join(root, dn)
                relatname = localpath[relatpos:]
                if allowlist and relatname not in allowlist:
                    continue
                remotepath = os.path.join(remotedir, relatname)
                # print("mkdir:%s" % remotepath)
                try:
                    sftp.mkdir(remotepath)
                except Exception as e:
                    print("mkdir:%s, error:%s" % (remotepath, e))
            for fn in files:
                localpath = os.path.join(root, fn)
                relatname = localpath[relatpos:]
                if allowlist and relatname not in allowlist:
                    continue
                remotepath = os.path.join(remotedir, relatname)
                # print("upload:%s" % remotepath)
                try:
                    sftp.put(localpath, remotepath)
                except Exception as e:
                    print("upload %s to remote %s, error:%s" % (localpath, remotepath, e))
    except Exception as e:
        print(e)
    finally:
        pt.close()
    print('%s upload file done' % datetime.datetime.now())