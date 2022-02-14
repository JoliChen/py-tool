# -*- coding: utf-8 -*-
# @Time    : 2021/11/1 8:33 PM
# @Author  : Joli
# @Email   : 99755349@qq.com
import ast
import hashlib
import math
import os
import re
import shutil
import time
import xxtea

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
    def get_filename(dstfile):
        return dstfile[dstfile.rfind(os.sep) + 1: dstfile.rfind('.')]

    @staticmethod
    def make_parentdir(dstfile):
        parent = os.path.dirname(dstfile)
        if not os.path.isdir(parent):
            os.makedirs(parent)

    @staticmethod
    def rmdirs(dstdir):
        if os.path.isdir(dstdir):
            shutil.rmtree(dstdir)

    @staticmethod
    def cleandir(dstdir):
        if os.path.isdir(dstdir):
            shutil.rmtree(dstdir)
        os.makedirs(dstdir)

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

    @staticmethod
    def safe_copyfile(srcfile, dstfile):
        Kit.make_parentdir(dstfile)
        shutil.copyfile(srcfile, dstfile)

    @staticmethod
    def fast_copytree(srcdir, dstdir, ignore_function=None):
        Kit.rmdirs(dstdir)
        shutil.copytree(srcdir, dstdir, ignore=ignore_function, copy_function=shutil.copyfile)

    @staticmethod
    def mergetree(srcdir, dstdir, copy_function=shutil.copyfile):
        if not os.path.isdir(dstdir):
            os.makedirs(dstdir)
        for name in os.listdir(srcdir):
            sp = os.path.join(srcdir, name)
            dp = os.path.join(dstdir, name)
            if os.path.isdir(sp):
                Kit.mergetree(sp, dp, copy_function)
            else:
                copy_function(sp, dp)

    @staticmethod
    def clean_empty_dirs(rootdir):
        for (parent, dirs, _) in os.walk(rootdir):
            for fn in dirs:
                dirpath = os.path.join(parent, fn)
                if not os.listdir(dirpath):
                    os.rmdir(dirpath)

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
    def get_filesize(filepath):
        return os.path.getsize(filepath)

    @staticmethod
    def get_filemd5(filepath):
        with open(filepath, 'rb') as fp:
            h = hashlib.md5()
            h.update(fp.read())
            return h.hexdigest()

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

class BaseProject:
    # xxtea
    TEA_KEY = b'$yz#z0X78'  # xxtea秘钥
    TEA_SIG = b'0x0305~yz'  # xxtea签名

    def __init__(self, projdir, major):
        self.majorver = major
        self.projdir = projdir
        self.builddir = os.path.join(projdir, 'build')
        self.appdir = os.path.join(projdir, 'dazhanguo')  # application dir
        self.patchdir = os.path.join(self.appdir, 'patch')  # patch dir
        self.hotfix_manifest_txt = os.path.join(self.patchdir, 'manifest_hotfix.txt')
        self.bundle_manifest_txt = os.path.join(self.patchdir, 'manifest_bundle.txt')
        self.svnclient = SvnClient()

        self.teakey = self.TEA_KEY + bytes(16 - len(self.TEA_KEY))  # need a 16-byte key.
        self.teasig = self.TEA_SIG  # xxtea签名

        Log.i('projdir',  self.projdir)
        Log.i('builddir', self.builddir)
        Log.i('patchdir', self.patchdir)
        Log.i('appdir',   self.appdir)

    def encrypt_file(self, src, dst):
        with open(src, 'rb') as sfp:
            data = sfp.read()
        n = len(data)
        data += bytes((4 - n % 4) & 3) + bytes([n & 0xFF, n >> 8 & 0xFF, n >> 16 & 0xFF, n >> 24 & 0xFF])
        data = xxtea.encrypt(data, self.teakey, padding=False)
        data = self.teasig + data
        Kit.make_parentdir(dst)
        with open(dst, 'wb') as dfp:
            dfp.write(data)

    def encrypt_res(self, res_dir):
        for (parent, _, files) in os.walk(res_dir):
            for fn in files:
                if fn.endswith('.plist'):
                    fn = os.path.join(parent, fn)
                    self.encrypt_file(fn, fn)
        Log.i('encrypt res done')

    @staticmethod
    def create_fileinfo(filepath, namepos):
        name = Kit.normposix(filepath[namepos:])
        md5  = Kit.get_filemd5(filepath)
        size = Kit.get_filesize(filepath)
        return {'patchName': name, 'md5': md5, 'size': size}

    @staticmethod
    def collect_manifest(rootdir, namepos, filedict):
        for (parent, _, files) in os.walk(rootdir):
            for fn in files:
                fp = os.path.join(parent, fn)
                name = Kit.normposix(fp[namepos:])
                filedict[name] = {'md5': Kit.get_filemd5(fp), 'size': Kit.get_filesize(fp)}

    @staticmethod
    def load_old_manifest(txtpath):
        filedict = {}
        if os.path.isfile(txtpath):
            with open(txtpath, 'r') as fp:
                for s in fp.readlines():
                    fileinfo = ast.literal_eval(s)
                    name = fileinfo['patchName']
                    if not name.startswith('res/') and not name.startswith('src/'):
                        name = 'res/' + name  # 兼容旧版本
                        fileinfo['patchName'] = name
                    filedict[name] = fileinfo
        return filedict

    @staticmethod
    def save_manifest(txtpath, filedict):
        s = ''
        for (name, info) in filedict.items():
            if name.endswith('.DS_Store'):
                continue
            s += "{'patchName':'%s', 'md5':'%s', 'size':%d}\n" % (name, info['md5'], info['size'])
        Kit.make_parentdir(txtpath)
        with open(txtpath, 'w') as fp:
            fp.write(s)
        Log.i('safe manifest done %s' % txtpath)

    @staticmethod
    def create_flist(filedict, major, minor):
        s = ''
        reg_key = re.compile(r'[/.]')
        reg_err = re.compile(r'[^0-9a-zA-Z_/.-]')
        for (name, info) in filedict.items():
            if name.endswith('.DS_Store'):
                continue
            if reg_err.search(name):
                raise ValueError('error file name: %s' % name)
            k = reg_key.sub('', name)
            s += "%s={patchName='%s', md5='%s', size=%d},\n" % (k, name, info['md5'], info['size'])
        s = "return {\nstage={\n%s},\ncurVer='%d.%d',\n}" % (s, major, minor)
        return s

    def save_flist(self, verdir, major, minor):
        if 0 == major:
            major = self.majorver
        if 0 == minor:
            minor = self.svnclient.get_revision(self.appdir)
        filedir = os.path.join(verdir, 'myfile')
        namepos = len(verdir) + 1
        filedict = {}
        for (parent, _, files) in os.walk(filedir):
            for fn in files:
                fp = os.path.join(parent, fn)
                name = Kit.normposix(fp[namepos:])
                filedict[name] = {'md5': Kit.get_filemd5(fp), 'size': Kit.get_filesize(fp)}
        s = self.create_flist(filedict, major, minor)
        txtpath = os.path.join(verdir, 'flist')
        Kit.make_parentdir(txtpath)
        with open(txtpath, 'w') as fp:
            fp.write(s)
        Log.i('save flist done [major:%d, minor:%d] %s' % (major, minor, txtpath))

# 战国项目（特征是配置表是lua格式）
class OldProject(BaseProject):
    # 脚本包
    LUA_PACKAGES = ('script', 'modules', 'config')

    def __init__(self, projdir, major):
        super(OldProject, self).__init__(projdir, major)

    @staticmethod
    def _mklua_script(srcdir, luadir):
        namepos = len(srcdir) + 1

        def filter_func(folder, names):
            ignored_names = set()
            for fn in names:
                fp = os.path.join(folder, fn)
                fk = Kit.normposix(fp[namepos:])
                if fk.startswith('config/'):
                    ignored_names.add(fn)
                elif fk.startswith('app/modules'):
                    ignored_names.add(fn)
            return ignored_names

        Kit.fast_copytree(srcdir, luadir, filter_func)
        Log.i('make luadir', luadir)

    @staticmethod
    def _mklua_modules(srcdir, luadir):
        Kit.fast_copytree(os.path.join(srcdir, 'app/modules'), os.path.join(luadir, 'app/modules'))
        Log.i('make luadir', luadir)

    @staticmethod
    def _mklua_config(srcdir, luadir):
        Kit.fast_copytree(os.path.join(srcdir, 'config'), os.path.join(luadir, 'config'))
        Log.i('make luadir', luadir)

    def make_luadirs(self, dstdir, packages=LUA_PACKAGES):
        srcdir = os.path.join(self.appdir, 'src')
        for name in packages:
            luadir = os.path.join(dstdir, name)
            getattr(self, '_mklua_%s' % name)(srcdir, luadir)
        Log.i('make all luadir done')

    def pack_luazips(self, dstdir, packages=LUA_PACKAGES):
        for name in packages:
            luadir = os.path.join(dstdir, name)
            if os.path.isdir(luadir):
                zippath = shutil.make_archive(luadir, 'zip', luadir)
                self.encrypt_file(zippath, zippath)
                os.rename(zippath, zippath.replace('.zip', '.pak'))
                shutil.rmtree(luadir)
        Log.i('pack all lua done')

    @staticmethod
    def classify_luapkgs(luapkgs, fk):
        if fk.startswith('app/modules'):
            luapkgs.add('modules')
        elif fk.startswith('config/'):
            luapkgs.add('config')
        else:
            luapkgs.add('script')

    def make_changed_src(self, dstdir, old_filedict, new_filedict):
        luapkgs = set()  # 'csb', 'modules', 'base', 'script'
        namepos = len(self.appdir) + 1
        for (parent, _, files) in os.walk(os.path.join(self.appdir, 'src')):
            for fn in files:
                if fn == '.DS_Store':
                    continue
                fp = os.path.join(parent, fn)
                new_fileinfo = self.create_fileinfo(fp, namepos)
                fk = new_fileinfo['patchName']
                new_filedict[fk] = new_fileinfo
                old_fileinfo = old_filedict.get(fk)
                if (not old_fileinfo) or (old_fileinfo['md5'] != new_fileinfo['md5']):
                    self.classify_luapkgs(luapkgs, fk[4:])  # 去掉'src/'
        if luapkgs:
            self.make_luadirs(dstdir, luapkgs)
            self.pack_luazips(dstdir, luapkgs)
        Log.i('make changed src done')

    def make_changed_res(self, dstdir, old_filedict, new_filedict):
        namepos = len(self.appdir) + 1
        for (parent, _, files) in os.walk(os.path.join(self.appdir, 'res')):
            for fn in files:
                if fn == '.DS_Store':
                    continue
                fp = os.path.join(parent, fn)
                new_fileinfo = self.create_fileinfo(fp, namepos)
                name = new_fileinfo['patchName']
                new_filedict[name] = new_fileinfo
                old_fileinfo = old_filedict.get(name)
                if (not old_fileinfo) or (old_fileinfo['md5'] != new_fileinfo['md5']):
                    Kit.safe_copyfile(fp, os.path.join(dstdir, name))
        Log.i('make changed res done')

    def hotfix(self, major=0, minor=0):
        t = time.time()
        verdir = os.path.join(self.patchdir, 'version')
        hotdir = os.path.join(self.builddir, 'hotfix')
        newdir = os.path.join(hotdir, 'version')  # 新版本目录
        # 初始化版本清单
        has_modified = False
        new_filedict = {}
        if os.path.isfile(self.hotfix_manifest_txt):
            old_filedict = self.load_old_manifest(self.hotfix_manifest_txt)
        else:
            old_filedict = self.load_old_manifest(self.bundle_manifest_txt)
        # 拷贝基础版本
        Kit.rmdirs(hotdir)
        if os.path.isdir(verdir):
            Kit.fast_copytree(verdir, newdir)
        # 打包脚本
        srcdir = os.path.join(hotdir, 'src')
        self.make_changed_src(srcdir, old_filedict, new_filedict)
        if os.path.isdir(srcdir):
            Kit.mergetree(srcdir, os.path.join(newdir, 'myfile'))  # 把新的脚本包合并到基础版本
            has_modified = True
        # 打包资源
        resdir = os.path.join(hotdir, 'res')
        self.make_changed_res(hotdir, old_filedict, new_filedict)
        if os.path.isdir(resdir):
            self.encrypt_res(resdir)  # 加密资源
            dstdir = os.path.join(newdir, 'myfile', 'res')
            Kit.mergetree(resdir, dstdir)  # 把新的加密资源合并到基础版本里
            has_modified = True
        if not has_modified:
            Log.i('nothing has modified')
            return
        # 生成新版本
        self.save_flist(newdir, major, minor)  # 保存flist
        if os.path.isdir(verdir):
            bakdir = os.path.join(self.patchdir, 'backup', time.strftime('%Y-%m-%d %X'))
            Kit.make_parentdir(bakdir)
            shutil.move(verdir, bakdir)
        shutil.move(newdir, verdir)
        # 保存版本清单
        self.save_manifest(self.hotfix_manifest_txt, new_filedict)
        print('hotfix done %smin' % round((time.time() - t) / 60, 3))

    def bundle(self, major=0, minor=0):
        t = time.time()
        bundledir = os.path.join(self.builddir, 'bundle')
        myfiledir = os.path.join(bundledir, 'myfile')
        # 打包脚本
        appsrcdir = os.path.join(self.appdir, 'src')
        Kit.rmdirs(bundledir)
        self.make_luadirs(myfiledir)
        self.pack_luazips(myfiledir)
        # 打包资源
        appresdir = os.path.join(self.appdir, 'res')
        dstresdir = os.path.join(myfiledir, 'res')
        Kit.fast_copytree(appresdir, dstresdir)
        self.encrypt_res(dstresdir)
        # 生成flist
        self.save_flist(bundledir, major, minor)
        # 去掉myfile文件夹
        for fn in os.listdir(myfiledir):
            shutil.move(os.path.join(myfiledir, fn), os.path.join(bundledir, fn))
        os.rmdir(myfiledir)
        # 生成版本清单
        new_filedict = {}
        namepos = len(self.appdir) + 1
        self.collect_manifest(appsrcdir, namepos, new_filedict)
        self.collect_manifest(appresdir, namepos, new_filedict)
        self.save_manifest(self.bundle_manifest_txt, new_filedict)
        print('bundle done %smin' % round((time.time() - t) / 60, 3))

# 修仙项目（特征是配置表是ulo格式）
class UloProject(BaseProject):
    # 脚本包
    LUA_PACKAGES = ('csb', 'modules', 'base', 'script')
    # 打包到script包的文件
    LUA_SCRIPT_FILES = ('main.lua', 'app/yzframe/update/updateUI.lua')
    # 打包到base包的CSB
    LUA_BASE_CSBLIST = (
        'Activity',
        'G_All',
        'huanpi',
        'loading',
        'Login',
        'mainCity',
        'Plugins',
        'Gang',
        'formation',
        'CountryWar_new',
        'classicBattle',
        'Pet',
        'Animals',
        'battle',
        'Drama',
        'DramaCartoon'
    )

    def __init__(self, projdir, major):
        super(UloProject, self).__init__(projdir, major)

    @staticmethod
    def classify_luapkgs(luapkgs, fk):
        if fk.startswith('csb/'):
            ep = fk.find('/', 4)
            csbname = fk[4: ep] if ep > 0 else fk[4:]
            if csbname in UloProject.LUA_BASE_CSBLIST:
                luapkgs.add('base')
            else:
                luapkgs.add('csb')
        elif fk.startswith('app/modules'):
            luapkgs.add('modules')
        elif fk in UloProject.LUA_SCRIPT_FILES:
            luapkgs.add('script')
        else:
            luapkgs.add('base')

    @staticmethod
    def _mklua_base(srcdir, luadir):
        namepos = len(srcdir) + 1

        def filter_func(folder, names):
            ignored_names = set()
            for fn in names:
                fp = os.path.join(folder, fn)
                fk = Kit.normposix(fp[namepos:])
                if fk.startswith('csb/'):
                    ep = fk.find('/', 4)
                    csbname = fk[4: ep] if ep > 0 else fk[4:]
                    if csbname not in UloProject.LUA_BASE_CSBLIST:
                        ignored_names.add(fn)
                elif fk.startswith('app/modules'):
                    ignored_names.add(fn)
                elif fk in UloProject.LUA_SCRIPT_FILES:
                    ignored_names.add(fn)
            return ignored_names
        Kit.fast_copytree(srcdir, luadir, filter_func)
        Log.i('make luadir', luadir)

    @staticmethod
    def _mklua_csb(srcdir, luadir):
        csbdir = os.path.join(srcdir, 'csb')
        namepos = len(csbdir) + 1

        def filter_func(folder, names):
            ignored_names = set()
            for fn in names:
                fp = os.path.join(folder, fn)
                fk = Kit.normposix(fp[namepos:])
                ep = fk.find('/')
                csbname = fk[:ep] if ep > 0 else fk
                if csbname in UloProject.LUA_BASE_CSBLIST:
                    ignored_names.add(fn)
            return ignored_names
        Kit.fast_copytree(csbdir, os.path.join(luadir, 'csb'), filter_func)
        Log.i('make luadir', luadir)

    def _mklua_script(self, srcdir, luadir):
        for fn in self.LUA_SCRIPT_FILES:
            Kit.safe_copyfile(os.path.join(srcdir, fn), os.path.join(luadir, fn))
        Log.i('make luadir', luadir)

    @staticmethod
    def _mklua_modules(srcdir, luadir):
        Kit.fast_copytree(os.path.join(srcdir, 'app/modules'), os.path.join(luadir, 'app/modules'))
        Log.i('make luadir', luadir)

    def make_luadirs(self, dstdir, packages=LUA_PACKAGES):
        srcdir = os.path.join(self.appdir, 'src')
        for name in packages:
            luadir = os.path.join(dstdir, name)
            getattr(self, '_mklua_%s' % name)(srcdir, luadir)
        Log.i('make all luadir done')

    def pack_luazips(self, dstdir, packages=LUA_PACKAGES):
        for name in packages:
            luadir = os.path.join(dstdir, name)
            if os.path.isdir(luadir):
                zippath = shutil.make_archive(luadir, 'zip', luadir)
                self.encrypt_file(zippath, zippath)
                os.rename(zippath, zippath.replace('.zip', '.pak'))
                shutil.rmtree(luadir)
        Log.i('pack all lua done')

    @staticmethod
    def merge_config(dstdir):
        cfgdir = os.path.join(dstdir, 'config')
        cfgzip = os.path.join(cfgdir, 'config.zip')
        if not os.path.isfile(cfgzip):
            return
        unzdir = os.path.join(dstdir, 'config_unzip')
        shutil.unpack_archive(cfgzip, unzdir)  # 解压基础版本配置表压缩包
        os.remove(cfgzip)
        Kit.mergetree(cfgdir, unzdir)
        newzip = shutil.make_archive(unzdir, 'zip', unzdir)
        Kit.cleandir(cfgdir)
        shutil.move(newzip, cfgzip)
        shutil.rmtree(unzdir)

    def make_changed_res(self, dstdir, old_filedict, new_filedict):
        namepos = len(self.appdir) + 1
        for (parent, _, files) in os.walk(os.path.join(self.appdir, 'res')):
            for fn in files:
                if fn == '.DS_Store':
                    continue
                fp = os.path.join(parent, fn)
                new_fileinfo = self.create_fileinfo(fp, namepos)
                name = new_fileinfo['patchName']
                new_filedict[name] = new_fileinfo
                old_fileinfo = old_filedict.get(name)
                if (not old_fileinfo) or (old_fileinfo['md5'] != new_fileinfo['md5']):
                    Kit.safe_copyfile(fp, os.path.join(dstdir, name))
        Log.i('make changed res done')

    def make_changed_src(self, dstdir, old_filedict, new_filedict):
        luapkgs = set()  # 'csb', 'modules', 'base', 'script'
        namepos = len(self.appdir) + 1
        for (parent, _, files) in os.walk(os.path.join(self.appdir, 'src')):
            for fn in files:
                if fn == '.DS_Store':
                    continue
                fp = os.path.join(parent, fn)
                new_fileinfo = self.create_fileinfo(fp, namepos)
                fk = new_fileinfo['patchName']
                new_filedict[fk] = new_fileinfo
                old_fileinfo = old_filedict.get(fk)
                if (not old_fileinfo) or (old_fileinfo['md5'] != new_fileinfo['md5']):
                    self.classify_luapkgs(luapkgs, fk[4:])  # 去掉'src/'
        if luapkgs:
            self.make_luadirs(dstdir, luapkgs)
            self.pack_luazips(dstdir, luapkgs)
        Log.i('make changed src done')

    def hotfix(self, major=0, minor=0):
        t = time.time()
        verdir = os.path.join(self.patchdir, 'version')
        hotdir = os.path.join(self.builddir, 'hotfix')
        newdir = os.path.join(hotdir, 'version')  # 新版本目录
        # 初始化版本清单
        has_modified = False
        new_filedict = {}
        if os.path.isfile(self.hotfix_manifest_txt):
            old_filedict = self.load_old_manifest(self.hotfix_manifest_txt)
        else:
            old_filedict = self.load_old_manifest(self.bundle_manifest_txt)
        # 拷贝基础版本
        Kit.rmdirs(hotdir)
        if os.path.isdir(verdir):
            Kit.fast_copytree(verdir, newdir)
        # 打包脚本
        srcdir = os.path.join(hotdir, 'src')
        self.make_changed_src(srcdir, old_filedict, new_filedict)
        if os.path.isdir(srcdir):
            Kit.mergetree(srcdir, os.path.join(newdir, 'myfile'))  # 把新的脚本包合并到基础版本
            has_modified = True
        # 打包资源
        resdir = os.path.join(hotdir, 'res')
        self.make_changed_res(hotdir, old_filedict, new_filedict)
        if os.path.isdir(resdir):
            self.encrypt_res(resdir)  # 加密资源
            dstdir = os.path.join(newdir, 'myfile', 'res')
            cfgdir = os.path.join(resdir, 'config')
            Kit.mergetree(resdir, dstdir)  # 把新的加密资源合并到基础版本里
            if os.path.isdir(cfgdir) and os.listdir(cfgdir):
                self.merge_config(dstdir)  # 合并旧版本配置表
            has_modified = True
        if not has_modified:
            Log.i('nothing has modified')
            return
        # 生成新版本
        self.save_flist(newdir, major, minor)  # 保存flist
        if os.path.isdir(verdir):
            bakdir = os.path.join(self.patchdir, 'backup', time.strftime('%Y-%m-%d %X'))
            Kit.make_parentdir(bakdir)
            shutil.move(verdir, bakdir)
        shutil.move(newdir, verdir)
        # 保存版本清单
        self.save_manifest(self.hotfix_manifest_txt, new_filedict)
        print('hotfix done %smin' % round((time.time() - t) / 60, 3))

    def bundle(self, major=0, minor=0):
        t = time.time()
        bundledir = os.path.join(self.builddir, 'bundle')
        myfiledir = os.path.join(bundledir, 'myfile')
        # 打包脚本
        appsrcdir = os.path.join(self.appdir, 'src')
        Kit.rmdirs(bundledir)
        self.make_luadirs(myfiledir)
        self.pack_luazips(myfiledir)
        # 打包资源
        appresdir = os.path.join(self.appdir, 'res')
        dstresdir = os.path.join(myfiledir, 'res')
        Kit.fast_copytree(appresdir, dstresdir)
        self.encrypt_res(dstresdir)
        # 生成flist
        self.save_flist(bundledir, major, minor)
        # 去掉myfile文件夹
        for fn in os.listdir(myfiledir):
            shutil.move(os.path.join(myfiledir, fn), os.path.join(bundledir, fn))
        os.rmdir(myfiledir)
        # 生成版本清单
        new_filedict = {}
        namepos = len(self.appdir) + 1
        self.collect_manifest(appsrcdir, namepos, new_filedict)
        self.collect_manifest(appresdir, namepos, new_filedict)
        self.save_manifest(self.bundle_manifest_txt, new_filedict)
        print('bundle done %smin' % round((time.time() - t) / 60, 3))

def main():
    # project = UloProject(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    # project = OldProject('/Users/joli/Work/CS/C/sanguo_dudainew_vn', 16774)
    # project = UloProject('/Users/joli/Work/CS/C/xiuxian_bt2', 20000)
    project = UloProject('/Users/joli/Work/CS/C/sanguonew_bt_vn', 16774)
    # project.bundle()
    project.hotfix()

    # from jonlin.utils import FS
    # FS.explorer(project.builddir)

if __name__ == '__main__':
    main()