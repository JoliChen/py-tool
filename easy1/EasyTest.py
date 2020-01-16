# -*- coding: UTF-8 -*-

import os
import shutil

def _test_ftp():
    package_path = '/Users/joli/Desktop/outputs/xcode/zipfile/201805151417_dada_sgwszj.zip'
    host = '10.16.254.16'
    port = 21
    timeout = 60
    username = 'ttans'
    password = 'ttans'
    ftp_path = 'ttans_bak/products/ios/' + os.path.split(package_path)[1]
    local_file = None
    ftp_client = None
    try:
        from ftplib import FTP
        ftp_client = FTP()  # 实例化FTP对象
        ftp_client.set_debuglevel(2)
        ftp_client.connect(host, port, timeout)
        ftp_client.login(username, password)  # 登录
        # print ftp_client.getwelcome()
        local_file = open(package_path, 'rb')
        ftp_client.storbinary('STOR ' + ftp_path, local_file)
    except:
        print('upload to ftp failed')
    finally:
        if ftp_client is not None:
            ftp_client.close()
        if local_file is not None:
            local_file.close()
    print('ftp://10.16.254.16/' + ftp_path)


def _test_messagebox(thread_name):
    print('thread_name=%s' % thread_name)
    import tkinter.messagebox
    tkinter.messagebox.showerror('打包错误', '请断开网络连接')

# def _test_thread():
#     from concurrent.futures import thread
#     thread.start_new_thread(lambda thread_name: _test_messagebox(thread_name), ("Thread-1", ))

def _auto_crop(image, background_color=None):
    # '''Intelligent automatic image cropping.
    #    This functions removes the usless "white" space around an image.
    #
    #    If the image has an alpha (tranparency) channel, it will be used
    #    to choose what to crop.
    #
    #    Otherwise, this function will try to find the most popular color
    #    on the edges of the image and consider this color "whitespace".
    #    (You can override this color with the backgroundColor parameter)
    #
    #    Input:
    #         image (a PIL Image object): The image to crop.
    #         backgroundColor (3 integers tuple): eg. (0,0,255)
    #              The color to consider "background to crop".
    #              If the image is transparent, this parameters will be ignored.
    #              If the image is not transparent and this parameter is not
    #              provided, it will be automatically calculated.
    #
    #    Output:
    #         a PIL Image object : The cropped image.
    # '''

    def _most_popular_edge_color(edge_img):
        # ''' Compute who's the most popular color on the edges of an image.
        #     (left,right,top,bottom)
        #
        #     Input:
        #         image: a PIL Image object
        #
        #     Ouput:
        #         The most popular color (A tuple of integers (R,G,B))
        # '''
        im = edge_img
        if im.mode != 'RGB':
            im = edge_img.convert("RGB")

        # Get pixels from the edges of the image:
        width, height = im.size
        left = im.crop((0, 1, 1, height - 1))
        right = im.crop((width - 1, 1, width, height - 1))
        top = im.crop((0, 0, width, 1))
        bottom = im.crop((0, height - 1, width, height))
        pixels = left.tostring() + right.tostring() + top.tostring() + bottom.tostring()

        # Compute who's the most popular RGB triplet
        counts = {}
        for i in range(0, len(pixels), 3):
            rgb = pixels[i] + pixels[i + 1] + pixels[i + 2]
            if rgb in counts:
                counts[rgb] += 1
            else:
                counts[rgb] = 1

                # Get the colour which is the most popular:
        most_popular_color = sorted([(count, rgba) for (rgba, count) in counts.items()], reverse=True)[0][1]
        return ord(most_popular_color[0]), ord(most_popular_color[1]), ord(most_popular_color[2])

    # bbox = None

    # If the image has an alpha (tranparency) layer, we use it to crop the image.
    # Otherwise, we look at the pixels around the image (top, left, bottom and right)
    # and use the most used color as the color to crop.

    # --- For transparent images -----------------------------------------------
    if 'A' in image.getbands():  # If the image has a transparency layer, use it.
        # This works for all modes which have transparency layer
        bbox = image.split()[list(image.getbands()).index('A')].getbbox()
    # --- For non-transparent images -------------------------------------------
    elif image.mode == 'RGB':
        if not background_color:
            background_color = _most_popular_edge_color(image)
        # Crop a non-transparent image.
        # .getbbox() always crops the black color.
        # So we need to substract the "background" color from our image.
        from PIL import Image
        bg = Image.new("RGB", image.size, background_color)
        from PIL import ImageChops
        diff = ImageChops.difference(image, bg)  # Substract background color from image
        bbox = diff.getbbox()  # Try to find the real bounding box of the image.
    else:
        raise NotImplementedError("Sorry, this function is not implemented yet for images in mode '%s'." % image.mode)

    if bbox:
        image = image.crop(bbox)
    return image

def _test_pixcel():
    from PIL import Image
    logo_image = Image.open('/Users/joli/Desktop/test/splash/真·无双LOGO.png')
    bbox = logo_image.split()[list(logo_image.getbands()).index('A')].getbbox()
    logo_image = logo_image.crop(bbox)
    logo_size = logo_image.size

    bg_image = Image.new('RGBA', (940, 640), (0, 0, 0))
    bg_size = bg_image.size

    x = int((bg_size[0] - logo_size[0]) * 0.5)
    y = int((bg_size[1] - logo_size[1]) * 0.5)
    box = (x, y, x+logo_size[0], y+logo_size[1])
    bg_image.paste(logo_image, box, logo_image.split()[3])

    # bg_image.show()
    bg_image.save('/Users/joli/Desktop/test/splash/bg.png')

def _test_uuid():
    import uuid
    print(uuid.uuid1())
    from machine.Network import JNetwork
    JNetwork.set_random_mac_address('6666', 'en0')

def _strong_assignment(arr, pos, obj):
    num = pos - len(arr)+1
    for i in range(num):
        arr.append('')
    arr[pos] = obj

def _test_make_assets():
    from Dev2 import MakeAssets
    MakeAssets.main(['MakeAssets', '/Users/joli/proj/client_sgwww/trunk/project/xcode', 'quick_xytx', 'xytx'])

def _parse_effect_data():
    import json
    flashxdir = '/Users/joli/proj/client_hssg/trunk/runtime-src/proj.assets/kato_orig/res/flashEff'
    json_file = os.path.join(flashxdir, 'all_flashx')
    with open(json_file, "rb") as f:
        b = f.read()
    data = json.loads(b.decode('utf-8'))
    print(len(data))
    animate_data_map = data[0]
    sheet_frame_list = data[1]
    sheet_name_dict = data[2]
    print(len(animate_data_map), len(sheet_frame_list), len(sheet_name_dict))

    ani_sheet_counter = {}
    sheet_use_counter = {}
    for ani_id in animate_data_map:
        animate = animate_data_map[ani_id]
        ele_map = animate[1]
        ani_counter = {}
        for ele_id in ele_map:
            element = ele_map[ele_id]
            sheet_id = element[3]
            # print(sheet_id)
            ani_counter[sheet_id] = True
        ani_counter = list(ani_counter.keys())
        # print('animate:', ani_id, ani_counter)
        for sheet_id in ani_counter:
            if sheet_id in sheet_use_counter:
                sheet_use_counter[sheet_id] += 1
            else:
                sheet_use_counter[sheet_id] = 1
        ani_sheet_counter[ani_id] = ani_counter

    print('sheet_use_counter:', len(sheet_use_counter))
    used_sheet_list = list(sheet_use_counter.keys())
    used_sheet_list.sort(key=lambda k: sheet_use_counter[k], reverse=True)

    use_once_list = []
    use_many_dict = {}
    for sheet_id in used_sheet_list:
        use_times = sheet_use_counter[sheet_id]
        # print(sheet_id, use_times)
        if 1 == use_times:
            use_once_list.append(sheet_id)
        else:
            use_many_dict[sheet_id] = use_times
    print('use_once:', len(use_once_list))
    print('use_many:', len(use_many_dict))
    total_bytes = 0
    for sheet_id in use_many_dict:
        # print(use_many_dict[sheet_id], sheet_name_dict[sheet_id])
        img_time = use_many_dict[sheet_id]
        img_name = sheet_name_dict[sheet_id] + '.png'
        img_path = os.path.join(flashxdir, 'skillEff', img_name)
        img_size = 0
        if os.path.exists(img_path):
            img_size = os.path.getsize(img_path)
            shutil.copy(img_path, os.path.join('/Users/joli/Desktop/test/swf/shared', img_name))
        else:
            img_path = os.path.join(flashxdir, 'UIEff', img_name)
            if os.path.exists(img_path):
                img_size = os.path.getsize(img_path)
                shutil.copy(img_path, os.path.join('/Users/joli/Desktop/test/swf/shared', img_name))
            else:
                print('file not exists:', img_path)
        print(img_name, img_time, img_size)
        img_size = img_size * img_time
        total_bytes += img_size
    print(total_bytes / float(1024 * 1024))

    # def is_share_sheet(ani_id, sheet_id):
    #     for ani_id_2 in ani_sheet_counter:
    #         if ani_id == ani_id_2:
    #             continue
    #         ani_counter_2 = ani_sheet_counter[ani_id_2]
    #         for sheet_id_2 in ani_counter_2:
    #             if sheet_id == sheet_id_2:
    #                 return True
    #
    # shard_sheet_list = []
    # for ani_id in ani_sheet_counter:
    #     ani_counter = ani_sheet_counter[ani_id]
    #
    #     def is_share_group(ani_id, ani_group):
    #         for ani_id_1 in ani_sheet_counter:
    #             if ani_id_1 == ani_id:
    #                 continue
    #             ani_counter = ani_sheet_counter[ani_id_1]
    #             if len(ani_group) != len(ani_counter):
    #                 continue
    #             is_all_exists = True
    #             for sheet_id in ani_group:
    #                 if sheet_id not in ani_counter:
    #                     is_all_exists = False
    #                     break
    #             if is_all_exists:
    #                 return True
    #
    #     def is_record_sheet(ani_id, ani_counter, shard_group_list):
    #         for group in shard_group_list:
    #             if len(group) != len(ani_counter):
    #                 continue
    #             is_all_exists = True
    #             for sheet_id in group:
    #                 if sheet_id not in ani_counter:
    #                     is_all_exists = False
    #                     break
    #             if is_all_exists:
    #                 return True
    #
    #     shard_group_list = []
    #     for ani_id in ani_sheet_counter:
    #         ani_counter = ani_sheet_counter[ani_id]
    #         if is_share_group(ani_id, ani_counter):
    #             if not is_record_sheet(ani_id, ani_counter, shard_group_list):
    #                 # print(ani_counter)
    #                 shard_group_list.append(ani_counter)
    #     print('shard_group_list:', len(shard_group_list))
    #     for sheet_id in ani_counter:
    #         if is_share_sheet(ani_id, sheet_id):
    #             if sheet_id not in shard_sheet_list:
    #                 shard_sheet_list.append(sheet_id)
    # shard_sheet_list.sort()
    # print('shard_sheets:', len(shard_sheet_list))

# def test_excel():
#     def read_excel(excel_path):
#         import xlrd
#         book = xlrd.open_workbook(excel_path)
#         sheet_data_dict = {}
#         for sheet_name in book.sheet_names():
#             sheet = book.sheet_by_name(sheet_name)
#             matrix = []
#             for row in range(sheet.nrows):
#                 row_data = []
#                 for col in range(sheet.ncols):
#                     row_data.append(sheet.cell_value(row, col))
#                 matrix.append(row_data)
#             sheet_data_dict[sheet_name] = matrix
#         return sheet_data_dict
#
#     excel_1 = read_excel('/Users/joli/Downloads/火舞-2018-07-01-2018-07-31.xls')
#     excel_2 = read_excel('/Users/joli/Downloads/火舞 卧龙三国7月数据.xlsx')
#     print(excel_1)
#     print(excel_2)

def test_load_jstm():
    import threading
    import requests
    # with open('/Users/joli/Desktop/test/web/skill.txt', 'rb') as f:
    #     b = f.read()
    # data = json.loads(b.decode('utf-8'))
    # nums = 0
    # rurl = 'https://jstmcdn.playtai.com/jstm/e/resource/game/skill/effect'
    # wurl = '/Users/joli/Desktop/test/web/effect'
    # for item in data:
    #     for sk_sub in item['skillSubLevel']:
    #         for buff in sk_sub['buff']:
    #             effect_id = buff['effectId']
    #             nums += 1
    #             png = '/%d.png' % effect_id
    #             txt = '/%d.png' % effect_id
    #             response = requests.get(rurl + png)
    #             if response:
    #                 print(nums, 'load effect:', effect_id)
    #                 with open (wurl + png,'wb') as f:
    #                     f.write(response.content)
    #             else:
    #                 print(nums, 'not found', effect_id)
    #             # response = requests.get(rurl + txt)
    #             # with open(wurl + txt, 'wb') as f:
    #             #     f.write(response.content)

    r_url = 'https://jstmcdn.playtai.com/jstm/e/resource/game/skill/effect'
    w_url = '/Users/joli/Desktop/test/web/effect'

    def load_func(start, length):
        for eid in range(start, start+length, 1):
            png = '/%d.png' % eid
            try:
                response = requests.get(r_url + png)
                if response:
                    print(eid, 'load success')
                    with open(w_url + png, 'wb') as f:
                        f.write(response.content)
                    cfg = '/%d.json' % eid
                    response = requests.get(r_url + cfg)
                    if response:
                        with open(w_url + cfg, 'wb') as f:
                            f.write(response.content)
                else:
                    print(eid, 'load failed')
            except:
                pass

    t_num = 10000000
    t_chn = 10
    t_arr = []
    for i in range(t_chn):
        t = threading.Thread(target=load_func, args=(i * t_num / t_chn, t_num / t_chn), name=('load%d' % i))
        t_arr.append(t)
        t.start()
    for t in t_arr:
        t.join()
    print('done')


def easy_test():
    # ba = bytearray(5)
    # test_load_jstm()
    pass