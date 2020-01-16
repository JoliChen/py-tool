# -*- coding: utf-8 -*-
# @Time    : 2019/4/11 5:56 PM
# @Author  : Joli
# @Email   : 99755349@qq.com
import json
import os
import random
from PIL import Image
from jonlin.utils import FS

def _get_design_rules():
    return {
        "images": [
            {
                "filename": "640x960.png",
                "scale": "2x",
                "orientation": "portrait",
                "extent": "full-screen",
                "idiom": "iphone",
                "minimum-system-version": "7.0",
            },
            {
                "filename": "640x1136.png",
                "scale": "2x",
                "subtype": "retina4",
                "orientation": "portrait",
                "extent": "full-screen",
                "idiom": "iphone",
                "minimum-system-version": "7.0"
            },
            {
                "filename": "750x1334.png",
                "scale": "2x",
                "subtype": "667h",
                "orientation": "portrait",
                "extent": "full-screen",
                "idiom": "iphone",
                "minimum-system-version": "8.0"
            },
            {
                "filename": "1242x2208.png",
                "scale": "3x",
                "subtype": "736h",
                "orientation": "portrait",
                "extent": "full-screen",
                "idiom": "iphone",
                "minimum-system-version": "8.0"
            },
            {
                "filename": "1125x2436.png",
                "scale": "3x",
                "subtype": "2436h",
                "orientation": "portrait",
                "extent": "full-screen",
                "idiom": "iphone",
                "minimum-system-version": "11.0"
            },
            {
                "filename": "828x1792.png",
                "scale": "2x",
                "subtype": "1792h",
                "orientation": "portrait",
                "extent": "full-screen",
                "idiom": "iphone",
                "minimum-system-version": "12.0",
            },
            {
                "filename": "1242x2688.png",
                "scale": "3x",
                "subtype": "2688h",
                "orientation": "portrait",
                "extent": "full-screen",
                "idiom": "iphone",
                "minimum-system-version": "12.0"
            },
            {
                "filename": "768x1024.png",
                "scale": "1x",
                "orientation": "portrait",
                "extent": "full-screen",
                "idiom": "ipad",
                "minimum-system-version": "7.0"
            },
            {
                "filename": "1536x2048.png",
                "scale": "2x",
                "orientation": "portrait",
                "extent": "full-screen",
                "idiom": "ipad",
                "minimum-system-version": "7.0"
            }
        ],
        "info": {"version": 1, "author": "xcode"}
    }

def _calc_select_able(filename):
    rate = {'640x960.png': 30, '828x1792.png': 50, '768x1024.png': 30}
    return (rate.get(filename) or 100) >= random.randint(1, 100)

def _calc_image_size(filename):
    size = filename[0:-4].split('x')
    size = (int(size[0].strip()), int(size[1].strip()))
    return size

def _rand_name(records=None, left=3, right=15):
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

def _make_logo_images(outdir, simple, is_portrait, bg_color=None, scale=1):
    def output_image(img_path, img_size, logo_path, is_base_img):
        foreground = Image.open(logo_path)
        rgba = list(foreground.getbands())
        foreground_mask = False
        if 'A' in rgba:
            chan = foreground.split()
            bbox = chan[rgba.index('A')].getbbox()
            foreground = foreground.crop(bbox)
            foreground_mask = True
        if is_base_img:
            if not is_portrait:
                foreground = foreground.transpose(Image.ROTATE_270)  # 顺时针
            logo_size = foreground.size
            logo_size = (int(logo_size[0] * scale), int(logo_size[1] * scale))
        else:
            logo_size = foreground.size
            wf = img_size[0] / logo_size[0]
            hf = img_size[1] / logo_size[1]
            if wf < hf:
                hf = int(logo_size[1] * wf)
                wf = img_size[0]  # int(logo_size[0] * wf)
            else:
                wf = int(logo_size[0] * hf)
                hf = img_size[1]  # int(logo_size[1] * hf)
            logo_size = (wf, hf)
        foreground = foreground.resize(logo_size, Image.ANTIALIAS)
        # 设置logo位置
        x = int((img_size[0] - logo_size[0]) * 0.5)
        y = int((img_size[1] - logo_size[1]) * 0.5)
        box = (x, y, x + logo_size[0], y + logo_size[1])
        # 贴上logo
        background = Image.new('RGBA', img_size, bg_color)
        if foreground_mask:
            background.paste(foreground, box, foreground.split()[3])
        else:
            background.paste(foreground, box)
        # background.show()
        background.save(img_path)

    def create_item(img_node, logo_path, name_list, is_base_img=False):
        img_size = _calc_image_size(img_node['filename'])
        img_name = _rand_name(name_list) + '.png'
        img_path = os.path.join(outdir, img_name)
        img_node['filename'] = img_name
        output_image(img_path, img_size, logo_path, is_base_img)
        return img_path

    jcontents = _get_design_rules()
    img_nodes = jcontents['images']
    img_names = []  # 命名表
    base_img_tag = 1
    base_img_pos = create_item(img_nodes[base_img_tag], simple, img_names, True)
    for i in range(len(img_nodes) - 1, -1, -1):
        if i == base_img_tag:
            continue
        if _calc_select_able(img_nodes[i]['filename']):
            create_item(img_nodes[i], base_img_pos, img_names)
        else:
            img_nodes.pop(i)
    json_text = json.dumps(jcontents, indent='\t')
    FS.write_text(os.path.join(outdir, 'Contents.json'), json_text)
    print(json_text)

def _make_clip_images(outdir, simple, is_portrait, align='center'):
    def output_image(img_path, img_size):
        image_obj = Image.open(simple)
        if not is_portrait:
            image_obj = image_obj.transpose(Image.ROTATE_270)  # 顺时针
        clip_size = image_obj.size
        wf = img_size[0] / clip_size[0]
        hf = img_size[1] / clip_size[1]
        if wf > hf:
            hf = int(clip_size[1] * wf)
            wf = img_size[0]  # int(logo_size[0] * wf)
        else:
            wf = int(clip_size[0] * hf)
            hf = img_size[1]  # int(logo_size[1] * hf)
        clip_size = (wf, hf)
        image_obj = image_obj.resize(clip_size, Image.ANTIALIAS)
        clip_rect = [0, 0, 0, 0]
        if align == 'center':
            clip_rect[0] = int((clip_size[0] - img_size[0]) * 0.5)
            clip_rect[1] = int((clip_size[1] - img_size[1]) * 0.5)
            clip_rect[2] = clip_rect[0] + img_size[0]
            clip_rect[3] = clip_rect[1] + img_size[1]
        image_obj = image_obj.crop(clip_rect)
        image_obj.save(img_path)

    jcontents = _get_design_rules()
    img_nodes = jcontents['images']
    img_names = []  # 命名表
    for i in range(len(img_nodes) - 1, -1, -1):
        if _calc_select_able(img_nodes[i]['filename']):
            img_name = _rand_name(img_names) + '.png'
            output_image(os.path.join(outdir, img_name), _calc_image_size(img_nodes[i]['filename']))
            img_nodes[i]['filename'] = img_name
        else:
            img_nodes.pop(i)
    json_text = json.dumps(jcontents, indent='\t')
    FS.write_text(os.path.join(outdir, 'Contents.json'), json_text)
    print(json_text)

def make_images(root):
    import biplist
    config = biplist.readPlist(os.path.join(root, 'iOS image.plist'))
    outdir = os.path.join(root, config['lanunchimage_dir'])
    simple = os.path.join(root, config['lanunchimage_src'])
    is_portrait = config['lanunchimage_isPortrait']

    FS.cleanup_dir(outdir)
    is_crop_mode = config['lanunchimage_cropMode']
    if is_crop_mode:
        _make_clip_images(outdir, simple, is_portrait, config['lanunchimage_cropAlign'])
    else:
        scale = config['lanunchimage_scale']
        bg_color = []
        for s in config['lanunchimage_bgColor'].split(','):
            bg_color.append(int(s.strip()))
        _make_logo_images(outdir, simple, is_portrait, tuple(bg_color), scale)