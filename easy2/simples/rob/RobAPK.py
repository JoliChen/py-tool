# -*- coding: utf-8 -*-
# @Time    : 2019/8/3 3:08 PM
# @Author  : Joli
# @Email   : 99755349@qq.com
import base64
import json
import os
import xml.etree.ElementTree as ET
from androguard.core.bytecodes import axml

from jonlin.cl import APKTool, ADB
from jonlin.utils import FS, Text, Crypto, Bit
from simples.rob import RobCom
from simples.rob.unity import UnityExtract
from simples.rob.unity import PKMTools


class DeApkBase:
    def __init__(self, name):
        self.root = '/Users/joli/Desktop/test/rob/apk'
        self.dist = os.path.join(self.root, name + '_dist')
        self.mxml = os.path.join(self.dist, 'AndroidManifest.xml')
        self.name = name
        self.appid = ''

    def decompile(self, zipopt=False):
        apk = os.path.join(self.root, self.name + '.apk')
        if zipopt:
            ret = APKTool.unzapk(apk, self.dist)
        else:
            ret = APKTool.dapk(apk, self.dist)
        print('decompile apk done, ret:', ret)
        if 0 != ret:
            return
        self.load_manifest(zipopt)

    def reinstall(self, zipopt=False):
        self.load_manifest(zipopt)
        unsign_apk = os.path.join(self.root, self.name + '_unsign.apk')
        if zipopt:
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

    def load_manifest(self, isbinary=False):
        if isbinary:
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
        from simples.rob.unity import UnityExtract
        cur = '/Users/joli/Downloads/tianmingchuanshuo1.4.0'
        dst = os.path.join(cur, 'assets-d')
        src = os.path.join(cur, 'assets')
        pos = len(src) + 1
        for (root, _, files) in os.walk(src):
            for fn in files:
                fn = os.path.join(root, fn)
                fd = os.path.join(dst, fn[pos:])
                UnityExtract.unityfs(fn, fd)
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
        # for f in FS.walk_files(raw_root, ewhites=['.pvr', '.pvr@alpha']):
        #     with open(f, 'rb') as fp:
        #         pkm = fp.read()
        #     png = PKMTools.pkm2png(gen=10, data=pkm)
        #     with open('/Users/joli/Downloads/zqqst/assets/res/fca/1.png', 'wb') as fp:
        #         fp.write(png)
        #     break
        f = '/Users/joli/Downloads/zqqst/assets/res/fca/hero/Bard0.pvr'




        # with open(f, 'rb') as fp:
        #     pkm = fp.read()
        #     # pkm = pkm[4:]
        # png = PKMTools.pkm2png(gen=5, data=pkm)
        # with open('/Users/joli/Downloads/zqqst/assets/res/fca/1.png', 'wb') as fp:
        #     fp.write(png)
        # print('finish')

    @staticmethod
    def decrypt_png(buffer):
        if buffer[:5] != b'tkmcg':
            return buffer
        mask = buffer[5]
        buffer = bytearray(buffer[6:])
        for i in range(len(buffer)):
            buffer[i] = buffer[i] ^ mask
        return buffer