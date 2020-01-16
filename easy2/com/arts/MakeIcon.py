# -*- coding: utf-8 -*-
# @Time    : 2019/4/11 4:28 PM
# @Author  : Joli
# @Email   : 99755349@qq.com

import os
import json
import random
from PIL import Image
from jonlin.utils import FS

def _rand_name(records=None, left=5, right=15):
    while True:
        name = ''
        for i in range(random.randint(left, right)):
            factor = random.random()
            if factor < 0.4:
                name += chr(random.randint(65, 90))
            elif factor < 0.8:
                name += chr(random.randint(97, 122))
            else:
                name += str(random.randint(0, 9))
        if records is None:
            return name
        if name not in records:
            records.append(name)
            return name

def _build_ios(source, icon_dir):
    # ios icon 设计规则
    def get_design_rules():
        return {
            'App': {
                'iPhone': ['60@3x', '60@2x'],
                'iPad Pro': ['83.5@2x'],
                'iPad, iPad mini': ['76@1x', '76@2x'],
                'App Store': ['1024@1x']
            },
            'Spotlight': {
                'iPhone': ['40@3x', '40@2x'],
                'iPad Pro, iPad, iPad mini': ['40@2x']
            },
            'Settings': {
                'iPhone': ['29@3x', '29@2x'],
                'iPad Pro, iPad, iPad mini': ['29@2x']
            },
            'Notification': {
                'iPhone': ['20@3x', '20@2x'],
                'iPad Pro, iPad, iPad mini': ['20@2x']
            }
        }

    # ios icon 每种类型的生成概率
    def get_catalog_rate():
        return {'App': 100, 'Spotlight': 60, 'Settings': 60, 'Notification': 60}

    # 转换名称
    def trans_idiom(devices):
        if 'iPhone' in devices:
            return 'iphone'
        if 'iPad' in devices:
            return 'ipad'
        if 'App Store' in devices:
            return 'ios-marketing'
        return devices

    # step1: clear
    FS.cleanup_dir(icon_dir)
    # step2: load template
    icon_rules = get_design_rules()
    icon_rates = get_catalog_rate()
    images = []
    for catalog in icon_rates:
        if icon_rates[catalog] < random.randint(1, 100):
            continue
        zone_dict = icon_rules[catalog]
        for device in zone_dict:
            idiom = trans_idiom(device)
            icon_size_list = zone_dict[device]
            for icon_size_desc in icon_size_list:
                parts = icon_size_desc.split('@')
                size_item = {
                    'size': '%sx%s' % (parts[0], parts[0]),
                    'idiom': idiom,
                    'filename': 'icon-%s.png' % icon_size_desc,
                    'scale': parts[1]
                }
                images.append(size_item)
    contents = {'images': images, 'info': {
        'version': 1,
        'author': 'xcode'
    }}
    # step3: create icon
    srouce_icon = Image.open(source).convert("RGBA")
    assert srouce_icon.size[0] == srouce_icon.size[1], 'source icon must be a rectangle!'
    size_dict = {}  # 避免重复生成相同尺寸的图片
    name_list = []
    name_1024 = None
    for item in contents['images']:
        scale = float(item['scale'].split('x')[0])  # scale:2x
        size = float(item['size'].split('x')[0])  # size:20x20
        size = int(size * scale)
        if 1024 != size:
            name = size_dict.get(size)
            if not name:
                name = _rand_name(name_list) + '.png'
                size_dict[size] = name
                icon_image = srouce_icon.resize((size, size), Image.ANTIALIAS)
                icon_image.save(os.path.join(icon_dir, name))
        else:
            name = _rand_name(name_list) + '.png'  # 1024的不透明icon最后生成
            name_1024 = name
        item['filename'] = name
    # 去除1024的alpha通道
    if 1024 != srouce_icon.size[0]:
        srouce_icon = srouce_icon.resize((1024, 1024), Image.ANTIALIAS)
    icon_1024 = Image.new("RGB", (1024, 1024), (255, 255, 255))
    icon_1024.paste(srouce_icon, mask=srouce_icon.split()[3])
    icon_1024.save(os.path.join(icon_dir, name_1024), 'PNG')
    # 保存配置
    json_text = json.dumps(contents, indent='\t')
    FS.write_text(os.path.join(icon_dir, 'Contents.json'), json_text)
    print(json_text)

def _build_android(source, icon_dir):
    srouce_icon = Image.open(source).convert("RGBA")
    assert srouce_icon.size[0] == srouce_icon.size[1], 'source icon must be a rectangle!'
    icon_image = srouce_icon.resize((192, 192), Image.ANTIALIAS)
    icon_image.save(os.path.join(icon_dir, 'app_icon.png'))
    print('create icon-192*192 done')

def make_icons(root, android=False):
    import biplist
    if android:
        config = biplist.readPlist(os.path.join(root, 'android icon.plist'))
        _build_android(
            os.path.join(root, config['icon_src']),
            root
        )
    else:
        config = biplist.readPlist(os.path.join(root, 'iOS icon.plist'))
        _build_ios(
            os.path.join(root, config['icon_src']),
            os.path.join(root, config['icon_dir'])
        )