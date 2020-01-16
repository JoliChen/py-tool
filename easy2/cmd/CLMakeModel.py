# -*- coding: utf-8 -*-
# @Time    : 2019/5/14 6:37 PM
# @Author  : Joli
# @Email   : 99755349@qq.com

import os
import sys

# 添加根目录搜索路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# print(sys.path)

def main():
    import optparse
    parser = optparse.OptionParser(description='make model tool')
    parser.add_option('--src',
                      dest='src',
                      type='string',
                      default=optparse.NO_DEFAULT,
                      help='模型路径')
    parser.add_option('--dst',
                      dest='dst',
                      type='string',
                      default=optparse.NO_DEFAULT,
                      help='输出路径')
    parser.add_option('--opt',
                      dest='opt',
                      type='string',
                      default=optparse.NO_DEFAULT,
                      help='操作类型')
    (options, args) = parser.parse_args(sys.argv[1:])

    from com.dev import MakeModel
    if options.opt == 'offset':
        offset_x, offset_y = 0, 0
        if args:
            if len(args) > 0:
                if args[0][0] == '0':
                    offset_x = -int(args[0][1:])
                else:
                    offset_x = int(args[0])
            if len(args) > 1:
                if args[1][0] == '0':
                    offset_y = -int(args[1][1:])
                else:
                    offset_y = int(args[1])
        MakeModel.offset(options.src, options.dst, offset_x, offset_y)
    else:
        print('unknow opt:', options.opt)

if __name__ == '__main__':
    main()