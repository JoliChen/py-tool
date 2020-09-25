# -*- coding: utf-8 -*-
# @Time    : 2019/4/9 7:03 PM
# @Author  : Joli
# @Email   : 99755349@qq.com

import os
import xml.dom.minidom

# float转字符串并保留4位小数
def f2s(f):
    return '%.4f' % f

kXmlNode = 'AbstractNodeData'
kTypeText = 'TextObjectData'
kTypeButton = 'ButtonObjectData'
kPropFont = 'FontResource'
kPropOutline = 'OutlineColor'

class MakeCSD:
    def __init__(self):
        pass

    # 修改画布中文本的描边
    def modify_dom_outline(self, csd_file, *tasks):
        csd_dom, changed = xml.dom.minidom.parse(csd_file), False
        for node in csd_dom.getElementsByTagName(kXmlNode):
            if kTypeText == node.getAttribute('ctype'):
                color = self.get_outline(node)
                if not color:
                    continue
                for t in tasks:
                    if not self.is_equal_color(t['old'], color):
                        continue
                    new_color = t['new']
                    if new_color == 'CLOSE':
                        if node.getAttribute('OutlineEnabled') == 'True':
                            # node.removeNamedItem('OutlineEnabled')
                            del node._attrs['OutlineEnabled']
                            changed = True
                    else:
                        self.set_outline(node, new_color)
                        changed = True
        return csd_dom.toxml(encoding='utf-8') if changed else None

    # 修改画布中文本的颜色
    def modify_dom_textcolor(self, csd_file, *tasks):
        csd_dom, changed = xml.dom.minidom.parse(csd_file), False
        for node in csd_dom.getElementsByTagName(kXmlNode):
            if kTypeText == node.getAttribute('ctype'):
                color = self.get_color(node)
                if not color:
                    continue
                for t in tasks:
                    if not self.is_equal_color(t['old'], color):
                        continue
                    new_color = t['new']
                    self.set_color(node, new_color)
                    changed = True
        return csd_dom.toxml(encoding='utf-8') if changed else None

    # 修改画布中的字体
    def modify_dom_font(self, csd_file, font_name, user_ctypes):
        csd_dom, changed = xml.dom.minidom.parse(csd_file), False
        for node in csd_dom.getElementsByTagName(kXmlNode):
            if user_ctypes and node.getAttribute('ctype') not in user_ctypes:
                continue
            changed |= self.modify_dom_font0(csd_dom, node, font_name)
        return csd_dom.toxml(encoding='utf-8') if changed else None

    def modify_dom_font0(self, csd_dom, node, font_name):
        changed = False
        for e in node.getElementsByTagName(kXmlNode):
            if kTypeText == e.getAttribute('ctype'):
                if not font_name:
                    changed |= self.remove_font(e)
                else:
                    changed |= self.set_font(csd_dom, e, font_name)
        if not font_name:
            changed |= self.remove_font(node)
        else:
            if kTypeButton == node.getAttribute('ctype'):
                title = node.getAttribute('ButtonText')
                if not title or title.isspace():
                    return changed  # 纯图片的按钮就不需要添加字体了
            changed |= self.set_font(csd_dom, node, font_name)
        return changed

    # 修改画布中的字体大小
    def modify_dom_fontsize(self, csd_file, *tasks):
        csd_dom, changed = xml.dom.minidom.parse(csd_file), False
        for node in csd_dom.getElementsByTagName(kXmlNode):
            for t in tasks:
                user_ctypes = t['user_ctypes']
                if user_ctypes and node.getAttribute('ctype') not in user_ctypes:
                    continue
                changed |= self.modify_dom_fontsize0(node, t)
        return csd_dom.toxml(encoding='utf-8') if changed else None

    def modify_dom_fontsize0(self, node, task):
        changed = False
        user_fonts = task['user_fonts']
        for e in node.getElementsByTagName(kXmlNode):
            if kTypeText == e.getAttribute('ctype'):
                if user_fonts and self.get_font(e) not in user_fonts:
                    continue
                if e.getAttribute('FontSize') == task['old']:
                    e.setAttribute('FontSize', task['new'])
                    changed = True
        if not user_fonts or self.get_font(node) in user_fonts:
            if node.getAttribute('FontSize') == task['old']:
                node.setAttribute('FontSize', task['new'])
                changed = True
        return changed

    # 修改画布中所有的按钮皮肤
    def modify_dom_btn_skin(self, csd_file, *tasks):
        csd_dom, changed = xml.dom.minidom.parse(csd_file), False
        for node in csd_dom.getElementsByTagName(kXmlNode):
            if kTypeButton != node.getAttribute('ctype'):
                continue
            for t in tasks:
                if not self.validate_button(node, t['feature']):
                    # print('------------------- not validate_button')
                    continue
                # print(node.getAttribute('Name'))
                # print(get_position(node))
                self.modify_btn_skin(node, t['new'])
                changed = True
        # print(csd_dom.toxml(encoding='utf-8'))
        return csd_dom.toxml(encoding='utf-8') if changed else None

    # 修改按钮皮肤
    def modify_btn_skin(self, node, feature):
        skin = feature.get('skin')
        size = feature.get('size')
        title_color = feature.get('title_color')
        title_outline = feature.get('title_outline')
        title_shadow = feature.get('title_shadow')
        children = []
        for prop in node.childNodes:
            if prop.nodeName == 'Children':
                for child in prop.childNodes:
                    if child.nodeName == kXmlNode:
                        children.append(child)
            elif prop.nodeName == 'NormalFileData':
                if skin:
                    prop.setAttribute('Path', skin['normal'])
                    if 'plist' in skin:
                        self.set_plist_prop(prop, skin['plist'])
            elif prop.nodeName == 'PressedFileData':
                if skin:
                    prop.setAttribute('Path', skin['pressed'])
                    if 'plist' in skin:
                        self.set_plist_prop(prop, skin['plist'])
            elif prop.nodeName == 'DisabledFileData':
                if skin:
                    prop.setAttribute('Path', skin['disabled'])
                    if 'plist' in skin:
                        self.set_plist_prop(prop, skin['plist'])
        if children:
            for child in children:
                if child.getAttribute('ctype') == kTypeText:
                    if title_color:
                        self.set_color(child, title_color)
                    if title_outline:
                        self.set_outline(child, title_outline)
                    if title_shadow:
                        self.set_shadow(child, title_shadow)
            if size:
                self.set_size_center_children(node, children, size)
        else:
            if title_color:
                self.set_color(node, title_color)
            if title_outline:
                self.set_outline(node, title_outline)
            if title_shadow:
                self.set_shadow(node, title_shadow)
            if size:
                self.set_size(node, size['width'], size['height'])

    # 设置节点尺寸并把子节点居中对齐
    def set_size_center_children(self, node, children, size):
        p_rect = self.box_node_rect(node)
        # print('p_rect', p_rect)
        b_rect = self.box_children_rect(children)
        b_rect = (b_rect[0]+p_rect[0], b_rect[1]+p_rect[0], b_rect[2]+p_rect[3], b_rect[3]+p_rect[3])
        # print('b_rect', b_rect)

        self.set_size(node, size['width'], size['height'])
        n_rect = self.box_node_rect(node)
        if 'edge' in size:
            hext, vext = 0, 0
            over = b_rect[0] - n_rect[0]
            if over < size['edge'][0]:
                hext += size['edge'][0] - over
            over = n_rect[1] - b_rect[1]
            if over < size['edge'][1]:
                hext += size['edge'][1] - over
            over = n_rect[2] - b_rect[2]
            if over < size['edge'][2]:
                vext += size['edge'][2] - over
            over = b_rect[3] - n_rect[3]
            if over < size['edge'][3]:
                vext += size['edge'][3] - over
            if hext > 0 or vext > 0:
                self.set_size(node, size['width'] + hext, size['height'] + vext)
                n_rect = self.box_node_rect(node)

        # print('n_rect', n_rect)
        nw = abs(n_rect[1] - n_rect[0])
        nh = abs(n_rect[2] - n_rect[3])
        bw = abs(b_rect[1] - b_rect[0])
        bh = abs(b_rect[2] - b_rect[3])
        # print('size', nw, nh, bw, bh)
        cl = p_rect[0] + (nw - bw) * 0.5
        cb = p_rect[3] + (nh - bh) * 0.5
        # print('center_origin', cl, cb)
        ox = cl - b_rect[0]
        oy = cb - b_rect[3]
        if 'offset' in size:
            ox += size['offset'][0]
            oy += size['offset'][1]
        # print('offset', ox, oy)
        for node in children:
            self.add_position(node, ox, oy)

    # 把子节点居中对齐
    def center_children_in_parent(self, node, children):
        p_rect = self.box_node_rect(node)
        # print('p_rect', p_rect)
        b_rect = self.box_children_rect(children)
        b_rect = (b_rect[0] + p_rect[0], b_rect[1] + p_rect[0], b_rect[2] + p_rect[3], b_rect[3] + p_rect[3])
        # print('b_rect', b_rect)
        # print('n_rect', n_rect)
        nw = abs(p_rect[1] - p_rect[0])
        nh = abs(p_rect[2] - p_rect[3])
        bw = abs(b_rect[1] - b_rect[0])
        bh = abs(b_rect[2] - b_rect[3])
        # print('size', nw, nh, bw, bh)
        cl = p_rect[0] + (nw - bw) * 0.5
        cb = p_rect[3] + (nh - bh) * 0.5
        # print('center_origin', cl, cb)
        ox = cl - b_rect[0]
        oy = cb - b_rect[3]
        # print('offset', ox, oy)
        for node in children:
            self.add_position(node, ox, oy)

    # 计算节点的矩形 (不考虑旋转)
    def box_node_rect(self, node):
        x, y = self.get_position(node)
        ax, ay = self.get_anchor(node)
        sx, sy = self.get_scale(node)
        width, height = self.get_size(node)
        width *= sx
        height *= sy
        return (x - ax * width), (x + (1 - ax) * width), (y + (1 - ay) * height), (y - ay * height)

    # 计算子节点组成的大矩形 (不考虑旋转)
    def box_children_rect(self, children):
        bl, br, bt, bb = self.box_node_rect(children[0])
        for node in children[1:]:
            l, r, t, b = self.box_node_rect(node)
            if l < bl:
                bl = l
            if r > br:
                br = r
            if t > bt:
                bt = t
            if b < bb:
                bb = b
        return bl, br, bt, bb

    @staticmethod
    def get_content_root(dom):
        for node in dom.documentElement.childNodes:
            if node.nodeName == 'Content':
                for child in node.childNodes:
                    if child.nodeName == 'Content':
                        return child

    def get_object_root(self, dom):
        content = self.get_content_root(dom)
        if content:
            for node in content.childNodes:
                if node.nodeName == 'ObjectData':
                    for child in node.childNodes:
                        if child.nodeName == 'Children':
                            return child

    #  根据特征确定按钮
    def validate_button(self, node, feature):
        if feature:
            if 'skin' in feature:
                if not self.validate_button_skin(node, feature['skin']):
                    return False
        return True

    # 确定按钮皮肤
    def validate_button_skin(self, node, skin):
        flag = False
        for prop in node.childNodes:
            if prop.nodeName == 'NormalFileData':
                if 'normal' in skin:
                    if prop.getAttribute('Path') != skin['normal']:
                        return False
                    if 'plist' in skin and not self.is_plist_prop(prop, skin['plist']):
                        return False
                    flag = True
            elif prop.nodeName == 'PressedFileData':
                if 'pressed' in skin:
                    if prop.getAttribute('Path') != skin['pressed']:
                        return False
                    if 'plist' in skin and not self.is_plist_prop(prop, skin['plist']):
                        return False
            elif prop.nodeName == 'DisabledFileData':
                if 'disabled' in skin:
                    if prop.getAttribute('Path') != skin['disabled']:
                        return False
                    if 'plist' in skin and not self.is_plist_prop(prop, skin['plist']):
                        return False
        return flag

    # 判断锚点在中心且没有设置缩放
    def is_noscale_centeralign(self, node):
        x, y = self.get_scale(node)
        if float(x) != 1 or float(y) != 1:
            return False
        x, y = self.get_anchor(node)
        if float(x) != 0.5 or float(y) != 0.5:
            return False
        return True

    # 判断颜色是否一样
    @staticmethod
    def is_equal_color(c4b1, c4b2):
        if c4b1['a'] != c4b2['a']:
            return False
        if c4b1['r'] != c4b2['r']:
            return False
        if c4b1['g'] != c4b2['g']:
            return False
        if c4b1['b'] != c4b2['b']:
            return False
        return True

    # 设置颜色
    @staticmethod
    def set_prop_color(prop, color):
        prop.setAttribute('A', str(color['a']))
        prop.setAttribute('R', str(color['r']))
        prop.setAttribute('G', str(color['g']))
        prop.setAttribute('B', str(color['b']))

    # 设置颜色
    def set_color(self, node, color):
        for prop in node.childNodes:
            if prop.nodeName == 'CColor':
                self.set_prop_color(prop, color)
                break

    @staticmethod
    def get_color(node):
        for prop in node.childNodes:
            if prop.nodeName == 'CColor':
                return {
                    'a': int(prop.getAttribute('A')),
                    'r': int(prop.getAttribute('R')),
                    'g': int(prop.getAttribute('G')),
                    'b': int(prop.getAttribute('B')),
                }

    # 设置描边
    def set_outline(self, node, color):
        for prop in node.childNodes:
            if prop.nodeName == 'OutlineColor':
                self.set_prop_color(prop, color)
                break

    # 获取描边
    @staticmethod
    def get_outline(node):
        for prop in node.childNodes:
            if prop.nodeName == 'OutlineColor':
                return {
                    'a': int(prop.getAttribute('A')),
                    'r': int(prop.getAttribute('R')),
                    'g': int(prop.getAttribute('G')),
                    'b': int(prop.getAttribute('B')),
                }

    # 设置阴影
    def set_shadow(self, node, color):
        for prop in node.childNodes:
            if prop.nodeName == 'ShadowColor':
                self.set_prop_color(prop, color)
                break

    @staticmethod
    def set_position(node, x=None, y=None):
        for prop in node.childNodes:
            if prop.nodeName == 'Position':
                if x is not None:
                    prop.setAttribute('X', f2s(x))
                if y is not None:
                    prop.setAttribute('Y', f2s(y))
                break

    @staticmethod
    def add_position(node, x=None, y=None):
        for prop in node.childNodes:
            if prop.nodeName == 'Position':
                if x is not None:
                    _x = prop.getAttribute('X')
                    _x = float(_x) if _x else 0
                    prop.setAttribute('X', f2s(_x + x))
                if y is not None:
                    _y = prop.getAttribute('Y')
                    _y = float(_y) if _y else 0
                    prop.setAttribute('Y', f2s(_y + y))
                break

    @staticmethod
    def get_position(node):
        for prop in node.childNodes:
            if prop.nodeName == 'Position':
                x, y = prop.getAttribute('X'), prop.getAttribute('Y')
                return float(x) if x else 0, float(y) if y else 0

    @staticmethod
    def get_anchor(node):
        for prop in node.childNodes:
            if prop.nodeName == 'AnchorPoint':
                x, y = prop.getAttribute('ScaleX'), prop.getAttribute('ScaleY')
                return float(x) if x else 0.5, float(y) if y else 0.5

    @staticmethod
    def get_scale(node):
        for prop in node.childNodes:
            if prop.nodeName == 'Scale':
                x, y = prop.getAttribute('ScaleX'), prop.getAttribute('ScaleY')
                return float(x) if x else 1, float(y) if y else 1

    @staticmethod
    def set_size(node, width=None, height=None):
        for prop in node.childNodes:
            if prop.nodeName == 'Size':
                if width is not None:
                    prop.setAttribute('X', f2s(width))
                if height is not None:
                    prop.setAttribute('Y', f2s(height))
                break

    @staticmethod
    def get_size(node):
        for prop in node.childNodes:
            if prop.nodeName == 'Size':
                x, y = prop.getAttribute('X'), prop.getAttribute('Y')
                return float(x) if x else 0, float(y) if y else 0

    @staticmethod
    def get_font(node):
        for p in node.childNodes:
            if p.nodeName == kPropFont:
                return p.getAttribute('Path')

    @staticmethod
    def set_font(dom, node, font_name):
        prop, changed = None, False
        for p in node.childNodes:
            if p.nodeName == kPropFont:
                prop = p
                break
        if not prop:
            prop = dom.createElement(kPropFont)
            node.appendChild(dom.createTextNode('  '))
            node.appendChild(prop)
            node.appendChild(dom.createTextNode('\n                  '))
        if prop.getAttribute('Type') != 'Normal':
            prop.setAttribute('Type', 'Normal')
            changed = True
        if prop.getAttribute('Plist') != '':
            prop.setAttribute('Plist', '')
            changed = True
        if prop.getAttribute('Path') != font_name:
            prop.setAttribute('Path', font_name)
            changed = True
        return changed

    @staticmethod
    def remove_font(node):
        for prop in node.childNodes:
            if prop.nodeName == kPropFont:
                node.childNodes.remove(prop)
                return True
        return False

    # 设置plist
    @staticmethod
    def set_plist_prop(prop, plist):
        prop.setAttribute('Type', 'PlistSubImage')
        prop.setAttribute('Plist', plist)

    # 判断资源是否来自plist
    @staticmethod
    def is_plist_prop(prop, plist):
        if prop.getAttribute('Type') != 'PlistSubImage':
            return False
        if prop.getAttribute('Plist') != plist:
            return False
        return True

##############################################################################################
def batch_modify_button(csd_dir, tasks):
    maker = MakeCSD()
    for (par, _, files) in os.walk(csd_dir):
        for name in files:
            if not name.endswith('.csd'):
                continue
            f = os.path.join(par, name)
            print(f)
            buffer = maker.modify_dom_btn_skin(f, *tasks)
            if not buffer:
                continue
            with open(f, 'wb') as fp:
                fp.write(buffer[38:])  # 去除<?xml version="1.0" encoding="utf-8"?>
    print('batch_modify_button done')

def simple_modify_button(csd_dir):
    tasks = list()
    # tasks.append({
    #         'feature': {
    #             'skin': {
    #                 'normal': 'anniu_cheng.png',
    #                 # 'pressed': 'anniu_cheng.png',
    #                 # 'disabled': 'anniu_cheng.png',
    #                 'plist': 'pic/ui/gongyong_btn.plist'
    #             }
    #         },
    #         'new': {
    #             'skin': {
    #                 'normal': 'gongyong_anniu_1.png',
    #                 'pressed': 'gongyong_anniu_1.png',
    #                 'disabled': 'gongyong_anniu_3.png',
    #                 'plist': 'pic/ui/gongyong_btn.plist'
    #             },
    #             # 'size': {'width': 182, 'height': 62, 'offset': (0, 3), 'edge': (20, 20, 8, 8)},
    #             # 'title_color': {'a': 255, 'r': 255, 'g': 255, 'b': 255},
    #             'title_outline': {'a': 255, 'r': 97, 'g': 79, 'b': 32},
    #             # 'title_shadow': {'a': 255, 'r': 255, 'g': 255, 'b': 255},
    #         }
    #     }
    # )
    # tasks.append({
    #         'feature': {
    #             'skin': {
    #                 'normal': 'anniu_lv.png',
    #                 # 'pressed': 'anniu_lv.png',
    #                 # 'disabled': 'anniu_lv.png',
    #                 'plist': 'pic/ui/gongyong_btn.plist'
    #             }
    #         },
    #         'new': {
    #             'skin': {
    #                 'normal': 'gongyong_anniu_4.png',
    #                 'pressed': 'gongyong_anniu_4.png',
    #                 'disabled': 'gongyong_anniu_3.png',
    #                 'plist': 'pic/ui/gongyong_btn.plist'
    #             },
    #             # 'size': {'width': 182, 'height': 62, 'offset': (0, 3), 'edge': (20, 20, 8, 8)},
    #             # 'title_color': {'a': 255, 'r': 255, 'g': 255, 'b': 255},
    #             'title_outline': {'a': 255, 'r': 65, 'g': 90, 'b': 11},
    #             # 'title_shadow': {'a': 255, 'r': 255, 'g': 255, 'b': 255},
    #         }
    #     }
    # )
    # tasks.append({
    #         'feature': {
    #             'skin': {
    #                 'normal': 'anniu_lan.png',
    #                 # 'pressed': 'anniu_lan.png',
    #                 # 'disabled': 'anniu_lan.png',
    #                 'plist': 'pic/ui/gongyong_btn.plist'
    #             }
    #         },
    #         'new': {
    #             'skin': {
    #                 'normal': 'gongyong_anniu_5.png',
    #                 'pressed': 'gongyong_anniu_5.png',
    #                 'disabled': 'gongyong_anniu_3.png',
    #                 'plist': 'pic/ui/gongyong_btn.plist'
    #             },
    #             # 'size': {'width': 182, 'height': 62, 'offset': (0, 3), 'edge': (20, 20, 8, 8)},
    #             # 'title_color': {'a': 255, 'r': 255, 'g': 255, 'b': 255},
    #             'title_outline': {'a': 255, 'r': 8, 'g': 83, 'b': 81},
    #             # 'title_shadow': {'a': 255, 'r': 255, 'g': 255, 'b': 255},
    #         }
    #     }
    # )
    tasks.append({
        'feature': {
            'skin': {
                'normal': 'gongyong_anniu_1.png'
            }
        },
        'new': {
            'title_color': {'a': 255, 'r': 255, 'g': 240, 'b': 229},
            'title_outline': {'a': 255, 'r': 97, 'g': 59, 'b': 32},
        }
    })
    tasks.append({
        'feature': {
            'skin': {
                'normal': 'gongyong_anniu_4.png'
            }
        },
        'new': {
            'title_color': {'a': 255, 'r': 255, 'g': 240, 'b': 229},
            'title_outline': {'a': 255, 'r': 38, 'g': 92, 'b': 35},
        }
    })
    tasks.append({
        'feature': {
            'skin': {
                'normal': 'gongyong_anniu_5.png'
            }
        },
        'new': {
            'title_color': {'a': 255, 'r': 255, 'g': 240, 'b': 229},
            'title_outline': {'a': 255, 'r': 8, 'g': 83, 'b': 81},
        }
    })
    batch_modify_button(csd_dir, tasks)

def simple_modify_font(csd_dir):
    maker = MakeCSD()
    for (par, _, files) in os.walk(csd_dir):
        for name in files:
            if not name.endswith('.csd'):
                continue
            f = os.path.join(par, name)
            print(f)
            # buffer = maker.modify_dom_font(f, 'font/AdobeHeit.ttf')
            buffer = maker.modify_dom_font(f, 'font/fzwb.ttf', [kTypeButton])
            if not buffer:
                continue
            with open(f, 'wb') as fp:
                fp.write(buffer[38:])  # 去除<?xml version="1.0" encoding="utf-8"?>

def simple_modify_outline(csd_dir):
    maker = MakeCSD()
    for (par, _, files) in os.walk(csd_dir):
        for name in files:
            if not name.endswith('.csd'):
                continue
            f = os.path.join(par, name)
            # f = '/Users/joli/Work/LightPro/Client/CocosProject/cocosstudio/csb/Login/fenbao.csd'
            print(f)
            # buffer = maker.modify_dom_outline(f, *[{
            #     'old': {'a': 255, 'r': 8, 'g': 83, 'b': 81},
            #     'new': 'CLOSE'
            # }])
            buffer = maker.modify_dom_outline(f, *[{
                'old': {'a': 255, 'r': 8, 'g': 83, 'b': 81},
                'new': {'a': 255, 'r': 49, 'g': 113, 'b': 131},
                'user_ctype': kTypeButton
            }, {
                'old': {'a': 255, 'r': 97, 'g': 59, 'b': 32},
                'new': {'a': 255, 'r': 138, 'g': 97, 'b': 38},
                'user_ctype': kTypeButton
            }])
            if not buffer:
                continue
            with open(f, 'wb') as fp:
                fp.write(buffer[38:])  # 去除<?xml version="1.0" encoding="utf-8"?>

def simple_modify_textcolor(csd_dir):
    maker = MakeCSD()
    for (par, _, files) in os.walk(csd_dir):
        for name in files:
            if not name.endswith('.csd'):
                continue
            f = os.path.join(par, name)
            # f = '/Users/joli/Work/LightPro/Client/CocosProject/cocosstudio/csb/Login/fenbao.csd'
            print(f)
            buffer = maker.modify_dom_textcolor(f, *[
                # {
                #     'old': {'a': 255, 'r': 255, 'g': 240, 'b': 229},
                #     'new': {'a': 255, 'r': 255, 'g': 255, 'b': 255},
                #     'user_ctype': kTypeButton
                # }
                {
                    # 'old': {'a': 255, 'r': 109, 'g': 45, 'b': 6},
                    'old': {'a': 255, 'r': 74, 'g': 76, 'b': 7},
                    'new': {'a': 255, 'r': 74, 'g': 46, 'b': 7},
                }
            ])
            if not buffer:
                continue
            with open(f, 'wb') as fp:
                fp.write(buffer[38:])  # 去除<?xml version="1.0" encoding="utf-8"?>

def simple_modify_fontsize(csd_dir):
    maker = MakeCSD()
    for (par, _, files) in os.walk(csd_dir):
        for name in files:
            if not name.endswith('.csd'):
                continue
            f = os.path.join(par, name)
            # f = '/Users/joli/Work/LightPro/Client/CocosProject/cocosstudio/csb/Login/fenbao.csd'
            print(f)
            buffer = maker.modify_dom_fontsize(f, *[{
                'old': "24",
                'new': "28",
                'user_ctypes': [kTypeButton],
                'user_fonts': ['font/fzwb.ttf']
            }, {
                'old': "26",
                'new': "28",
                'user_ctypes': [kTypeButton],
                'user_fonts': ['font/fzwb.ttf']
            }])
            if not buffer:
                continue
            with open(f, 'wb') as fp:
                fp.write(buffer[38:])  # 去除<?xml version="1.0" encoding="utf-8"?>

def main():
    csd_dir = '/Users/joli/Work/LightPro/Client/CocosProject/cocosstudio/csb'
    # simple_modify_button(csd_dir)
    # simple_modify_font(csd_dir)
    # simple_modify_outline(csd_dir)
    simple_modify_textcolor(csd_dir)
    # simple_modify_fontsize(csd_dir)
    print("done")

if __name__ == '__main__':
    main()