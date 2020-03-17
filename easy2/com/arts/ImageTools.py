from PIL import Image

# 合并颜色通道和透明通道，生成新的图像对象。
def merge_rgb_alpha(rgb_file, alpha_file):
    rgba = Image.open(rgb_file).convert('RGBA')
    a = Image.open(alpha_file)
    rgba.putalpha(a.convert('L'))
    return rgba