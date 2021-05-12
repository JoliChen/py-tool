# -*- coding: utf-8 -*-
# @Time    : 2019/3/25 4:43 PM
# @Author  : Joli
# @Email   : 99755349@qq.com
import sys
import optparse
from scripts.MakeSheet2 import SheetBuilder

def do_test():
    sb = SheetBuilder()
    sb.set_editor()
    sb.build(
        '/Users/joli/Work/CS/C/xiuxian_new/docs/config',
        '/Users/joli/Work/CS/C/xiuxian_new/dazhanguo/res/config')

def do_export(opts):
    denylist = None if opts.denylist is None else opts.denylist.split(',')
    allowlist = None if opts.allowlist is None else opts.allowlist.split(',')
    sb = SheetBuilder(opts.listwarn, opts.listerr, opts.canalert)
    sb.set_editor(opts.data_format)
    sb.build(opts.sheet_dir, opts.data_path, denylist, allowlist)

def main():
    op = optparse.OptionParser(description='make sheet tool')
    op.add_option('-i', dest='sheet_dir', help='表文件夹路径')
    op.add_option('-o', dest='data_path', help='输出路径')
    op.add_option('-f', dest='data_format', default='binary', help='输出格式:[binary,lua]')
    op.add_option('-b', dest='denylist', help='黑名单(使用逗号分隔)')
    op.add_option('-w', dest='allowlist', help='白名单(使用逗号分隔)')
    op.add_option('-e', dest='error_file', help='deprecated option, use "--listerr".')
    op.add_option('--listerr',  dest='listerr', action="store_true",  default=False, help='输出错误')
    op.add_option('--listwarn', dest='listwarn',  action="store_true",  default=False, help='输出警告')
    op.add_option('--canalert',  dest='canalert',   action="store_true", default=False,  help='弹出导表错误提示框')

    (opts, args) = op.parse_args(sys.argv[1:])
    if opts and opts.sheet_dir:
        do_export(opts)
    else:
        do_test()

if __name__ == '__main__':
    main()