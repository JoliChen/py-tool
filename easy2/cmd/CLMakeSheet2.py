# -*- coding: utf-8 -*-
# @Time    : 2019/3/25 4:43 PM
# @Author  : Joli
# @Email   : 99755349@qq.com
import os
import sys

# 添加根目录搜索路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# print(sys.path)

def main():
    import optparse
    parser = optparse.OptionParser(description='make sheet tool')
    parser.add_option('-i',
                      dest='sheet_dir',
                      type='string',
                      default=optparse.NO_DEFAULT,
                      help='表文件夹路径')
    parser.add_option('-o',
                      dest='data_path',
                      type='string',
                      default=optparse.NO_DEFAULT,
                      help='输出路径')
    parser.add_option('-f',
                      dest='data_format',
                      type='string',
                      default='binary',
                      help='输出格式 [binary, lua]')
    parser.add_option('-b',
                      dest='black_list',
                      type='string',
                      default=optparse.NO_DEFAULT,
                      help='黑名单(使用逗号分隔)')
    parser.add_option('--forceone',
                      dest='forceone',
                      action="store_true",
                      default=False,
                      help='合并成一个文件')
    parser.add_option('-e',
                      dest='error_file',
                      type='string',
                      default=optparse.NO_DEFAULT,
                      help='deprecated option, use "--listerr".')
    parser.add_option('--listerr',
                      dest='list_error',
                      action="store_true",
                      default=False,
                      help='输出错误')
    parser.add_option('--listwarn',
                      dest='list_warn',
                      action="store_true",
                      default=False,
                      help='输出警告')
    parser.add_option('--noalert',
                      dest='no_alert',
                      action="store_false",
                      default=True,
                      help='弹出导表错误提示框')
    (options, args) = parser.parse_args(sys.argv[1:])

    # 开始导表
    from com.dev.MakeSheet2 import SheetBuilder
    sb = SheetBuilder().set_editor(options.data_format, options.forceone)
    sb.build(options.sheet_dir, options.data_path,
                black_list=options.black_list,
                list_warn=options.list_warn,
                list_error=options.list_error,
                alert=options.no_alert)

if __name__ == '__main__':
    main()