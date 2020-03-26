# import struct
# import io
# from itertools import count
# from PIL import Image, ImageDraw
#
#
# def _pack(data):
#     return struct.pack('<' + ('B' * len(data)), data)
#
#
# def _unpack(data):
#     return struct.unpack('<' + ('B' * len(data)), data)
#
#
# def pkm2png(gen, data):
#     """Convert a PKM file to a PNG image.
#     The file data is unpacked as individual bytes in a tuple. An empty image
#     is then created and the unpacked tuple is looped over with every four
#     bytes being placed in a four-item tuple and appended to a list.
#     An empty PNG is created with the game generation located as the 'R'
#     value of the first pixel. This set of four bytes functions as the
#     header, carrying any extra data.
#     The list of tuples is then looped over, using each tuple as the fill
#     value for a pixel (RGBA being four 8-bit numbers).
#     Keyword arguments:
#     gen (int) -- the file's game generation
#     data (string) -- the file data as a bytestring
#     """
#
#     length = len(data)
#     if length % 4 != 0:
#         raise ValueError('the pkm data supplied is incomplete')
#     # The first pixel is always the header, so we need to add one to the
#     # terminator.
#     terminator = int((length / 4) + 1)
#
#     data = _unpack(data)
#
#     # a list of 4-item tuples representing pixels
#     pixels = list()
#
#     # Header format:
#     # R value: game generation
#     # G value: terminator pixel
#     # B value: unused
#     # A value: unused
#     pixels.append((gen, terminator, 0, 0))
#
#     for i in count(start=0, step=4):
#         if i >= length:
#             break
#         pixel = (data[i], data[i + 1], data[i + 2], data[i + 3])
#         pixels.append(pixel)
#
#     width = 10
#     height = 6
#     size = (width, height)
#
#     # the PNG should default all-white
#     color = (0, 0, 0, 0)
#
#     imgobj = Image.new('RGBA', size, color)
#     drawobj = ImageDraw.Draw(imgobj)
#
#     xpos = 0
#     ypos = 0
#
#     for pixel in pixels:
#         drawobj.point((xpos, ypos), fill=pixel)
#
#         # advance xpos but make sure it stays between 0 and width
#         xpos = (xpos + 1) % width
#         # if it's starting a new row, advance ypos
#         if xpos == 0:
#             ypos += 1
#
#     # PIL's Image module requires the data to be a file buffer in order
#     # to save. It's a complicated library, but image manipulation is a
#     # complicated topic!
#
#     imgbuffer = io.BytesIO()
#     imgobj.save(imgbuffer, format='PNG')
#
#     # grab that data back out of the buffer
#     imgdata = imgbuffer.getvalue()
#
#     imgbuffer.close()
#
#     return imgdata
#
#
# def png2pkm(data):
#     """Convert a PNG image to a PKM file.
#     The PIL.Image module contains a useful method `getdata()` which returns
#     a sequence object containing each pixel of the image as a tuple of pixel
#     values (in our case, the RGBA values). What this function does is calls
#     that method, flattens the returned object into a list, loops over
#     the list, and appends each pixel value to the end of an empty PKM file.
#     Keyword arguments:
#     data (string) -- the file data as a bytestring
#     """
#     # PIL's Image module requires the data to be a file buffer in order
#     # to open.
#     imgbuffer = io.BytesIO()
#     imgbuffer.write(data)
#     # make sure you're at the beginning of the buffer
#     imgbuffer.seek(0)
#
#     imgobj = Image.open(imgbuffer)
#     pixels = list(imgobj.getdata())
#
#     imgbuffer.close()
#
#     # The first pixel is header information, and the 'R' value of that
#     # header is the file's game generation.
#     generation = pixels[0][0]
#     # The 'G' value is the last pixel containing PKM data.
#     terminator = pixels[0][1]
#
#     bytedata = ''
#     for pixel in pixels[1:terminator]:
#         bytedata += struct.pack('BBBB', *pixel)
#     return set(generation, bytedata)

# *************************************** github 上 pkm2png 脚本亲测不可用 ***************************************** #


# PKM格式的图片，用UItraEdit打开查看魔数是 {PMK 10}
# https://developer.arm.com/tools-and-software/graphics-and-gaming/mali-texture-compression-tool
# 1、下载mali显卡工具包
# 2、cd \Mali Developer Tools\Mali Texture Compression Tool\bin
# 3、etcpack {your.pkm} {your.png} -ext PNG。
import os
import shutil
from PIL import Image

malibin = '/Users/joli/Priv/hack/mali/v4.3.0.b81c088_MacOSX_x64/bin'
etcpack = os.path.join(malibin, 'etcpack')

def pkm2png(src, dst_dir, transpose=False, subfix=''):
    rename_src = None
    src_name = src[src.rfind(os.sep)+1: src.rfind('.')]
    # print(src_name)
    if not src.endswith('.pkm'):
        rename_src = os.path.join(dst_dir, src_name + '.pkm')
        # print(rename_src)
        shutil.copyfile(src, rename_src)
        src = rename_src
    pkm2ppm(src, dst_dir)  # 先转成 .ppm 文件
    if rename_src and os.path.isfile(rename_src):
        os.remove(rename_src)
    ppm_path = os.path.join(dst_dir, src_name + '.ppm')
    if os.path.isfile(ppm_path):
        image = Image.open(ppm_path)
        if transpose:
            image = image.transpose(Image.ROTATE_180)
            image = image.transpose(Image.FLIP_LEFT_RIGHT)  # 左右对换
        image.save(os.path.join(dst_dir, src_name + subfix + '.png'), format='png')
        os.remove(ppm_path)

def pkm2ppm(src, dst_dir):
    # cmd = f'"{etcpack}" "{src}" "{dst}" -s slow -f RGBA -c etc2 -e perceptual -v -progress'
    # cmd = f'"{etcpack}" "{src}" "{dst}" -s slow -f RGBA -c etc2 -e perceptual'
    # cmd = f'"{etcpack}" "{src}" "{dst}" -s slow -f RGBA -c etc2'
    cmd = f'"{etcpack}" "{src}" "{dst_dir}" -s slow'
    # print(cmd)
    os.system(cmd)