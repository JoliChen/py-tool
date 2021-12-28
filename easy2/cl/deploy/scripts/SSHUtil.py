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
        fp = rootdir + '/' + fn  # os.path.join(rootdir, fn)
        try:
            sftp.remove(fp)
        except Exception as e:
            print("sftp remove:%s, error:%s" % (fp, e))

def upload(sshconf, localdir, remotedir, allowlist: list, syncstat=True):
    print('%s upload: %s -> %s' % (datetime.datetime.now(), localdir, remotedir))
    relatpos = len(localdir) + 1
    pt = None
    try:
        pt = paramiko.Transport((sshconf['host'], sshconf['port']))
        key_file = sshconf.get('key')
        if key_file:
            private_key = paramiko.RSAKey.from_private_key_file(key_file)
            pt.connect(username=sshconf['username'], pkey=private_key)
        else:
            pt.connect(username=sshconf['username'], password=sshconf['password'])
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
                remotepath = remotedir + '/' + relatname  # os.path.join(remotedir, relatname)
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
                remotepath = remotedir + '/' + relatname  # os.path.join(remotedir, relatname)
                # print("upload:%s" % remotepath)
                try:
                    sftp.put(localpath, remotepath)
                    if syncstat:
                        lst = os.stat(localpath)
                        sftp.utime(remotepath, (lst.st_atime, lst.st_mtime))
                except Exception as e:
                    print("upload %s to remote %s, error:%s" % (localpath, remotepath, e))
    except Exception as e:
        print(e)
    finally:
        if pt:
            pt.close()
    print('%s upload file done' % datetime.datetime.now())

# 执行远程命令 commands用;隔开
def run(sshconf, commands):
    print('%s run command: %s' % (datetime.datetime.now(), commands))
    pc = paramiko.SSHClient()
    if sshconf.get('policy') == 'auto':
        pc.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key_file = sshconf.get('key')
    if key_file:
        private_key = paramiko.RSAKey.from_private_key_file(key_file)
        pc.load_system_host_keys()
        pc.connect(sshconf['host'], sshconf['port'], sshconf['username'], pkey=private_key)
    else:
        pc.connect(sshconf['host'], sshconf['port'], sshconf['username'], sshconf['password'])
    stdin, stdout, stderr = pc.exec_command(commands)
    results = stdout.read(), stderr.read()
    for line in results:
        print(line)
    print('%s run command done' % datetime.datetime.now())