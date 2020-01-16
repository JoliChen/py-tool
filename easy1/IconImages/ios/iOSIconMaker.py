# -*- coding: UTF-8 -*-

import json
import os
import random
import shutil
from PIL import Image, ImageFilter
from IconImages.ios.iOSHIG import iOSHIG

class iOSIconMaker:
    def __init__(self, source_icon, output_dir):
        self._source_icon = source_icon
        self._output_dir = output_dir
        self._contents = None

    @staticmethod
    def _rand_name(records=None, left=5, right=10):
        while True:
            name = ''
            for i in range(random.randint(left, right)):
                factor = random.random()
                if factor < 0.4:
                    name += chr(random.randint(65, 90))
                elif factor < 0.7:
                    name += chr(random.randint(97, 122))
                else:
                    name += str(random.randint(1, 1024))
            if records is None:
                return name
            if name not in records:
                records.append(name)
                return name

    @staticmethod
    def _trans_idiom(devices):
        if 'iPhone' in devices:
            return 'iphone'
        if 'iPad' in devices:
            return 'ipad'
        if 'App Store' in devices:
            return 'ios-marketing'
        return devices

    def _load_contents(self):
        images = []
        for icon_type in iOSHIG.ICON_RATE:
            rate_base = iOSHIG.ICON_RATE[icon_type]
            if random.randint(1, 100) > rate_base:
                continue
            icon_size_dict = iOSHIG.ICON_SIZE[icon_type]
            for devices in icon_size_dict:
                idiom = self._trans_idiom(devices)
                icon_size_list = icon_size_dict[devices]
                for icon_size_desc in icon_size_list:
                    parts = icon_size_desc.split('@')
                    size_item = {
                        'size': '%sx%s' % (parts[0], parts[0]),
                        'idiom':idiom,
                        'filename': 'icon-%s.png' % icon_size_desc,
                        'scale':parts[1]
                    }
                    images.append(size_item)
        informations = {
            'version': 1, # random.randint(1, 10000),
            'author': self._rand_name(None, 6, 20)
        }
        self._contents = {'images':images, 'info':informations}
        # print('contents:%s' % self._contents)

    def _save_contents(self):
        json_text = json.dumps(self._contents)
        f = open(os.path.join(self._output_dir, 'Contents.json'), 'w')
        f.write(json_text)
        f.flush()
        f.close()

    def _make_icons(self):
        srouce_icon = Image.open(self._source_icon).convert("RGBA")
        assert srouce_icon.size[0] == srouce_icon.size[1], 'Icon file must be a rectangle!'

        # 输出icon
        name_list = []
        name_1024 = None
        for item in self._contents['images']:
            scale = float(item['scale'].split('x')[0])  # scale:2x
            size = float(item['size'].split('x')[0])  # size:20x20
            size = int(size * scale)
            name = self._rand_name(name_list) + '.png'
            if (size == 1024):
                name_1024 = name
            else:
                icon_image = srouce_icon.resize((size, size), Image.ANTIALIAS)
                icon_image.save(os.path.join(self._output_dir, name))
            item['filename'] = name

        # 去除1024的alpha通道
        if (srouce_icon.size[0] != 1024):
            srouce_icon = srouce_icon.resize((1024, 1024), Image.ANTIALIAS)
        icon_1024 = Image.new("RGB", (1024, 1024), (255, 255, 255))
        icon_1024.paste(srouce_icon, mask=srouce_icon.split()[3])
        icon_1024.save(os.path.join(self._output_dir, name_1024), 'PNG')

    def _prepare(self):
        if os.path.exists(self._output_dir):
            shutil.rmtree(self._output_dir)
        os.makedirs(self._output_dir)

    def build(self):
        self._prepare()
        self._load_contents()
        self._make_icons()
        self._save_contents()

def make_icon():
    iOS_icon_maker = iOSIconMaker(
        '/Users/joli/Desktop/outputs/icon&images/icon.png',
        '/Users/joli/Desktop/outputs/icon&images/AppIcon.appiconset'
    )
    iOS_icon_maker.build()