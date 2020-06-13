# -*- coding: utf-8 -*-
# @Time    : 2019/4/18 11:27 AM
# @Author  : Joli
# @Email   : 99755349@qq.com
# android adb

from jonlin.cl import Shell

def fmt(script, device=None):
    if device:
        return 'adb -s %s %s' % (device, script)
    else:
        return 'adb %s' % script

def list_devices():  # 列出连接的手机
    array = []
    lines = Shell.stdout(fmt('devices')).split('\n')
    for i in range(1, len(lines)):  # List of devices attached
        item = lines[i]
        if item:
            array.append(item[:item.find('\tdevice')])
    return array

def list_packages(device=None):
    array = []
    for item in Shell.stdout(fmt('shell pm list packages', device)).split('\n'):
        item = item.strip()
        if item:
            array.append(item[item.find(':')+1:])
    return array

def select(device):
    device_list = list_devices()
    assert device_list, 'no device connected'
    if device:
        assert device in device_list, 'device(%s) not connect' % device
    return device

def pull(src, dst, device=None):  # 从手机上传到电脑
    return Shell.run(fmt('pull %s %s' % (src, dst), device))

def install(apk, appid=None, device=None):  # 安装应用
    if appid and appid in list_packages(device):
        # retcode = Shell.run(fmt('uninstall %s' % appid, device))
        # assert 0 == retcode, 'uninstall apk fail:%d' % retcode
        return Shell.run(fmt('install -r %s' % apk, device))
    return Shell.run(fmt('install %s' % apk, device))

def screenshot(image='/sdcard/screenshot.png', device=None):  # 在手机上截图
    return Shell.run(fmt('shell /system/bin/screencap -p %s' % image, device))