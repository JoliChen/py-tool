# -*- coding: utf-8 -*-
# @Time    : 2018/10/8 下午2:39
# @Author  : Joli
# @Email   : 99755349@qq.com
import os
import sys

class CmdTest:
    def __init__(self):
        pass

    @staticmethod
    def test_shell():
        from simples import TestShell
        return TestShell.main()

    @staticmethod
    def test_rob():
        from simples import TestRob
        return TestRob.main()

    @staticmethod
    def test_extension():
        from simples import TestExtension
        return TestExtension.main()

    @staticmethod
    def test_regexp():
        from simples import TestRegexp
        return TestRegexp.main()

    @staticmethod
    def test_lang():
        from simples import TestLang
        return TestLang.main()


class CmdMake:
    def __init__(self):
        self.root = '/Users/joli/Desktop/test'

    @staticmethod
    def make_csd():
        from com.dev import MakeCSD
        MakeCSD.main()

    @staticmethod
    def make_ccs():
        from com.dev import MakeCCS
        MakeCCS.main()

    def make_lua(self):
        from com.dev.MakeScript import LuacBuilder
        lb = LuacBuilder()
        lb.compile(os.path.join(self.root, 'script/lua/src'), os.path.join(self.root, 'script/lua/dst'), is_debug=False)

    @staticmethod
    def make_obb():
        from com.deploy.android import OBB
        OBB.ObbBuilder().build('/Users/joli/Desktop/outputs/obb')

    @staticmethod
    def make_icon():
        from com.arts import MakeIcon
        MakeIcon.make_icons('/Users/joli/Desktop/outputs/icon&images', android=False)

    @staticmethod
    def make_lanunchimages():
        from com.arts import MakeLaunchImage
        MakeLaunchImage.make_images('/Users/joli/Desktop/outputs/icon&images')

    @staticmethod
    def make_asset():
        from com.dev import MakeAsset
        MakeAsset.main()

    @staticmethod
    def make_spine():
        from com.dev import MakeSpine
        MakeSpine.main()

def main():
    # 添加工程搜索路径
    sys.path.append(os.path.abspath(os.path.dirname(__file__)))
    # 设置log等级
    from jonlin.utils import Log
    Log.DEFAULT_LEVEL = Log.DEBUG
    # 执行指令
    opt, tag = sys.argv[1], sys.argv[2]
    getattr({'test': CmdTest(), 'make': CmdMake()}[opt], '%s_%s' % (opt, tag))()

if __name__ == '__main__':
    main()