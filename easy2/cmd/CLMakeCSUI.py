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
    parser = optparse.OptionParser(description='make csui tool')
    parser.add_option('--src',
                      dest='src',
                      type='string',
                      default=optparse.NO_DEFAULT,
                      help='原始路径')
    parser.add_option('--dst',
                      dest='dst',
                      type='string',
                      default=optparse.NO_DEFAULT,
                      help='输出路径')
    parser.add_option('--dangling',
                      dest='dangling',
                      type='int',
                      default=2,
                      help='悬空节点[0-不处理, 1-输出日志, 2-删除节点] 默认2')
    parser.add_option('--hidden',
                      dest='hidden',
                      type='int',
                      default=1,
                      help='隐藏节点[0-不处理, 1-输出日志, 2-删除节点] 默认1')
    parser.add_option('--repeat',
                      dest='repeat',
                      type='int',
                      default=0,
                      help='重名节点[0-不处理, 1-输出日志, 2-删除节点] 默认0')
    (options, args) = parser.parse_args(sys.argv[1:])

    from com.dev.MakeCSUI import LuaCSBuilder
    cs = LuaCSBuilder(options.dangling, options.hidden, options.repeat)
    cs.build(options.src, options.dst)

if __name__ == '__main__':
    main()