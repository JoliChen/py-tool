# -*- coding: utf-8 -*-
# @Time    : 2021/6/26 6:17 PM
# @Author  : Joli
# @Email   : 99755349@qq.com
import json
import os
import re
from xml.dom import minidom

from jonlin.utils import Crypto, Bit


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

def main():
    # print(json.dumps({"command": "openRechargeView", "args": {"storeType": 1}}))
    # test_crypto()
    # test_mod_optime()
    # test_modify_androidmanifest()

    # for sn in range(1, 256):
    #     for module in range(1, 256):
    #         for cmd in range(1, 256):
    #             a = sn << 16 | module << 8 | cmd
    #             b = sn * 65536 + module * 256 + cmd
    #             if a == b:
    #                 print('errr', a, b)

    print(pow(2, 16))
    print('done')

if __name__ == '__main__':
    main()