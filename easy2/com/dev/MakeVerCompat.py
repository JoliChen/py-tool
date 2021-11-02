# -*- coding: utf-8 -*-
# @Time    : 2021/11/1 8:33 PM
# @Author  : Joli
# @Email   : 99755349@qq.com
import hashlib
import math
import os
import re
import shutil
import time

class Log:
    @staticmethod
    def i(*args):
        print(*args)

    @staticmethod
    def e(*args):
        print(*args)

class Kit:
    @staticmethod
    def normposix(path):
        return '/'.join(path.split('\\'))

    @staticmethod
    def get_filename(filepath):
        return filepath[filepath.rfind(os.sep) + 1: filepath.rfind('.')]

    @staticmethod
    def get_filemd5(filepath):
        with open(filepath, 'rb') as fp:
            h = hashlib.md5()
            h.update(fp.read())
            return h.hexdigest()

    @staticmethod
    def make_parentdir(filepath):
        pardir = os.path.dirname(filepath)
        if not os.path.isdir(pardir):
            os.makedirs(pardir)

    @staticmethod
    def safe_copyfile(src, dst):
        Kit.make_parentdir(dst)
        shutil.copyfile(src, dst)

    @staticmethod
    def is_meta_modified(src, dst):
        st1 = os.stat(src)
        st2 = os.stat(dst)
        if st1.st_size != st2.st_size:
            return True
        mt1 = math.floor(st1.st_mtime * 1000)
        mt2 = math.floor(st2.st_mtime * 1000)
        return mt1 != mt2

    @staticmethod
    def compare_dir(srcdir, dstdir):
        fid_slice = len(srcdir) + 1
        for root, _, files in os.walk(srcdir):
            for fn in files:
                src = os.path.join(root, fn)
                fid = src[fid_slice:]
                # print(fid)
                dst = os.path.join(dstdir, fid)
                if not os.path.isfile(dst):
                    print("miss", fid)

class SvnClient:
    def __init__(self, commandline='svn'):
        self.cl = commandline

    def get_revision(self, localdir='.'):
        cmd = '%s info "%s"' % (self.cl, localdir)
        with os.popen(cmd) as fp:
            for s in fp.readlines():
                if s.find('Revision:') == 0 or s.find('版本:') == 0:
                    reversions = re.findall(r'\d+', s)
                    if reversions:
                        return int(reversions[0])

class CocosProject:
    # 热更模式、整包模式
    kHOTFIX, kBUNDLE = 'hotfix', 'bundle'

    # 这部分CSB打包到base.pak
    PACK_CSB_TO_BASE = (
        'loading',
        'Login',
        'Plugins',
        'G_All',
        'huanpi',
        'Gang',
        'Activity',
        'formation',
        'CountryWar_new',
        'classicBattle',
        'Pet',
        'mainCity',
        'Animals',
        'battle',
        'Drama',
        'DramaCartoon'
    )

    def __init__(self, projdir):
        self.projdir = projdir
        self.shelldir = os.path.join(projdir, 'make')
        self.toolsdir = os.path.join(projdir, 'tools')
        self.builddir = os.path.join(projdir, 'build')
        self.ccsuidir = os.path.join(projdir, 'CocosProject')
        self.ccsrtdir = os.path.join(projdir, 'dazhanguo')  # cocos runtime dir
        self.srcdir = os.path.join(self.ccsrtdir, 'src')
        self.resdir = os.path.join(self.ccsrtdir, 'res')
        self.teakey = b'$yz#z0X78'  # xxtea秘钥
        self.teasig = b'0x0305~yz'  # xxtea签名
        self.svnclient = SvnClient()
        Log.i('projdir',  self.projdir)
        Log.i('shelldir', self.shelldir)
        Log.i('toolsdir', self.toolsdir)
        Log.i('builddir', self.builddir)
        Log.i('ccsrtdir', self.ccsrtdir)
        Log.i('ccsuidir', self.ccsuidir)

    def pack_lua_script(self, zipname):
        dst_dir = os.path.join(self.builddir, zipname)
        if os.path.isdir(dst_dir):
            shutil.rmtree(dst_dir)
        luafile = 'main.lua'
        Kit.safe_copyfile(os.path.join(self.srcdir, luafile), os.path.join(dst_dir, luafile))
        luafile = 'app/yzframe/update/updateUI.lua'
        Kit.safe_copyfile(os.path.join(self.srcdir, luafile), os.path.join(dst_dir, luafile))


    def pack_lua_base(self, zipname):
        dst_dir = os.path.join(self.builddir, zipname)
        # os.makedirs(dst_dir)

    def pack_lua_csb(self, zipname):
        dst_dir = os.path.join(self.builddir, zipname)
        # os.makedirs(dst_dir)

    def pack_lua_modules(self, zipname):
        dst_dir = os.path.join(self.builddir, zipname)
        # os.makedirs(dst_dir)

    def zip_lua(self, zipname):
        if zipname == 'csb':
            self.pack_lua_csb(zipname)
        elif zipname == 'modules':
            self.pack_lua_modules(zipname)
        elif zipname == 'base':
            self.pack_lua_base(zipname)
        elif zipname == 'script':
            self.pack_lua_script(zipname)

    def make_lua(self):
        self.zip_lua('csb')
        self.zip_lua('modules')
        self.zip_lua('base')
        self.zip_lua('script')

    def make_res(self):
        pass

class CocosBuilder(CocosProject):
    kHOTFIX, kBUNDLE = 'hotfix', 'bundle'  # 热更模式、整包模式

    def __init__(self, projdir):
        CocosProject.__init__(self, projdir)

    def load_oldmainifest(self):
        pass

    # @param major  程序版本
    # @param minor  资源版本
    # @param mode   [hotfix, bundle]
    def build(self, major, minor, mode):
        t = time.time()
        if 0 == minor:
            minor = self.svnclient.get_revision(self.ccsrtdir)
        self.version = (major, minor)
        self.buildmode = mode

        self.make_lua()

        print('done %smin' % round((time.time() - t) / 60, 3))

    def hotfix(self, major, minor=0):
        return self.build(major, minor, CocosBuilder.kHOTFIX)

    def bundle(self, major, minor=0):
        return self.build(major, minor, CocosBuilder.kBUNDLE)

def main():
    # builder = CocosBuilder(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    builder = CocosBuilder('/Users/joli/Downloads/xxx')
    # builder.bundle(16774)
    builder.hotfix(16774, 99999)

    from jonlin.utils import FS
    FS.explorer(builder.builddir)

if __name__ == '__main__':
    main()