# -*- coding: UTF-8 -*-
import os

import shutil

import PIL
from PIL import Image, ImageFilter

class iOSLaunchMaker:
    def __init__(self, source_image, output_dir, bg_color=(0,0,0), srouce_rotate=None):
        self._source_image = source_image
        self._srouce_rotate = srouce_rotate
        self._output_dir = output_dir
        self._bg_color = bg_color
        self.scale_factor = 1

    def _auto_fix_size(self, src_size, dst_size):
        wf = dst_size[0] / src_size[0]
        hf = dst_size[1] / src_size[1]
        w = 0
        h = 0
        if wf < hf:
            w = int(src_size[0] * wf)
            h = int(src_size[1] * wf)
        else:
            w = int(src_size[0] * hf)
            h = int(src_size[1] * hf)
        # print('sacle size:(%d, %d)', w, h)
        return (w, h)

    def _save_image(self, fg_path, bg_path, bg_size, bg_color=(0, 0, 0), fg_transpose=None, auto_fix=True):
        foreground = Image.open(fg_path)
        rgba = list(foreground.getbands())
        foreground_mask = False
        if 'A' in rgba:
            chan = foreground.split()
            bbox = chan[rgba.index('A')].getbbox()
            foreground = foreground.crop(bbox)
            foreground_mask = True
        if fg_transpose is not None:
            foreground = foreground.transpose(fg_transpose) # 顺时针角度表示
        if auto_fix:
            auto_scale_size = self._auto_fix_size(foreground.size, bg_size)
            foreground = foreground.resize(auto_scale_size, Image.ANTIALIAS)
        else:
            scale_factor = self.scale_factor
            manu_scale_size = (int(foreground.size[0]*scale_factor), int(foreground.size[1]*scale_factor))
            foreground = foreground.resize(manu_scale_size, Image.ANTIALIAS)
        fg_size = foreground.size

        x = int((bg_size[0] - fg_size[0]) * 0.5)
        y = int((bg_size[1] - fg_size[1]) * 0.5)
        box = (x, y, x + fg_size[0], y + fg_size[1])

        background = Image.new('RGBA', bg_size, bg_color)
        if foreground_mask:
            background.paste(foreground, box, foreground.split()[3])
        else:
            background.paste(foreground, box)

        # background.show()
        background.save(bg_path)

    def _prepare(self):
        if os.path.exists(self._output_dir):
            shutil.rmtree(self._output_dir)
        os.makedirs(self._output_dir)

    def build(self):
        self._prepare()
        image_sizes = [(640, 1136), (750, 1334), (1242, 2208), (1125, 2436), (1536, 2048)]
        base_size_pos = 0
        base_img_size = image_sizes[base_size_pos]
        base_img_path = os.path.join(self._output_dir, '%dx%d.png' % (base_img_size[0], base_img_size[1]))
        self._save_image(self._source_image, base_img_path, base_img_size, self._bg_color, self._srouce_rotate, False)

        for i in range(len(image_sizes)):
            if i == base_size_pos:
                continue
            img_size = image_sizes[i]
            img_path = os.path.join(self._output_dir, '%dx%d.png' % (img_size[0], img_size[1]))
            self._save_image(base_img_path, img_path, img_size, self._bg_color)

def make_launch():
    ios_launch_maker = iOSLaunchMaker(
        '/Users/joli/Desktop/outputs/icon&images/image.png',
        '/Users/joli/Desktop/outputs/icon&images/LaunchImage.launchimage',
        # (0, 0, 0), PIL.Image.ROTATE_270
        (255, 255, 255), PIL.Image.ROTATE_270
        # (128, 62, 224), PIL.Image.ROTATE_270
        # (255, 255, 255)
        # (0, 0, 0)
    )
    ios_launch_maker.scale_factor = 0.6
    ios_launch_maker.build()