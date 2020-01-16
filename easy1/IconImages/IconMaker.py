#encoding=utf-8

import os
import json
import random
import shutil
from PIL import Image

def _full_tool_path(path):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), path)

# 获取一个尚未存在名字，避免覆盖。
def _rand_name(mapping):
    while True :
        name = ''
        for i in range(random.randint(5, 10)):
            factor = random.random()
            if factor < 0.4:
                name += chr(random.randint(65, 90))
            elif factor < 0.7:
                name += chr(random.randint(97, 122))
            else:
                name += str(random.randint(1, 1024))
        if (mapping is not None) and (name not in mapping) :
            mapping.append(name)
            return name

def _write_string(path, text):
    f = open(path, 'w')
    f.write(text)
    f.flush()
    f.close()

def _read_string(path):
    f = open(path)
    t = f.read()
    f.close()
    return t

def _make_android_launchImage(source):
    return

def _make_android_appIcon(source):
    return

def _make_ios_launchImage(source):
    return

def _make_ios_appIcon(source, icon_dir):
    icon = Image.open(source).convert("RGBA")
    if icon.size[0] != icon.size[1]:
        print('Icon file must be a rectangle!')
        return
    tempText = _read_string(_full_tool_path('template/ios/AppIconContents.json'))
    if (tempText == None) or (tempText.__len__() <= 0) :
        print('ios icon templete is None')
        return
    template = json.loads(tempText)
    if (template == None) :
        print('templete parse error')
        return
    # 清理文件夹
    if os.path.exists(icon_dir):
        shutil.rmtree(icon_dir)
    os.makedirs(icon_dir)
    # 输出icon
    nameMapping = []
    name1024 = None
    for item in template[u'images'] :
        scale = float(item['scale'].split('x')[0]) # scale:2x
        size = float(item['size'].split('x')[0]) # size:20x20
        size = int(size * scale)
        imageName = _rand_name(nameMapping) + '.png'
        item[u'filename'] = imageName
        if (size == 1024) :
            name1024 = imageName
        else :
            iconImage = icon.resize((size, size), Image.LANCZOS)
            iconImage.save(os.path.join(icon_dir, imageName))
    #去除1024的alpha通道
    if (icon.size[0] != 1024) :
        icon = icon.resize((1024, 1024), Image.LANCZOS)
    icon1024 = Image.new("RGB", (1024, 1024), (255, 255, 255))
    icon1024.paste(icon, mask=icon.split()[3])
    icon1024.save(os.path.join(icon_dir, name1024), 'PNG')
    #输出配置文件
    tempText = json.dumps(template)
    _write_string(os.path.join(icon_dir, 'Contents.json'), tempText)
    print(tempText)

def make_appIcon():
    _make_ios_appIcon('/Users/joli/desktop/outputs/icon/1024.png', '/Users/joli/desktop/outputs/icon/ios')


# 入口函数
# def main(platform, action, source):
#     p = platform.lower()
#     a = action.lower()
#     if p == 'android' :
#         if a == 'icon' :
#             makeAndroidAppIcon(source)
#         elif a == 'screenshot' :
#             makeAndroidLaunchImage(source)
#     elif p == 'ios' :
#         if a == 'icon' :
#             makeIosAppIcon(source)
#         elif a == 'screenshot' :
#             makeIosLaunchImage(source)
