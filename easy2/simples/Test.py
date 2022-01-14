# -*- coding: utf-8 -*-
# @Time    : 2021/6/26 6:17 PM
# @Author  : Joli
# @Email   : 99755349@qq.com
import json
import os
import re
import shutil
from xml.dom import minidom

from com.arts import ImageTailor
from jonlin.utils import Crypto, Bit, FS


def test_crypto():
    key = b'l0u1a@5n#d$o%u&9'
    # key = b'$yz#z0X78'

    ret = Crypto.xor_bytes(b'myfile', key)
    print('{%s}' % ','.join(Bit.bytes2hex(ret)))
    print('-------------------------', len(ret))

    ret = Crypto.xor_bytes(b'src/script.pak', key)
    print('{%s}' % ','.join(Bit.bytes2hex(ret)))
    print('-------------------------', len(ret))

    ret = Crypto.xor_bytes(b'require "main"', key)
    print('{%s}' % ','.join(Bit.bytes2hex(ret)))
    print('-------------------------', len(ret))

    ret = Crypto.xor_bytes(b'src/main.lua', key)
    print('{%s}' % ','.join(Bit.bytes2hex(ret)))
    print('-------------------------', len(ret))

    ret = Crypto.xor_bytes(b'$yz#z0X78', key)
    print('{%s}' % ','.join(Bit.bytes2hex(ret)))
    print('-------------------------', len(ret))

    ret = Crypto.xor_bytes(b'0x0305~yz', key)
    print('{%s}' % ','.join(Bit.bytes2hex(ret)))
    print('-------------------------', len(ret))

def test_mod_optime():
    for i in range(1024):
        print(i, i % 16, i & 15)
        if i % 16 != i & 15:
            print('----')

def _modify_androidmanifest(file_path):
    if not os.path.exists(file_path):
        print(f"文件不存在：{file_path}")
        return
    # file = open(file_path, 'r', encoding='utf-8')
    # dom_tree = minidom.parse(file)
    # activity_elements = dom_tree.documentElement.getElementsByTagName("activity")
    # for activity in activity_elements:
    #     android_name = activity.getAttribute("android:name")
    #     if android_name.endswith('.MainActivity'):
    #         activity.setAttribute("android:configChanges", "screenLayout|smallestScreenSize")
    #         break
    # try:
    #     with open(file_path, 'w', encoding='utf-8') as f:
    #         f.write(dom_tree.toprettyxml(newl=''))
    #         print(f"写入成功：{file_path}")
    # except Exception as e:
    #     print(e)
    with open(file_path, 'r', encoding='utf-8') as fp:
        file_content = fp.read()
    file_lines = file_content.split('\n')
    is_begin = False
    modified = 0
    parttern = re.compile('".*"')
    config_changes = '|'.join((
        'density',
        'fontScale',
        'keyboard',
        'keyboardHidden',
        'layoutDirection',
        'locale',
        'mcc',
        'mnc',
        'navigation',
        'orientation',
        'screenLayout',
        'screenSize',
        'smallestScreenSize',
        'touchscreen',
        'uiMode'
    ))
    launch_mode = 'singleTask'
    for i in range(len(file_lines)):
        line_content = file_lines[i].strip()
        if is_begin:
            if line_content.startswith('<'):
                is_begin = False
            elif line_content.startswith('android:configChanges'):
                file_lines[i] = parttern.sub(f'"{config_changes}"', file_lines[i])
                modified = modified + 1
                if modified > 1:
                    break
            elif line_content.startswith('android:launchMode'):
                file_lines[i] = parttern.sub(f'"{launch_mode}"', file_lines[i])
                modified = modified + 1
                if modified > 1:
                    break
        else:
            if line_content.startswith('android:name') and line_content.endswith('.MainActivity"'):
                is_begin = True
    if modified > 1:
        file_content = '\n'.join(file_lines)
        with open(file_path, 'w', encoding='utf-8') as fp:
            fp.write(file_content)
        print(f"写入成功：{file_path}")
    else:
        raise RuntimeError(f'修改失败：{file_path}')

def test_modify_androidmanifest():
    projdir = '/Users/joli/proj/sdk_uzone/trunk/projects/zhanguo/zhanguo_as/app'
    # projdir = '/Users/joli/proj/sdk_uzone/trunk/projects/luandou/luandou_as/app'
    for appname in os.listdir(projdir):
        apppath = os.path.join(projdir, appname)
        if not os.path.isdir(apppath):
            continue
        srcpath = os.path.join(apppath, 'src')
        for varname in os.listdir(srcpath):
            if varname == 'main':
                continue
            varpath = os.path.join(srcpath, varname)
            xmlpath = os.path.join(varpath, 'AndroidManifest.xml')
            _modify_androidmanifest(xmlpath)

def test_fenxi_bundlejson():
    projdir = '/Users/joli/Work/CS/C/xiuxian_new_release'
    jsonpath = os.path.join(projdir, 'build/bvm/notes/bundle_16774_116191.json')
    with open(jsonpath, 'r') as fp:
        manifest = json.load(fp)
        manifest = manifest['files']
    outdir = '/Users/joli/Downloads/out'
    dzgdir = os.path.join(projdir, 'dazhanguo')
    dzgpos = len(dzgdir) + 1
    for par, _, files in os.walk(os.path.join(dzgdir, 'res')):
        for fn in files:
            if fn.endswith(".DS_Store"):
                continue
            fp = os.path.join(par, fn)
            fk = fp[dzgpos:]
            if fk not in manifest or manifest[fk]['sign'] != FS.md5(fp):
                dstpath = os.path.join(outdir, fk)
                FS.make_parent(dstpath)
                shutil.copyfile(fp, dstpath)

def test_split_spine():
    # def spine(atlaspath, imagepath=None, outputdir=None, fixwhite=True):
    spine_dir = '/Users/joli/Downloads/sp/assetbundles'
    for par, _, files in os.walk(spine_dir):
        for fn in files:
            if fn.endswith('.atlas'):
                fp1 = os.path.join(par, fn)
                fd1 = os.path.dirname(fp1)
                print('------------', fp1)
                ImageTailor.spine(fp1, outputdir=os.path.join(fd1, 'images'))

def main():
    # test_fenxi_bundlejson()
    # test_split_spine()
    cut = len('/Users/joli/Work/CS/C/xuanmen_dev/')
    with open('/Users/joli/Desktop/sync.txt', 'r') as fp:
        s = fp.read()
        for ff in s.split('\n'):
            if not os.path.isfile(ff):
                continue
            # print(ff)
            fn = ff[cut:]
            print(fn)
            shutil.copyfile(ff, '/Users/joli/Work/proj.h/HClient/' + fn)

if __name__ == '__main__':
    main()