# -*- coding: utf-8 -*-
# @Time    : 2019/5/5 6:42 PM
# @Author  : Joli
# @Email   : 99755349@qq.com
import os
import sys
import time

def test_delete_all_dsstore(root_dir='/Users/joli'):  # 删除目录下所有的 .DS_Store
    for (root, _, files) in os.walk(root_dir):
        for name in files:
            if '.DS_Store' == name:
                f = os.path.join(root, name)
                print('remove:', f)
                os.remove(f)

def test_clear_meta():
    for (root, _, files) in os.walk('/Users/joli/Work/StonePro/stoneclient/Unity/Assets'):
        for name in files:
            if name.endswith('.meta'):
                f = os.path.join(root, name)
                print('remove:', f)
                os.remove(f)

# windows color console
def test_win_color_console():
    STD_INPUT_HANDLE = -10
    STD_OUTPUT_HANDLE = -11
    STD_ERROR_HANDLE = -12

    # 字体颜色定义 text colors
    FOREGROUND_BLACK = 0x00  # black.
    FOREGROUND_DARKBLUE = 0x01  # dark blue.
    FOREGROUND_DARKGREEN = 0x02  # dark green.
    FOREGROUND_DARKSKYBLUE = 0x03  # dark skyblue.
    FOREGROUND_DARKRED = 0x04  # dark red.
    FOREGROUND_DARKPINK = 0x05  # dark pink.
    FOREGROUND_DARKYELLOW = 0x06  # dark yellow.
    FOREGROUND_DARKWHITE = 0x07  # dark white.
    FOREGROUND_DARKGRAY = 0x08  # dark gray.
    FOREGROUND_BLUE = 0x09  # blue.
    FOREGROUND_GREEN = 0x0a  # green.
    FOREGROUND_SKYBLUE = 0x0b  # skyblue.
    FOREGROUND_RED = 0x0c  # red.
    FOREGROUND_PINK = 0x0d  # pink.
    FOREGROUND_YELLOW = 0x0e  # yellow.
    FOREGROUND_WHITE = 0x0f  # white.

    import ctypes
    std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

    def set_cmd_text_color(color, handle=std_out_handle):
        b = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
        return b

    def reset_color():
        set_cmd_text_color(FOREGROUND_DARKWHITE)

    def print_red(mess):
        set_cmd_text_color(FOREGROUND_RED)
        sys.stdout.write(mess)
        reset_color()

    def print_green(mess):
        set_cmd_text_color(FOREGROUND_GREEN)
        sys.stdout.write(mess)
        reset_color()

    def print_yellow(mess):
        set_cmd_text_color(FOREGROUND_YELLOW)
        sys.stdout.write(mess)
        reset_color()

    print_red('aasdfasdfasdfsdf我的1ewr342234啊')
    print_green('aasdfasdfasdfsdf我的1ewr342234啊')
    print_yellow('aasdfasdfasdfsdf我的1ewr342234啊')

def test_adb_screenshot():
    from jonlin.cl import ADB
    ADB.screenshot('/sdcard/screenshot.png')
    ADB.pull('/sdcard/screenshot.png', '/Users/joli/desktop/android_screenshot.png')

def test_adb_dingding_workon():
    import uiautomator2
    print('正在连接设备，请等待...')
    d = uiautomator2.connect()
    print('正在启动钉钉...')
    d.app_start('com.alibaba.android.rimet')
    time.sleep(20)
    print('打卡成功，退出APP')
    d.app_stop('com.alibaba.android.rimet')

def test_adb_dingding_workoff():
    import uiautomator2
    print('正在连接设备，请等待...')
    d = uiautomator2.connect()
    try:
        d.app_stop('com.alibaba.android.rimet')
    except:
        print('未运行钉钉！')
    print('正在启动钉钉...')
    d.app_start('com.alibaba.android.rimet')
    time.sleep(10)
    d(resourceId="com.alibaba.android.rimet:id/home_bottom_tab_icon", className="android.widget.ImageView", instance=1).click()
    # d.drag(0.5, 0.7, 0.5, 0.1, 0.5)
    # time.sleep(10)
    d.click(0.135, 0.65)
    # d.click(0.131, 0.731)
    time.sleep(10)

    d.click(0.497, 0.631)
    d.click(0.172, 0.639)
    try:
        time.sleep(5)
        d.click(0.773, 0.55)
        print('打卡成功，关闭钉钉')
        time.sleep(5)
        d.app_stop('com.alibaba.android.rimet')
    except:
        print('打卡失败！')
        d.app_stop('com.alibaba.android.rimet')

def test_adb_connect_nox():
    os.system('adb kill-server')
    os.system('adb start-server')
    os.system('adb connect 127.0.0.1:62001')
    os.system('adb devices')

def test_adb_connect_mumu():
    os.system('adb kill-server')
    os.system('adb start-server')
    os.system('adb connect 127.0.0.1:7555')
    os.system('adb devices')

def test_clear_adobe():
    pass
    # 'sudo killall ACCFinderSync "Core Sync" AdobeCRDaemon "Adobe Creative" AdobeIPCBroker node "Adobe Desktop Service" "Adobe Crash Reporter"'
    #
    # 'sudo rm -rf '
    # "/Library/Application Support/Adobe/SLCache/"
    # "/Library/Application Support/Adobe/SLStore/"
    # "/Library/Caches/."
    # "/private/tmp/zx"
    # "~/Library/Application Support/Adobe/"
    # "~/Library/Preferences/Adobe/."'

def test_package_air():
    def _package_(projxml, output, keystore):
        airbin_root = '/Users/joli/Applications/Adobe/Adobe Flash Builder 4.7/sdks/4.6.0/bin'
        execute_dir = os.getcwd()
        print(execute_dir)
        os.chdir(airbin_root)
        print(os.getcwd())
        os.system('./adt -package -storetype pkcs12 -keystore %s -target native %s %s .' % (keystore, output, projxml))
        os.chdir(execute_dir)
        print(os.getcwd())

    proj = '/Users/joli/proj/master/flex/Art2'
    xml = os.path.join(proj, 'src/Art2-app.xml')
    dst = os.path.join(proj, 'build')
    key = os.path.join(proj, '../jolidev.p12')
    _package_(xml, dst, key)

def main():
    pass
    # test_clear_adobe()
    test_clear_meta()
    # test_package_air()
    # test_delete_all_dsstore()
    # test_win_color_console()
    # test_adb_screenshot()
    # test_adb_dingding_workon()
    # test_adb_dingding_workoff()
    # test_adb_connect_nox()
    # test_adb_connect_mumu()