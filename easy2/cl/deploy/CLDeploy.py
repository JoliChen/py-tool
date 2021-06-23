# -*- coding: utf-8 -*-
# @Time    : 2021/5/8 8:23 PM
# @Author  : Joli
# @Email   : 99755349@qq.com
import sys
import optparse
from scripts import SSHUtil, XLSUtil

def do_test():
    # import os
    # sshconf = {'host': '10.16.101.68', 'port': 61620, 'username': 'uzone', 'password': 'uzone123', 'policy': 'auto'}
    # sshconf = {'host': '10.16.101.68', 'port': 61620, 'username': 'root', 'key': '/Users/joli/.ssh/id_rsa', 'policy': 'auto'}
    # SSHUtil.upload(
    #     sshconf,
    #     localdir='/Users/joli/Work/CS/C/xiuxian_new/docs/server_config',
    #     remotedir='/data/uzone_xiuxiannew_c9300/resources/config2',
    #     allowlist=[])
    # SSHUtil.run(sshconf, 'ls -l')

    # projdir = '/Users/joli/Work/CS/C/xiuxian_new'
    # xlsxdir = os.path.join(projdir, 'docs/config')
    # jsondir = os.path.join(projdir, 'dazhanguo/tmp/config_out')
    # XLSUtil.write(jsondir, xlsxdir, wballows=['JiYuan'])
    # XLSUtil.read(xlsxdir, None, wballows=['JiYuan'])
    pass

def do_ssh(opts, args):
    sshconf = {
        'host': opts.host,
        'port': opts.port,
        'username': opts.username,
        'password': opts.password,
        'key': opts.key,
        'policy': opts.policy
    }
    if opts.run:
        SSHUtil.run(sshconf, opts.command)
    elif opts.upload:
        allowlist = opts.allowlist.split(',') if opts.allowlist else None
        SSHUtil.upload(sshconf, opts.localdir, opts.remotedir, allowlist)
    else:
        pass

def do_excel(opts, args):
    wballows = opts.wballows.split(',') if opts.wballows else None
    wsallows = opts.wsallows.split(',') if opts.wsallows else None
    if opts.action == 'write':
        XLSUtil.write(opts.jsondir, opts.xlsxdir, wballows, wsallows)
    elif opts.action == 'read':
        XLSUtil.read(opts.xlsxdir,  opts.jsondir, wballows, wsallows)

def main():
    op = optparse.OptionParser(description='部署辅助工具')
    op.add_option('--do', dest='do', help='任务类型[ssh、excel]')

    og_ssh_login = optparse.OptionGroup(op, 'SSH登录配置')
    og_ssh_login.add_option('--host', dest='host', help='主机IP'),
    og_ssh_login.add_option('--port', dest='port', type='int', help='主机端口'),
    og_ssh_login.add_option('--username', dest='username', help='用户名称'),
    og_ssh_login.add_option('--password', dest='password', help='登录密码'),
    og_ssh_login.add_option('--key', dest='key', help='用户秘钥(id_rsa)'),
    og_ssh_login.add_option('--policy', dest='policy', default='auto', help='登录策略[auto, reject, warnning]')
    op.add_option_group(og_ssh_login)

    og_ssh_run = optparse.OptionGroup(op, 'SSH远程命令')
    og_ssh_run.add_option('--run', action="store_true", help='ssh远程命令')
    og_ssh_run.add_option('--command', dest='localdir', help='本地目录')
    op.add_option_group(og_ssh_run)

    og_ssh_upload = optparse.OptionGroup(op, 'SSH上传文件')
    og_ssh_upload.add_option('--upload', action="store_true", help='ssh上传')
    og_ssh_upload.add_option('--localdir', dest='localdir', help='本地目录')
    og_ssh_upload.add_option('--remotedir', dest='remotedir', help='远程目录')
    og_ssh_upload.add_option('--allowlist', dest='allowlist', help='白名单')
    op.add_option_group(og_ssh_upload)

    og_excel = optparse.OptionGroup(op, 'excel操作')
    og_excel.add_option('--action', dest='action', help='excel操作[read, write]')
    og_excel.add_option('--xlsxdir', dest='xlsxdir', help='xlsx文件目录')
    og_excel.add_option('--jsondir', dest='jsondir', help='json文件目录')
    og_excel.add_option('--wballows', dest='wballows', help='excel白名单')
    og_excel.add_option('--wsallows', dest='wsallows', help='sheet白名单')
    op.add_option_group(og_excel)

    (opts, args) = op.parse_args(sys.argv[1:])
    if opts and opts.do:
        getattr(sys.modules[__name__], 'do_%s' % opts.do)(opts, args)
    else:
        do_test()

if __name__ == '__main__':
    main()