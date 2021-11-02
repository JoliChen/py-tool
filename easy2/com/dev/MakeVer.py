# -*- coding: utf-8 -*-
# @Time    : 2020/9/14 6:45 PM
# @Author  : Joli
# @Email   : 99755349@qq.com
import hashlib
import json
import os
import platform
import re
import shutil
import math
import time
import zipfile
import xxtea

class Log:
    @staticmethod
    def i(*args):
        print(*args)

    @staticmethod
    def e(*args):
        print(*args)

class FileKit:
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
        FileKit.make_parentdir(dst)
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

class BinKit:
    @staticmethod
    def bytes2xor(buf, key):  # 异或处理二进制数据
        klen = len(key)
        ibuf = [(buf[i] ^ key[i % klen]) for i in range(len(buf))]
        return bytes(ibuf)

    @staticmethod
    def bytes2hex(buf):
        array = []
        for i in range(len(buf)):
            array.append('0x%x' % buf[i])
        return array

    @staticmethod
    def xorhex(src, key):
        dst = BinKit.bytes2hex(BinKit.bytes2xor(src, key))
        print('xorhex src:%s len:%d' % (src, len(dst)))
        return ','.join(dst)

    @staticmethod
    def hash_bkdr(chars, seed=131):  # BKDRHash [31 131 1313 13131 131313]
        h = 0
        for c in chars:
            h = h * seed + ord(c)
        return h & 0xFFFFFFFF

    @staticmethod
    def hash_bkdr2(chars, seed=131):
        h = 0
        for c in chars:
            h = (h * seed + ord(c)) & 0xFFFFFFFF
        return h

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

class BVM:  # Bundle Version Manager
    TEA_KEY = b'$yz#z0X78'  # xxtea秘钥
    TEA_SIG = b'0x0305~yz'  # xxtea签名

    kHOTFIX, kBUNDLE = 'hotfix', 'bundle'  # 热更模式、整包模式
    kMinor = 'minor'  # 资源版本字段
    RE_NOTE_NAME = re.compile(r'^(hotfix|bundle)_\d+_\d+.json$')  # 日志名称表达式
    RE_ILLEGAL_PATH = re.compile(r'[^a-z0-9_/.]', re.I)  # 非法路径字符验证

    LUA_DIR = 'src/'
    RES_DIR = 'res/'
    INCLUDE_DIRS = (LUA_DIR, RES_DIR)  # 打包资源和脚本
    # INCLUDE_DIRS = (RES_DIR,)  # 只打包资源
    # INCLUDE_DIRS = (LUA_DIR,)  # 只打包脚本
    IGNORE_STARTS = (
        'src/mobdebug.lua',
        'src/luadebug',
        'src/test',
        'src/ucool'
    )
    IGNORES_ENDS = ('.DS_Store', )
    SCRIPT_PKG_RULE = {
        'script': (
            'src/main.lua',
            'src/config.lua',
            'src/boot/',
        ),
        'engine': (
            'src/LuaExtend.lua',
            'src/cocos/',
            'src/packages/'
        ),
        'modules': (
            'src/LangUtils.lua',
            'src/app/',
            'src/lang/'
        ),
        'csb': ('src/csb/', ),
    }
    SCRIPT_PKG_SUFFIX = '.pak'
    ENCRYPT_FILETYPES = ('.plist', '.ulo')

    def __init__(self, bvmdir):
        self.bvmdir = os.path.abspath(bvmdir)
        self.notedir = os.path.join(self.bvmdir, 'notes')  # 日志目录
        self._tea = self.TEA_KEY + bytes(16 - len(self.TEA_KEY))  # need a 16-byte key.

    @staticmethod
    def name_note(mode, version):
        return '%s_%d_%d.json' % (mode, version[0], version[1])

    def save_note(self, note):
        Log.i('保存打包日志 BEGIN')
        version = note['version']
        notepath = os.path.join(self.notedir, self.name_note(note['mode'], version))
        FileKit.make_parentdir(notepath)
        with open(notepath, 'w') as fp:
            json.dump(note, fp, indent='\t')
        Log.i('保存打包日志 END')

    def load_note(self, mode, version):
        return self.load_note_by_name(self.name_note(mode, version))

    def load_note_by_name(self, name):
        notepath = os.path.join(self.notedir, name)
        if os.path.isfile(notepath):
            with open(notepath, 'rb') as fp:
                return json.load(fp)

    def load_prenote(self, mode, version):
        notedict = {}
        if os.path.isdir(self.notedir):
            curname = self.name_note(mode, version)
            for fn in os.listdir(self.notedir):
                if curname == fn:
                    raise Exception('current version existed %s' % fn)
                if self.RE_NOTE_NAME.search(fn):
                    notedict[fn] = int(fn[fn.rfind('_')+1: fn.rfind('.')])  # get minor number
        notelist = sorted(notedict.keys(), key=lambda k: notedict[k], reverse=True)
        curminor = version[1]
        if mode == self.kBUNDLE:
            for fn in notelist:
                if notedict[fn] < curminor:  # 最近版本
                    return self.load_note_by_name(fn)
        elif mode == self.kHOTFIX:
            for fn in notelist:
                if notedict[fn] < curminor and fn.startswith(mode):  # 最近热更版本
                    return self.load_note_by_name(fn)
            for fn in notelist:
                if notedict[fn] <= curminor:  # 最近整包版本
                    return self.load_note_by_name(fn)
            raise Exception('no hotfix base note:%s' % self.name_note(mode, version))
        return {'version': (0, 0), 'files': {}}

    def _gen_curnote(self, projdir, version, mode):
        prefiles = self._prenote['files']
        curfiles = {}
        id_slice = len(projdir) + 1
        for dn in self.INCLUDE_DIRS:
            folder = os.path.join(projdir, dn)
            self._put_files(folder, curfiles, prefiles, id_slice)
        curnote = {
            'preversion': self._prenote['version'],
            'version': version,
            'mode': mode,
            'count': len(curfiles),
            'files': curfiles
        }
        return curnote

    def _put_files(self, folder, curfiles, prefiles, idslice):
        for sudir, _, files in os.walk(folder):
            for fn in files:
                fp = os.path.join(sudir, fn)
                fid = FileKit.normposix(fp[idslice:])
                if self._check_fileid(fid):
                    curfiles[fid] = self._fast_gen_fileinfo(fp, prefiles.get(fid))

    def _check_fileid(self, fid):
        assert not self.RE_ILLEGAL_PATH.search(fid), 'illegal identifier=' + fid
        for pattern in self.IGNORE_STARTS:
            if fid.startswith(pattern):
                return False
        for pattern in self.IGNORES_ENDS:
            if fid.endswith(pattern):
                return False
        return True

    def _fast_gen_fileinfo(self, filepath, preinfo):
        mt = self._gen_filemeta(filepath)
        if not preinfo or mt['size'] != preinfo['size']:
            curinfo = self._gen_fileinfo(filepath, self._curminor, mt)
        else:
            sign = FileKit.get_filemd5(filepath)
            if sign == preinfo['sign']:
                curinfo = self._compatible_fileinfo(preinfo)
            else:
                curinfo = self._gen_fileinfo(filepath, self._curminor, mt, sign)
        return curinfo

    def _gen_fileinfo(self, filepath, minor, meta=None, sign=None):
        Log.i("put file:", filepath)
        sign = sign or FileKit.get_filemd5(filepath)
        info = meta or self._gen_filemeta(filepath)
        info['sign'] = sign
        info['hash'] = BinKit.hash_bkdr2(sign)
        info[self.kMinor] = minor
        # info['package'] = 'xxx.pak'
        # info['encrypt'] = {encrypt file info}
        # info['sub'] = 0 or 1
        return info

    def _compatible_fileinfo(self, info):
        if 'hash' not in info:
            info['hash'] = BinKit.hash_bkdr2(info['sign'])
        if 'encrypt' in info:
            info['encrypt'] = self._compatible_fileinfo(info['encrypt'])
        return info

    @staticmethod
    def _gen_filemeta(filepath):
        meta = os.stat(filepath)
        # return {'size': meta.st_size, 'mtime': math.floor(meta.st_mtime * 1000)}
        return {'size': meta.st_size}

    def _check_dirtyfiles(self):
        hashmap = {}
        if self.kHOTFIX == self._curnote['mode']:
            prefiles = self._prenote['files']
            for fid, curinfo in self._curnote['files'].items():
                preinfo = prefiles.get(fid)
                if not preinfo or preinfo['sign'] != curinfo['sign']:
                    hashmap[fid] = True
        else:
            hashmap = self._curnote['files']
        return hashmap

    def _built_files(self, outdir, tmpdir):
        dirtymap = self._check_dirtyfiles()
        if not dirtymap:
            return
        if os.path.isdir(outdir):
            shutil.rmtree(outdir)  # clear and remove
        if os.path.isdir(tmpdir):
            shutil.rmtree(tmpdir)  # clear and remove
        usefiles, luafiles = [], []
        for fid in self._curnote['files']:
            if fid.startswith(self.RES_DIR):
                if (fid in dirtymap) and self._gen_resfile(fid, outdir):
                    usefiles.append(fid)
            elif fid.startswith(self.LUA_DIR):
                luafiles.append(fid)
            else:
                raise Exception('unexpected built file', fid)
        if luafiles:
            for fid in self._gen_scripts(luafiles, dirtymap, outdir, tmpdir):
                usefiles.append(fid)
        return usefiles

    def _need_encrypt(self, fid):
        for ext in self.ENCRYPT_FILETYPES:
            if fid.endswith(ext):
                return True
        return False

    def _gen_resfile(self, fid, outdir):
        Log.i('gen res', fid)
        fsrc = os.path.join(self._projdir, fid)
        fdst = os.path.join(outdir, fid)
        if self._need_encrypt(fid):
            self._encrypt_file(fsrc, fdst)
            curinfo = self._curnote['files'][fid]  # type: dict
            curinfo['encrypt'] = self._gen_fileinfo(fdst, curinfo[self.kMinor])  # 记录plist加密
        else:
            FileKit.safe_copyfile(fsrc, fdst)
        return True

    def _encrypt_file(self, src, dst):
        with open(src, 'rb') as sfp:
            data = sfp.read()
        n = len(data)
        data += bytes((4 - n % 4) & 3) + bytes([n & 0xFF, n >> 8 & 0xFF, n >> 16 & 0xFF, n >> 24 & 0xFF])
        data = xxtea.encrypt(data, self._tea, padding=False)
        data = self.TEA_SIG + data
        FileKit.make_parentdir(dst)
        with open(dst, 'wb') as dfp:
            dfp.write(data)

    def _gen_scripts(self, luafiles, dirtymap, outdir, tmpdir):
        packages = []
        curfiles = self._curnote['files']
        pkgroot = os.path.join(tmpdir, 'scripts')
        for pkg, fset in self._fill_scripts_packages(luafiles).items():
            if not fset:
                continue
            pkgname = FileKit.normposix(self.LUA_DIR + pkg + self.SCRIPT_PKG_SUFFIX)
            if self._is_dirty_scirpts_package(fset, dirtymap):
                pkgdir = os.path.join(pkgroot, pkg)
                for fid in fset:
                    fsrc = os.path.join(self._projdir, fid)
                    fdst = os.path.join(pkgdir, fid)
                    FileKit.safe_copyfile(fsrc, fdst)
                    curfiles[fid]['package'] = pkg  # 记录脚本所在包
                archive = shutil.make_archive(pkgdir, 'zip', os.path.join(pkgdir, self.LUA_DIR))
                pkgpath = os.path.join(outdir, os.path.normpath(pkgname))
                Log.i('zip lua', pkgpath)
                FileKit.make_parentdir(pkgpath)
                self._encrypt_file(archive, pkgpath)
                curinfo = self._gen_fileinfo(pkgpath, self._curminor)  # 记录脚本加密包信息
            else:
                curinfo = self._compatible_fileinfo(self._prenote['files'][pkgname])  # 从前一次打包日志里取包信息
            if curinfo:
                curfiles[pkgname] = curinfo
                packages.append(pkgname)
        return packages

    def _fill_scripts_packages(self, allscripts):
        pkgmap = dict()
        for pkg, rule in self.SCRIPT_PKG_RULE.items():
            fset = set()
            pkgmap[pkg] = fset
            for fid in allscripts:
                for head in rule:
                    if fid.startswith(head):
                        fset.add(fid)
                        break
        return pkgmap

    @staticmethod
    def _is_dirty_scirpts_package(fset, dirtymap):
        for fid in fset:
            if fid in dirtymap:
                return True

    def _gen_manifest(self, outdir):
        Log.i('保存文件清单 BEGIN')
        rows, rfmt = [], '["%s"]={v=%d,h=%d,size=%d},'
        for fid, curinfo in self._curnote['files'].items():
            if 'encrypt' in curinfo:
                curinfo = curinfo['encrypt']  # 使用加密文件信息
            if 'package' in curinfo:
                continue  # 被打包的文件直接用包信息
            rows.append(rfmt % (fid, curinfo[self.kMinor], curinfo['hash'], curinfo['size']))
        if rows:
            rows[-1] = rows[-1][:-1]
            fstr = '\n'.join(rows)
        else:
            fstr = ''
        vstr = '{%d,%d}' % tuple(self._curnote['version'])
        text = 'return {\nversion=%s,\nfiles={\n%s\n}}' % (vstr, fstr)
        dist = os.path.join(outdir, 'flist')
        FileKit.make_parentdir(dist)
        if self._curnote['mode'] != self.kBUNDLE:
            with zipfile.ZipFile(dist, 'w', zipfile.ZIP_DEFLATED) as fp:
                fp.writestr('newflist', text)
        else:
            with open(dist, 'w') as fp:
                fp.write(text)
        Log.i('保存文件清单 END')

    def _gen_subfiles(self, subfiles, outdir, subdir):
        pass  # 分包资源处理

    @staticmethod
    def _log_filesize(tardir):
        size = 0
        for root, _, files in os.walk(tardir):
            for fn in files:
                meta = os.stat(os.path.join(root, fn))
                size += meta.st_size
        print('本次热更新%f(MB)' % (size / 1024 / 1024))

    def produce(self, projdir, version, mode, subfiles=None):
        self._projdir = projdir
        self._curminor = version[1]  # 0-major 1-minor
        self._prenote = self.load_prenote(mode, version)
        self._curnote = self._gen_curnote(projdir, version, mode)
        outdir = os.path.join(self.bvmdir, 'output')
        tardir = os.path.join(outdir, mode, '%d_%d' % version)
        subdir = os.path.join(outdir, 'sub')
        tmpdir = os.path.join(self.bvmdir, 'tmp')
        usefiles = self._built_files(tardir, tmpdir)
        assert usefiles, 'no file modified'
        if mode != self.kHOTFIX:
            if subfiles:
                self._gen_subfiles(subfiles, tardir, subdir)
        else:
            self._log_filesize(tardir)
        self._gen_manifest(tardir)
        # 自动上传ftp（未实现）
        self.save_note(self._curnote)

class CocosProject:
    def __init__(self, projdir):
        self.projdir  = projdir
        self.shelldir = os.path.join(projdir, 'make')
        self.toolsdir = os.path.join(projdir, 'tools')
        self.builddir = os.path.join(projdir, 'build')
        self.ccsrtdir = os.path.join(projdir, 'dazhanguo')  # cocos runtime dir
        self.ccsuidir = os.path.join(projdir, 'CocosProject')
        if 'Windows' in platform.system():
            self.exec_makeccsui = os.path.join(self.toolsdir, 'CLMakeCSUI.exe')
            self.exec_makesheet = os.path.join(self.toolsdir, 'MakeSheet.exe')
        else:
            self.exec_makeccsui = os.path.join(self.toolsdir, 'CLMakeCSUI')
            self.exec_makesheet = os.path.join(self.toolsdir, 'CLMakeSheet')
        self.svnclient = SvnClient()
        # Log.i('projdir', self.projdir)
        # Log.i('shelldir', self.shelldir)
        # Log.i('toolsdir', self.toolsdir)
        # Log.i('builddir', self.builddir)
        # Log.i('ccsrtdir', self.ccsrtdir)
        # Log.i('ccsuidir', self.ccsuidir)

    def _sh_server_sheet(self, srcdir, dstdir):
        jar = os.path.join(self.toolsdir, "ExcelTool.jar")
        if not os.path.isfile(jar):
            Log.e('can not found', jar)
            return
        cmd = 'java -jar %s -t -d %s -o %s' % (jar, srcdir, dstdir)
        Log.i('build_server_sheet', cmd)
        ret = os.system(cmd)
        Log.i('build_server_sheet done with code', ret)
        return ret == 0

    def _sh_client_sheet(self, srcdir, dstdir):
        if not os.path.isfile(self.exec_makesheet):
            Log.e('can not found', self.exec_makesheet)
            return
        errlog = os.path.join(self.builddir, 'make_client_sheet.log')
        cmd = '%s -i %s -o %s -f binary -e %s' % (self.exec_makesheet, srcdir, dstdir, errlog)
        Log.i('build_client_sheet', cmd)
        ret = os.system(cmd)
        Log.i('build_client_sheet done with code', ret)
        return ret == 0

    def _sh_ccsui_data(self, srcdir, dstdir):
        if not os.path.isfile(self.exec_makeccsui):
            Log.e('can not found', self.exec_makeccsui)
            return
        cmd = '%s --src %s --dst %s' % (self.exec_makeccsui, srcdir, dstdir)
        Log.i('build_ccsui_data', cmd)
        ret = os.system(cmd)
        Log.i('build_ccsui_data done with code', ret)
        return ret == 0

    @staticmethod
    def _sh_ccsui_atlas(srcdir, dstdir):
        src_slice_at = len(srcdir) + 1
        for root, _, files in os.walk(srcdir):
            parentdir = root[src_slice_at:]
            if parentdir.startswith('.'):
                continue
            parentdir = os.path.join(dstdir, parentdir)
            if not os.path.isdir(parentdir):
                os.makedirs(parentdir)
            for fn in files:
                if fn.startswith('.'):
                    continue
                src = os.path.join(root, fn)
                dst = os.path.join(parentdir, fn)
                if os.path.isfile(dst) and not FileKit.is_meta_modified(src, dst):
                    continue
                Log.i('copy', dst)
                shutil.copy2(src, dst)  # copy file and stat

    @staticmethod
    def encrypt_hex(chars, key=BVM.TEA_KEY):
        array = []
        ksize = len(key)
        for i in range(len(chars)):
            b = chars[i] ^ key[i % ksize]
            array.append('0x%x' % b)
        return array

    @staticmethod
    def encrypt_shader(shader):
        shader_size = len(shader)
        shader_hash = BinKit.hash_bkdr(shader)
        print(shader_size, shader_hash)
        print('-------------------------------------------')
        print(shader)
        print('-------------------------------------------')

        key = b'shader'
        klen = len(key)
        hexes, array = '', []
        for i in range(shader_size):
            s = '0x%x' % (ord(shader[i]) ^ key[i % klen])
            array.append(s)
            hexes += s + ','
            if (i + 1) % 16 == 0:
                hexes += '\n'
        output_size = len(array)
        heads = '%s,%s,%s,\n' % (
            ','.join(BinKit.bytes2hex(key)),
            ','.join(BinKit.bytes2hex(bytes([shader_hash       & 0xFF,
                                             shader_hash >> 8  & 0xFF,
                                             shader_hash >> 16 & 0xFF,
                                             shader_hash >> 24 & 0xFF]))),
            ','.join(BinKit.bytes2hex(bytes([output_size       & 0xFF,
                                             output_size >> 8  & 0xFF,
                                             output_size >> 16 & 0xFF,
                                             output_size >> 24 & 0xFF])))
        )
        hexes = heads + hexes[0:-1]
        output_size += 14  # magic + hash + size
        print(('[%d]={\n' % output_size) + hexes + '\n};')
        print('-------------------------------------------')
        shader = ''
        for c in array:
            shader += chr(int(c, 16))
        print(shader)
        print('-------------------------------------------')

class CocosBuilder(CocosProject):
    def __init__(self, projdir):
        CocosProject.__init__(self, projdir)

    def make_server_sheet(self, dstdir):
        srcdir = os.path.join(self.projdir, 'docs', 'config')
        if os.path.isdir(srcdir):
            return self._sh_server_sheet(srcdir, dstdir)
        Log.e('can not found', srcdir)

    def make_client_sheet(self):
        srcdir = os.path.join(self.projdir, 'docs', 'config')
        if os.path.isdir(srcdir):
            dstdir = os.path.join(self.ccsrtdir, 'res', 'config')
            return self._sh_client_sheet(srcdir, dstdir)
        Log.e('can not found', srcdir)

    def make_ccsui(self):
        pass

    # @param major  程序版本
    # @param minor  资源版本
    # @param mode   [hotfix, bundle]
    def build(self, major, minor=0, mode=BVM.kHOTFIX):
        t = time.time()
        if 0 == minor:
            minor = self.svnclient.get_revision(self.ccsrtdir)
        version = (major, minor)
        bvm = BVM(os.path.join(self.builddir, 'bvm'))
        bvm.produce(self.ccsrtdir, version, mode)
        print('done %smin' % round((time.time()-t) / 60, 3))

def unicode2hex(unicode):
    unicode = re.sub("^U\+0*", '', unicode)
    return '0x' + unicode

def main():
    # builder = CocosBuilder(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    # builder = CocosBuilder('/Users/joli/Work/CS/C/scjz')
    # builder = CocosBuilder('/Users/joli/Work/CS/C/scjz_bt')
    # builder = CocosBuilder('/Users/joli/Work/CS/C/xiyou')
    # builder = CocosBuilder('/Users/joli/Work/CS/C/xiuxian_new_develop')
    builder = CocosBuilder('/Users/joli/Work/CS/C/xiuxian_new_release')
    # builder = CocosBuilder('/Users/joli/Work/CS/C/hotfix_tmp')
    builder.build(16774, mode=BVM.kHOTFIX)

    from jonlin.utils import FS
    FS.explorer(builder.builddir)

if __name__ == '__main__':
    main()