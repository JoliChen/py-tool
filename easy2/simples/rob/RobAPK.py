# -*- coding: utf-8 -*-
# @Time    : 2019/8/3 3:08 PM
# @Author  : Joli
# @Email   : 99755349@qq.com
import base64
import json
import os
import shutil
import xml.etree.ElementTree as ET

from PIL import Image
from androguard.core.bytecodes import axml

from com.arts import ImageTailor, assetutil
from jonlin.cl import APKTool, ADB
from jonlin.utils import FS, Text, Crypto, Bit
from simples.rob import RobCom


class DeApkBase:
    def __init__(self, name):
        self.root = '/Users/joli/Desktop/test/rob/apk'
        self.dist = os.path.join(self.root, name + '_dist')
        self.mxml = os.path.join(self.dist, 'AndroidManifest.xml')
        self.name = name
        self.appid = ''

    def decompile(self, unz_opt=False):
        apk = os.path.join(self.root, self.name + '.apk')
        if unz_opt:
            ret = APKTool.unzapk(apk, self.dist)
        else:
            ret = APKTool.dapk(apk, self.dist)
        print('decompile apk done, ret:', ret)
        if 0 != ret:
            return
        self.load_manifest(unz_opt)

    def reinstall(self, unz_opt=False):
        self.load_manifest(unz_opt)
        unsign_apk = os.path.join(self.root, self.name + '_unsign.apk')
        if unz_opt:
            ret = APKTool.zipapk(self.dist, unsign_apk)
        else:
            ret = APKTool.bapk(self.dist, unsign_apk)
        print('recompile apk done, ret:', ret)
        if 0 != ret:
            return
        signed_apk = os.path.join(self.root, self.name + '_signed.apk')
        ret = APKTool.sign(unsign_apk, signed_apk)  # 签名APK
        if 0 != ret:
            return
        os.remove(unsign_apk)
        print('sign apk done, ret:', ret)
        ret = ADB.install(signed_apk, self.appid)  # 安装APK
        if 0 != ret:
            return
        # os.remove(signed_apk)
        print('install apk done, ret:', ret)

    def load_manifest(self, bin_opt=False):
        if bin_opt:
            with open(self.mxml, 'rb') as fp:
                axmlp = axml.AXMLPrinter(fp.read())
            etree = ET.fromstring(axmlp.get_xml())
        else:
            etree = ET.parse(self.mxml).getroot()
        self.appid = etree.get('package')

    def pull_hack_files(self, outdir, files, ftype=None):
        miss = []
        phone_dir = '/data/data/%s/files' % self.appid
        for i in range(len(files)):
            f = '%s/%s' % (outdir, files[i])
            FS.make_parent(f)
            if ADB.pull('%s/hack%d.%s' % (phone_dir, i + 1, ftype if ftype else f[-3:]), f) != 0:
                miss.append(f)
        print('miss', len(miss), miss)

class RobSnsgz(DeApkBase):  # 少年三国志
    def __init__(self):
        DeApkBase.__init__(self, 'snsgz2')
        self.odir = os.path.join(self.root, self.name + '_res')
        self.idir = os.path.join(self.dist, 'assets/res')
        self.flist = os.path.join(self.root, self.name + '_files.txt')

    def extract_files(self):
        files = FS.walk_files(self.idir, ewhites=('.png', '.jpg'), cut=len(self.idir) + 1)
        print(len(files))
        s = ''
        for f in files:
            s += '"' + f + '",\n'
        FS.write_text(self.flist, s)

    def read_files(self):
        files = []
        s = FS.read_text(self.flist)
        for f in s.split('\n'):
            if f:
                files.append(f[1:-2])
        print(len(files))
        return files

    def pull_files(self):
        fs = '/Users/joli/Documents/AndroidStudio/DeviceExplorer/meizu-m3s-Y15QKBPR242LL/data/data/com.youzu.snsgz2.aligames/files'
        files = self.read_files()
        misss = []
        for i in range(len(files)):
            fn = files[i]
            i += 1
            src = os.path.join(fs, 'hack%d%s' % (i, FS.extensions(fn)))
            if os.path.isfile(src):
                dst = os.path.join(self.odir, fn)
                FS.moveto(src, dst)
            else:
                misss.append(i)
        print(misss)
        # self.load_manifest()
        # self.pull_hack_files(self.odir, self.read_files())

    def copy_files(self):
        files = FS.walk_files(self.idir, cut=len(self.idir) + 1)
        for f in files:
            d = os.path.join(self.odir, f)
            if not os.path.isfile(d):
                FS.moveto(os.path.join(self.idir, f), d)

class RobQQSG(DeApkBase):  # 权倾三国
    def __init__(self):
        DeApkBase.__init__(self, 'qqsg')
        self.odir = os.path.join(self.root, self.name + '_res')
        self.idir = os.path.join(self.dist, 'assets')

    def save_files(self):
        files = FS.walk_files(self.idir, ewhites=('.png', '.jpg'), cut=len(self.idir) + 1)
        print(len(files))
        s = ''
        for f in files:
            s += '"' + f + '",\n'
        FS.write_text(os.path.join(self.idir, 'files.txt'), s)

    def read_files(self):
        files = []
        s = FS.read_text(os.path.join(self.idir, 'files.txt'))
        for f in s.split('\n'):
            if f:
                files.append(f[1:-2])
        print(len(files))
        return files

    def pull_files(self):
        self.load_manifest()
        self.pull_hack_files(self.odir, self.read_files())

    def copy_files(self):
        src = os.path.join(self.idir, 'Data')
        dst = os.path.join(self.odir, 'Data')
        files = FS.walk_files(src, cut=len(src) + 1)
        for f in files:
            if f[0] == '.':
                continue
            if FS.extensions(f) == '.bin':
                continue
            d = os.path.join(dst, f)
            if os.path.isfile(d):
                continue
            FS.moveto(os.path.join(src, f), d)

class RobDYQLB(DeApkBase):  # 道友请留步
    def __init__(self):
        DeApkBase.__init__(self, 'dyqlb')
        self.odir = os.path.join(self.root, self.name + '_res')
        self.idir = os.path.join(self.dist, 'assets/ires')

    def find_exts(self):
        def save(ext_map):
            ext_arr = sorted(ext_map.keys(), key=lambda kk: ext_map[kk], reverse=True)
            with open(os.path.join(self.root, self.name + '_ext.txt'), 'w') as fp:
                for k in ext_arr:
                    fp.writelines('%s:%d\n' % (k, ext_map[k]))

        def read():
            ext_map = {}
            with open(os.path.join(self.root, self.name + '_ext.txt'), 'r') as fp:
                for line in fp.readlines():
                    p = line.find(':')
                    ext_map[line[:p]] = int(line[p+1:])
            return ext_map

        def extract():
            ext_map = {}
            for f in os.listdir(self.idir):
                if f.rfind('.') != -1:
                    continue
                with open(os.path.join(self.idir, f), 'rb') as fp:
                    ret = RobCom.find_binary_exts(fp.read())
                if ret:
                    print(f, ret)
                    for k in ret:
                        if k in ext_map:
                            ext_map[k] += ret[k]
                        else:
                            ext_map[k] = ret[k]
                else:
                    print(f, '------------------------------')
            print(ext_map)
            save(ext_map)
        # extract()

        def filtered():
            ext_map = read()
            key_arr = []
            for k in ext_map:
                n = len(k)
                if n == 1:
                    key_arr.append(k)
                    continue
                if n == 2 and k != 'js':
                    key_arr.append(k)
                    continue
                if not Text.islower_str(k) and not Text.isupper_str(k):
                    key_arr.append(k)
                    continue
                if ext_map[k] < 500:
                    key_arr.append(k)
                    continue
            for k in key_arr:
                ext_map.pop(k)
            save(ext_map)
        filtered()

    def save_files(self):
        def extract():
            exts = (b'png', b'plist', b'ccb', b'ccbi', b'js', b'jpg')
            paths = set()
            for f in os.listdir(self.idir):
                if f.rfind('.') != -1:
                    continue
                with open(os.path.join(self.idir, f), 'rb') as fp:
                    ret = RobCom.find_binary_paths(fp.read(), exts)
                    if ret:
                        print(f, ret)
                        for item in ret:
                            paths.add(item[1])
            with open(os.path.join(self.root, self.name + '_files0.txt'), 'w') as fp:
                for k in sorted(paths):
                    fp.writelines('%s\n' % k)
        # extract()

        def filtered():
            paths = {}
            with open(os.path.join(self.root, self.name + '_files0.txt'), 'r') as fp:
                for line in fp.readlines():
                    line = line.strip()
                    while True:
                        m = Crypto.md5_bytes(bytes(Text.str2unicodes(line)))
                        p = os.path.join(self.idir, m)
                        if os.path.isfile(p):
                            paths[m] = line
                            break
                        if len(line) > 0:
                            line = line[1:]
                        else:
                            break
            with open(os.path.join(self.root, self.name + '_files.txt'), 'w') as fp:
                for k in paths:
                    fp.writelines('%s:%s\n' % (k, paths[k]))
        filtered()

    def read_files(self):
        paths = {}
        with open(os.path.join(self.root, self.name + '_files.txt'), 'r') as fp:
            for line in fp.readlines():
                line = line.strip()
                p = line.find(':')
                paths[line[:p]] = line[p+1:]
        return paths

    def repair_resouce(self):
        pass
        # paths = self.read_files()
        # for m in paths:
        #     src = os.path.join(self.idir, m)
        #     dst = os.path.join(self.odir, paths[m])
        #     FS.moveto(src, dst)
        # for fn in FS.walk_files(self.odir, ext_whites=('.png', '.jpg'), cut_pos=len(self.odir)+1):
        #     with open(os.path.join(self.odir, fn), 'rb') as fp:
        #         buffer = fp.read()
        #     if fn.endswith('png'):
        #         buffer = RobCom.PNG_BEG + RobCom.PNG_HDR + buffer[16:]
        #     else:
        #         buffer = RobCom.JPG_BEG + RobCom.JPG_HDR + bytes([buffer[16], buffer[17]]) + buffer[16:]
        #     with open(os.path.join(self.odir, fn), 'wb') as fp:
        #         fp.write(buffer)

        # xml_hdr = len(RobCom.XML_BEG)
        # for fn in FS.walk_files(self.idir, cut_pos=len(self.idir)+1):
        #     src = os.path.join(self.idir, fn)
        #     # if fn.rfind('.') != -1:
        #     #     FS.moveto(src, dst)
        #     #     continue
        #     with open(src, 'rb') as fp:
        #         buffer = fp.read()
        #     size = len(buffer)
        #     if buffer[:xml_hdr] == RobCom.XML_BEG:
        #         FS.moveto(src, os.path.join(self.odir, '2', fn))
        #         continue
        #     if buffer[size-8:size-4] == RobCom.PNG_END:
        #         print('png', fn)
        #         FS.moveto(src, os.path.join(self.odir, '3', fn))
        #         continue
        #     if buffer[size-2:] == RobCom.JPG_END:
        #         print('jpg', fn)
        #         FS.moveto(src, os.path.join(self.odir, '4', fn))
        #         continue

        # for fn in os.listdir(os.path.join(self.odir, '2')):
        #     FS.moveto(os.path.join(self.odir, '2', fn), os.path.join(self.odir, '2', fn + '.plist'))

        # for fn in os.listdir(os.path.join(self.odir, '3')):
        #     with open(os.path.join(self.odir, '3', fn), 'rb') as fp:
        #         buffer = fp.read()
        #     buffer = RobCom.PNG_BEG + RobCom.PNG_HDR + buffer[16:]
        #     with open(os.path.join(self.odir, '3', fn), 'wb') as fp:
        #         fp.write(buffer)
        #     FS.moveto(os.path.join(self.odir, '3', fn), os.path.join(self.odir, '3', fn + '.png'))

        # for fn in os.listdir(os.path.join(self.odir, '4')):
        #     with open(os.path.join(self.odir, '4', fn), 'rb') as fp:
        #         buffer = fp.read()
        #     buffer = RobCom.JPG_BEG + RobCom.JPG_HDR + bytes([buffer[16], buffer[17]]) + buffer[16:]
        #     with open(os.path.join(self.odir, '4', fn), 'wb') as fp:
        #         fp.write(buffer)
        #     FS.moveto(os.path.join(self.odir, '4', fn), os.path.join(self.odir, '4', fn + '.jpg'))

class RobSNXYJ(DeApkBase):  # 少年西游记
    def __init__(self):
        DeApkBase.__init__(self, 'snxyj')
        self.odir = os.path.join(self.root, self.name + '_res')
        self.idir = os.path.join(self.dist, 'assets')
        self.exts = (b'png', b'jpg', b'json', b'ccb', b'plist', b'fnt', b'atlas', b'skel', b'luac')
        # self.xxtea_key = RobCom.XXTEA.fmt_key(b'27efb289-bc7f-3636-ae74-e747b1bea17c')
        self.xxtea_key = b'27efb289-bc7f-3636-ae74-e747b1bea17c'

    def find_exts(self):
        with open(os.path.join(self.idir, 'package.was'), 'rb') as fp:
            ret = RobCom.find_binary_exts(fp.read())
            if ret:
                for k in sorted(ret.keys(), key=lambda x: ret[x]):
                    if len(k) > 2 and ret[k] > 5:
                        print(k, ret[k])

    def find_paths(self):
        # paths = set()
        # with open(os.path.join(self.idir, 'package.was'), 'rb') as fp:
        #     ret = RobCom.find_binary_paths(fp.read(), self.exts)
        #     if ret:
        #         for k in ret:
        #             paths.add(k[1])
        # with open(os.path.join(self.idir, 'patch.was'), 'rb') as fp:
        #     ret = RobCom.find_binary_paths(fp.read(), self.exts)
        #     if ret:
        #         for k in ret:
        #             paths.add(k[1])
        # with open(os.path.join(self.root, 'files.txt'), 'w') as fp:
        #     for k in sorted(paths):
        #         fp.writelines('"%s",\n' % k)

        # with open(os.path.join(self.root, 'files.txt'), 'w') as fp:
        #     resdir = os.path.join(self.odir, 'res')
        #     for fn in FS.walk_files(resdir, ext_whites=('.png', '.jpg'), cut_pos=len(resdir)+1):
        #         fp.writelines('"%s",\n' % fn)
        with open(os.path.join(self.root, 'files.txt'), 'w') as fp:
            resdir = os.path.join(self.odir, 'res')
            for fn in FS.walk_files(resdir, ewhites=('.json', '.plist', '.atlas'), cut=len(resdir) + 1):
                fp.writelines('"%s",\n' % fn)
            srcdir = os.path.join(self.odir, 'src')
            for fn in FS.walk_files(srcdir, ewhites=['.luac'], cut=len(srcdir) + 1):
                fp.writelines('"%s",\n' % fn)

    def split_res(self):
        # with open(os.path.join(self.idir, 'package.was'), 'rb') as fp:
        with open(os.path.join(self.idir, 'patch.was'), 'rb') as fp:
            buffer = fp.read()
            buffer = buffer[32:]
        e = len(buffer)
        p = 0
        while p < e:
            p += 4
            b = buffer[p:p+4]
            fs = Bit.u32_from(b)
            p += 24
            b = buffer[p:p+4]
            ns = Bit.u32_from(b)
            p += 4
            fn = Text.unicodes2str(buffer[p:p+ns])
            p += ns + 1
            if fn.endswith('.luac'):
                fn = 'src/' + fn
            else:
                fn = 'res/' + fn
            print(p, fs, fn)
            fb = buffer[p:p+fs]
            p += fs
            fp = os.path.join(self.odir, fn)
            FS.make_parent(fp)
            with open(fp, 'wb') as fp:
                fp.write(fb)
        print(p, e)
        # '27efb289-bc7f-3636-ae74-e747b1bea17c'
        # b = Bit.u32_bytes(1104)
        # print('%x' % b[0], '%x' % b[1], '%x' % b[2], '%x' % b[3])
        # b = Bit.u32_bytes(660)
        # print('%x' % b[0], '%x' % b[1], '%x' % b[2], '%x' % b[3])

    def pull_res(self):
        self.load_manifest()
        with open(os.path.join(self.root, 'files.txt'), 'r') as fp:
            files = []
            for line in fp.readlines():
                line = line[1:-3]
                # files.append(line)
                if line.endswith('.luac'):
                    files.append('src/' + line)
                else:
                    files.append('res/' + line)
        self.pull_hack_files(os.path.join(self.root, self.name + '_pull1'), files, 'plist')

    def decrypt_res(self):
        import biplist

        def readplist(pf):
            try:
                pli = biplist.readPlist(pf)
                return pli
            except biplist.InvalidPlistException as e:
                print('error', e)

        path = os.path.join(self.root, self.name + '_pull1')
        for fn in FS.walk_files(path, cut=len(path) + 1):
            if fn.endswith('.DS_Store'):
                continue
            print(fn)
            ft = os.path.join(path, fn)
            # fs = FS.read_text(ft)
            # if fs.startswith('<?xml') and fs.find('.dtd"/>') != -1:
            #     fs = fs.replace('.dtd"/>', '.dtd">', 1)
            #     FS.write_text(ft, fs)
            plist = readplist(ft)
            if plist:
                s = plist.get('base64')
            else:
                s = FS.read_text(ft)[:-31]
            try:
                s = base64.b64decode(s)
                FS.write_text(os.path.join(self.root, self.name + '_pull', fn), s.decode('utf-8'))
            except:
                pass

class RobJHYY(DeApkBase):  # 江湖悠悠
    def __init__(self):
        DeApkBase.__init__(self, 'jhyy')
        self.odir = os.path.join(self.root, self.name + '_res')
        self.idir = os.path.join(self.dist, 'assets')

        # from simples.rob.unity import UnityExtract
        # for (root, _, files) in os.walk(self.idir):
        #     for name in files:
        #         UnityExtract.unityfs(os.path.join(root, name), self.odir)

        for (root, _, files) in os.walk(self.odir):
            for name in files:
                tag = os.path.basename(root)
                dst = os.path.join(os.path.dirname(root), tag + "_" + name)
                if os.path.isfile(dst):
                    continue
                src = os.path.join(root, name)
                FS.moveto(src, dst)
        FS.rm_empty_dirs(self.odir)

class RobTMCS(DeApkBase):  # 天命传说
    def __init__(self):
        DeApkBase.__init__(self, 'tmcs')
        self.odir = os.path.join(self.root, self.name + '_res')
        self.idir = os.path.join(self.dist, 'assets')

        # for fn in FS.walk_files(self.idir, ext_whites=['.csprite'], cut_pos=len(self.idir)+1):
        #     with open(os.path.join(self.idir, fn), 'rb') as fp:
        #         tmp = fp.read()
        #         buffer = None
        #         for i in range(len(tmp)-3):
        #             if tmp[i] == ord('P') and tmp[i+1] == ord('K') and tmp[i+2] == ord('M'):
        #                 buffer = tmp[i:]
        #                 break
        #     if buffer is not None:
        #         dst = os.path.join(self.odir, fn[0:-8] + '.pkm')
        #         FS.make_parent(dst)
        #         with open(dst, 'wb') as fp:
        #             fp.write(buffer)

        # pkmdir = '/Users/joli/Desktop/test/rob/apk/tmcs_pkm'
        # for fn in FS.walk_files(pkmdir, ext_whites=['.pkm'], cut_pos=len(pkmdir) + 1):
        #     dst = os.path.join(self.odir, os.path.dirname(fn))
        #     FS.make_parent(dst)
        #     os.system('/Users/joli/source/mac/app/hack/MTCT/bin/etcpack %s %s' % (
        #         os.path.join(pkmdir, fn), dst
        #     ))

        from PIL import Image
        ppmdir = '/Users/joli/Desktop/test/rob/apk/tmcs_ppm'
        for fn in FS.walk_files(ppmdir, ewhites=['.ppm'], cut=len(ppmdir) + 1):
            dst = os.path.join(self.odir, fn[0:-8] + '.png')
            FS.make_parent(dst)
            image = Image.open(os.path.join(ppmdir, fn))
            image.save(dst, format='png')

        # for (root, _, files) in os.walk(self.odir):
        #     for name in files:
        #         tag = os.path.basename(root)
        #         dst = os.path.join(os.path.dirname(root), tag + "_" + name)
        #         if os.path.isfile(dst):
        #             continue
        #         src = os.path.join(root, name)
        #         FS.moveto(src, dst)
        # FS.rm_empty_dirs(self.odir)

class RobBZDX:
    def __init__(self):
        cur = '/Users/joli/Downloads/tianmingchuanshuo1.4.0'
        dst = os.path.join(cur, 'assets-d')
        src = os.path.join(cur, 'assets')
        pos = len(src) + 1
        for (root, _, files) in os.walk(src):
            for fn in files:
                fn = os.path.join(root, fn)
                fd = os.path.join(dst, fn[pos:])
                assetutil.unityfs(fn, fd)
        # self.make_shader()

    def make_shader(self):
        from com.dev import MakeShader
        shader = """
"""
        MakeShader.encode_shader(shader)

class RobKHSG(DeApkBase):  # 开黑三国
    def __init__(self):
        DeApkBase.__init__(self, 'khsg')
        # self.analyse_json(os.path.join(self.root, 'khsg_dist/assets/res/import'))

    def analyse_json(self, json_root):
        print(json_root)
        types_list = set()
        for p in FS.walk_files(json_root, ewhites=['.json']):
            obj = json.loads(FS.read_text(p))
            if not obj:
                continue
            if isinstance(obj, dict):
                t = obj['__type__']
                if t.startswith('cc.'):
                    if t == 'cc.JsonAsset':
                        if not obj['json']['frames']:
                            print(p)
                    types_list.add(t)
                continue
            # print(type(obj))
        print(types_list)

    def decrypt_res(self):
        raw_root = os.path.join(self.root, 'khsg_wf_dist/assets/res/raw-assets')
        for f in FS.walk_files(raw_root, ewhites=['.png']):
            with open(f, 'rb') as fp:
                buffer = self.decrypt_png(fp.read())
            with open(f, 'wb') as fp:
                fp.write(buffer)
        print('finish')

    @staticmethod
    def decrypt_png(buffer):
        if buffer[:5] != b'tkmcg':
            return buffer
        mask = buffer[5]
        buffer = bytearray(buffer[6:])
        for i in range(len(buffer)):
            buffer[i] = buffer[i] ^ mask
        return buffer

class RobZQQST(DeApkBase):  # 最强骑士团
    def __init__(self):
        DeApkBase.__init__(self, 'zqqst')

    def decrypt_res(self):
        raw_root = '/Users/joli/Downloads/zqqst/assets/res/fca'
        # self.convert_pngs(raw_root)
        # self.convert_final(raw_root)
        self.split_by_plist(raw_root)
        print('finish')

    @staticmethod
    def convert_pngs(raw_root):
        pkmtools = assetutil.PkmUtil()
        for f in FS.walk_files(raw_root, ewhites=['.pvr']):
            pkmtools.topng(f, os.path.dirname(f), needflip=False)
        for f in FS.walk_files(raw_root, ewhites=['.pvr@alpha']):
            pkmtools.topng(f, os.path.dirname(f), needflip=False, subfix='_alpha')

    @staticmethod
    def convert_final(raw_root):
        # r = '/Users/joli/Downloads/zqqst/assets/res/fca/effect/eff_buff_newSpider_ult0.png'
        # a = '/Users/joli/Downloads/zqqst/assets/res/fca/effect/eff_buff_newSpider_ult0_alpha.png'
        # f = '/Users/joli/Downloads/zqqst/assets/res/fca/effect/eff_buff_newSpider_ult0_final.png'
        # image = ImageTools.merge_rgb_alpha(r, a)
        # image.save(f, format='png')
        for f in FS.walk_files(raw_root, ewhites=['.pvr']):
            sub = os.path.splitext(f)[0]
            rgb = sub + '.png'
            if not os.path.isfile(rgb):
                continue
            a = sub + '_alpha.png'
            if not os.path.isfile(a):
                continue
            image = assetutil.merge_rgba(rgb, a)
            image.save(sub + '_final.png', format='png')

    @staticmethod
    def split_by_plist(raw_root):
        for f in FS.walk_files(raw_root, ewhites=['.pvr']):
            sub = os.path.splitext(f)[0]
            png = sub + '_final.png'
            if not os.path.isfile(png):
                continue
            plist = sub + '.plist'
            if not os.path.isfile(plist):
                continue
            ImageTailor.tp(plist, png, fixwhite=False)

class RobXAB1(DeApkBase):  # XAB1
    def __init__(self):
        DeApkBase.__init__(self, 'xab1')

    def decrypt_res(self):
        www_dir = '/Users/joli/Downloads/XAB/assets/www'
        data_js = FS.read_text(os.path.join(www_dir, 'data.js'))[1:]
        data_js = json.loads(data_js)
        print(data_js)

class RobJYYZ(DeApkBase):  # 莉莉丝-剑与远征
    def __init__(self):
        DeApkBase.__init__(self, 'jyyz')

    @staticmethod
    def decrypt_res():
        assets_dir = '/Users/joli/Downloads/Hack/jyyz/assets'
        pkmtools = assetutil.PkmUtil()
        for fp in FS.walk_files(assets_dir, ewhites=['.pvr']):
            fd = os.path.dirname(fp)
            rgb_path = pkmtools.topng(fp, fd, needflip=False)
            if not rgb_path:
                continue
            fn = FS.filename(rgb_path)
            a_path = os.path.join(fd, fn + '.pvr@alpha')
            if os.path.isfile(a_path):
                a_path = pkmtools.topng(a_path, fd, needflip=False, subfix='_alpha')
                png_path = os.path.join(fd, fn + '_final.png')
                image = assetutil.merge_rgba(rgb_path, a_path)
                image.save(png_path)
            else:
                png_path = rgb_path
            plist_path = os.path.join(fd, fn + '.plist')
            if os.path.isfile(plist_path):
                ImageTailor.tp(plist_path, png_path, fixwhite=False)

    @staticmethod
    def extract_files():
        assets_dir = '/Users/joli/Downloads/Hack/jyyz/assets'
        config_map = {}
        for fn in FS.walk_files(assets_dir, ewhites=['.jsonc'], cut=len(assets_dir)+1):
            config_map[FS.filename(fn)] = 1
        for fn in sorted(config_map.keys()):
            print('"' + fn + '",')

class RobMJFY(DeApkBase):  # 萌将风云
    def __init__(self):
        DeApkBase.__init__(self, 'mjfy')

    def decrypt_res(self):
        assets_dir = '/Users/joli/Downloads/Hack/com'
        for name in os.listdir(assets_dir):
            self.decrypt_pkm(os.path.join(assets_dir, name))

    @staticmethod
    def decrypt_pkm(pkm_dir):
        pkmtools = assetutil.PkmUtil()
        for name in os.listdir(pkm_dir):
            if not name.endswith('.pkm'):
                continue
            pkmtools.topng(os.path.join(pkm_dir, name), pkm_dir, needflip=False)
            name = FS.filename(name)  # 去掉后缀
            png_img = os.path.join(pkm_dir, name + '_image.png')
            png_rgb = os.path.join(pkm_dir, name + '.png')
            if os.path.isfile(png_rgb):
                png_a = os.path.join(pkm_dir, name + '_a.png')
                if os.path.isfile(png_a):
                    image = assetutil.merge_rgba(png_rgb, png_a)
                    image.save(png_img, format='png')
                else:
                    shutil.copyfile(png_rgb, png_img)
            plist = os.path.join(pkm_dir, name + '.plist')
            if os.path.isfile(png_img) and os.path.isfile(plist):
                ImageTailor.tp(plist, png_img, fixwhite=True)
            break

class RobSGZHXDL(DeApkBase):  # 三国志幻想大陆
    def __init__(self):
        DeApkBase.__init__(self, 'sgzhxdl')

    def decrypt_res(self):
        hash_dir = '/Users/joli/Downloads/sanguozhihuanxiangdalu_yxdown.com/assets/hash'
        # self.check_json_files(hash_dir)
        # self.check_paths(hash_dir)
        # self.check_files(hash_dir)
        # self.format_files('/Users/joli/Downloads/sanguozhihuanxiangdalu_yxdown.com/assets/hash2')
        self.export_pkm('/Users/joli/Downloads/sanguozhihuanxiangdalu_yxdown.com/assets/hash2')

    @staticmethod
    def export_pkm(root_dir):
        pkmtools = assetutil.PkmUtil()
        for fn in os.listdir(root_dir):
            if fn.endswith('.pkm') or fn.endswith('.pkm20'):
                pkmtools.topng(os.path.join(root_dir, fn), root_dir, needflip=False)

    @staticmethod
    def format_files(root_dir):
        import demjson
        luaq = bytes([0x1B, 0x4C, 0x75, 0x61, 0x51])
        csbv = bytes([0x32, 0x2E, 0x31, 0x2E, 0x30, 0x2E, 0x30])
        skelv = bytes([0x33, 0x2E, 0x36, 0x2E, 0x35, 0x32])
        plist = b'<?xml'
        plist_bom = bytes([0xEF, 0xBB, 0xBF]) + plist
        fnt = bytes([0x69, 0x6E, 0x66, 0x6F, 0x20])
        pkm10 = bytes([0x50, 0x4B, 0x4D, 0x20, 0x31, 0x30])
        pkm20 = bytes([0x50, 0x4B, 0x4D, 0x20, 0x32, 0x30])
        oo2 = bytes([0x0, 0x0, 0x2])
        files = os.listdir(root_dir)
        for fn in files:
            if '.' in fn:
                continue
            fn = os.path.join(root_dir, fn)
            with open(fn, 'rb') as fs:
                head = fs.read(8)
                fs.seek(0)
                if head[:2] == RobCom.JPG_BEG:
                    p = fs.tell()
                    fs.seek(os.stat(fn).st_size-2)
                    b = fs.read(2)
                    if b == RobCom.JPG_END:
                        os.rename(fn, os.path.join(root_dir, fn + '.jpg'))
                        fs.seek(p)
                        continue
                    fs.seek(p)
                elif head == RobCom.PNG_BEG:
                    os.rename(fn, os.path.join(root_dir, fn + '.png'))
                    continue
                elif head[:5] == luaq:
                    os.rename(fn, os.path.join(root_dir, fn + '.luac'))
                    continue
                elif head[:5] == plist or head == plist_bom:
                    os.rename(fn, os.path.join(root_dir, fn + '.plist'))
                    continue
                elif head[:5] == fnt:
                    os.rename(fn, os.path.join(root_dir, fn + '.fnt'))
                    continue
                elif head[:6] == pkm10:
                    os.rename(fn, os.path.join(root_dir, fn + '.pkm'))
                    continue
                elif head[:6] == pkm20:
                    os.rename(fn, os.path.join(root_dir, fn + '.pkm20'))
                    continue
                elif head[:3] == oo2:
                    os.rename(fn, os.path.join(root_dir, fn + '.oo2'))
                    continue
                elif head[0] == 0x0A:
                    os.rename(fn, os.path.join(root_dir, fn + '.script'))
                    continue
                elif head[0] == 0x14:
                    p = fs.tell()
                    fs.seek(52)
                    b = fs.read(7)
                    if b == csbv:
                        os.rename(fn, os.path.join(root_dir, fn + '.csb'))
                        fs.seek(p)
                        continue
                    fs.seek(p)
                elif head[0] == 0x1C:
                    p = fs.tell()
                    fs.seek(29)
                    b = fs.read(6)
                    if b == skelv:
                        os.rename(fn, os.path.join(root_dir, fn + '.skel'))
                        fs.seek(p)
                        continue
                    fs.seek(p)
                elif head[:1] == b'\n':
                    line = fs.readlines(2)
                    if line[0] == b'\n':
                        if len(line) > 1 and line[1].endswith(b'.png\n'):
                            os.rename(fn, os.path.join(root_dir, fn + '.atlas'))
                            continue
                elif head[:1] == b'{' or head[:1] == b'[':
                    try:
                        demjson.decode_file(fn)
                        os.rename(fn, os.path.join(root_dir, fn + '.json'))
                        continue
                    except:
                        pass
                print('unknow', fn)
        print('done')

    @staticmethod
    def check_files(root_dir):
        path = os.path.join(root_dir, '2/8/691b7f51a2a042ae60bbc467eedf8882')
        text = FS.read_text(path)
        confs = text.split('@')
        confs.pop(0)
        # print('\n'.join(confs))
        print(len(confs))

        # files = FS.walk_files(root_dir, cut=len(root_dir)+1)
        # print(len(files))
        # for fn in confs:
        #     if fn not in files:
        #         print("not in files", fn)
        # for fn in files:
        #     if fn not in confs:
        #         print("not in confs", fn)

        hash2_dir = os.path.join(os.path.dirname(root_dir), "hash2")
        if os.path.isdir(hash2_dir):
            shutil.rmtree(hash2_dir)
        os.makedirs(hash2_dir)
        for i in range(len(confs)):
            shutil.copyfile(os.path.join(root_dir, confs[i]), os.path.join(hash2_dir, str(i+1)))
        print('done')

    @staticmethod
    def check_paths(root_dir):
        # exts = (b'png', b'jpg', b'json', b'ccb', b'plist', b'fnt', b'atlas', b'skel', b'luac')
        exts = (b'jpg', b'json', b'ccb', b'plist', b'fnt', b'atlas', b'skel', b'luac')
        conf_list = []

        for (par, _, files) in os.walk(root_dir):
            for fn in files:
                path = os.path.join(par, fn)
                with open(path, 'rb') as fs:
                    array = RobCom.find_binary_paths(fs.read(), exts)
                    if array:
                        print(path)
                        conf_list.append({'path': path, 'list': array})
        print('-----------------------------------------------')
        conf_list.sort(key=lambda x: len(x['list']), reverse=True)
        log_file = os.path.join(os.path.dirname(root_dir), "config.log")
        if os.path.isfile(log_file):
            os.remove(log_file)
        with open(log_file, 'a') as fs:
            for i in range(len(conf_list)):
                item = conf_list[i]
                print(i, item['path'], item['list'], file=fs)
        print('done')

    @staticmethod
    def check_json_files(root_dir):
        import demjson
        json_list = []
        for (par, _, files) in os.walk(root_dir):
            for fn in files:
                path = os.path.join(par, fn)
                # print(path)
                try:
                    demjson.decode_file(path)
                    json_list.append({'path': path, 'stat': os.stat(path)})
                except:
                    pass
        print('-----------------------------------------------')
        json_list.sort(key=lambda x: x['stat'].st_size, reverse=True)
        for i in range(len(json_list)):
            item = json_list[i]
            print(i, item['path'], item['stat'].st_size)
        print('done')

class RobQQC(DeApkBase):  # 千秋辞
    def __init__(self):
        DeApkBase.__init__(self, 'qqc')

    @staticmethod
    def decrypt_res():
        # root = '/Users/joli/Downloads/Unity/hack/apk/qqc'
        # root = '/Users/joli/Downloads/Unity/hack/apk/xyjzjzy'
        # assetutil.sh_unityfs(os.path.join(root, 'assets'), os.path.join(root, 'output'), os.path.join(root, 'temp'))
        root = '/Users/joli/Desktop/xyjzjzy/textures$ui_android$chance'
        rgbpath = os.path.join(root, 'UI_chance.png')
        alphapath = os.path.join(root, 'UI_chance_alpha_1.png')
        image = assetutil.merge_rgba(rgbpath, alphapath, alphaindex=0)
        image.save(os.path.join(root, 'test.png'))

        # r = Image.open(alphapath).split()[0]
        # r.save(os.path.join(root, 'UI_chance_alpha_1.png'))