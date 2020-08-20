# -*- coding: utf-8 -*-
# @Time    : 2019/5/22 9:12 PM
# @Author  : Joli
# @Email   : 99755349@qq.com

import os
import pickle
import shutil

from PIL import Image, ImageOps
from argparse import ArgumentParser
from io import BytesIO

import unitypack
from unitypack.asset import Asset
from unitypack.export import OBJMesh
from unitypack.utils import extract_audioclip_samples
from unitypack.engine.texture import TextureFormat

# 从路径里分离出文件名（不包含后缀）
def split_filename(filepath):
	return filepath[filepath.rfind(os.sep)+1: filepath.rfind('.')]

# 另外的兄弟路径
def other_filepath(filepath):
	other = filepath
	while True:
		parts = os.path.splitext(other)
		other = parts[0] + '-' + parts[1]
		if not os.path.isfile(other):
			break
	print('Rename %s -> %s' % (filepath, other))
	return other

# 合并rgb和alpha通道，生成新的图像对象。
def merge_rgba(rgbpath, alphapath, alphaindex=-1):
	r, g, b = Image.open(rgbpath).split()
	acolors = Image.open(alphapath).split()
	a = acolors[alphaindex]
	return Image.merge('RGBA', (r, g, b, a))

class PkmUtil:
	MALI_BIN = "/Users/joli/Priv/hack/mali/v4.3.0.b81c088_MacOSX_x64/bin"
	ETCPACK = os.path.join(MALI_BIN, 'etcpack')

	FORMAT_MAP = dict()
	FORMAT_MAP[TextureFormat.ETC_RGB4] = 0
	FORMAT_MAP[TextureFormat.ETC2_RGB] = 1
	FORMAT_MAP[TextureFormat.ETC2_RGBA8] = 3
	FORMAT_MAP[TextureFormat.ETC2_RGBA1] = 4
	FORMAT_MAP[TextureFormat.EAC_R] = 5
	FORMAT_MAP[TextureFormat.EAC_RG] = 6
	FORMAT_MAP[TextureFormat.EAC_R_SIGNED] = 7
	FORMAT_MAP[TextureFormat.EAC_RG_SIGNED] = 8

	def __init__(self):
		pass

	def gen_pkm_buffer(self, texture):
		buffer = self.gen_pkm_header(texture.format, texture.width, texture.height)
		buffer += texture.image_data
		return buffer

	def gen_pkm_header(self, tex_fmt, width, height):
		pkm_fmt = self.FORMAT_MAP.setdefault(tex_fmt, 0)
		if pkm_fmt > 0:
			version = b"20"
		else:
			version = b"10"
		magic = b"\x50\x4B\x4D\x20"
		fbits = pkm_fmt.to_bytes(2, byteorder="big")
		wbits = width.to_bytes(2, byteorder="big")
		hbits = height.to_bytes(2, byteorder="big")
		buffer = magic + version + fbits + wbits + hbits + wbits + hbits
		return buffer

	def tex2image(self, texture, tmpdir, needflip=True):
		if not os.path.isdir(tmpdir):
			os.makedirs(tmpdir)
		pkmpath = os.path.join(tmpdir, texture.name + ".pkm")
		with open(pkmpath, 'wb') as fp:
			buffer = self.gen_pkm_buffer(texture)
			fp.write(buffer)
		pimage = self._sh_pkm2pimage(pkmpath, tmpdir, needflip)
		os.remove(pkmpath)
		return pimage

	def pkm2png(self, srcpath, pngpath, needflip=True, tmpdir=None):
		pngdir = os.path.dirname(pngpath)
		if not os.path.isdir(pngdir):
			os.makedirs(pngdir)
		if not srcpath.endswith('.pkm'):  # copy .pvr to .pkm
			pkmpath = os.path.join(pngdir, split_filename(pngpath) + '.pkm')
			removepkm = True
			shutil.copyfile(srcpath, pkmpath)
		else:
			pkmpath = srcpath
			removepkm = False
		if tmpdir:
			if not os.path.isdir(tmpdir):
				os.makedirs(tmpdir)
		else:
			tmpdir = pngdir
		pimage = self._sh_pkm2pimage(pkmpath, tmpdir, needflip)
		if removepkm:
			os.remove(pkmpath)  # 删除临时文件
		if pimage:
			pimage.save(pngpath)
			return pngpath

	def topng(self, pkmpath, pngdir, needflip=True, subfix='', tmpdir=None):
		pngpath = os.path.join(pngdir, split_filename(pkmpath) + subfix + '.png')
		return self.pkm2png(pkmpath, pngpath, needflip, tmpdir)

	def _sh_pkm2ppm(self, pkmpath, dstdir, tex_fmt=None):
		if tex_fmt == TextureFormat.ETC2_RGBA8:
			ppm_fmt = 'RGBA8'
		elif tex_fmt == TextureFormat.ETC2_RGBA1:
			ppm_fmt = 'RGBA1'
		else:
			ppm_fmt = 'RGB'
		# cmd = f'"{etcpack}" "{pkmpath}" "{dstdir}" -s slow -f RGBA -c etc2 -e perceptual -v -progress'
		# cmd = f'"{etcpack}" "{pkmpath}" "{dstdir}" -s slow -f RGBA -c etc2 -e perceptual'
		# cmd = f'"{etcpack}" "{pkmpath}" "{dstdir}" -s slow -f RGBA -c etc2'
		cmd = '"%s" "%s" "%s" -s slow -f %s' % (self.ETCPACK, pkmpath, dstdir, ppm_fmt)
		# print(cmd)
		return os.system(cmd) == 0

	def _sh_pkm2pimage(self, pkmpath, tmpdir, needflip=True):
		if not self._sh_pkm2ppm(pkmpath, tmpdir):
			return
		ppmpath = os.path.join(tmpdir, split_filename(pkmpath) + ".ppm")
		if not os.path.isfile(ppmpath):
			print('can not found', ppmpath)
			return
		pimage = Image.open(ppmpath)
		if needflip:
			# pimage = image.transpose(Image.ROTATE_180)
			# pimage = image.transpose(Image.FLIP_LEFT_RIGHT)  # 左右对换
			pimage = ImageOps.flip(pimage)
		os.remove(ppmpath)
		return pimage

class UnityExtract:
	FORMAT_ARGS = {
		"audio": "AudioClip",
		"fonts": "Font",
		"images": "Texture2D",
		"models": "Mesh",
		"shaders": "Shader",
		"text": "TextAsset",
		"video": "MovieTexture",
	}

	def __init__(self, args, tmpdir):
		if isinstance(args, str):
			self.parse_args(args)
		else:
			self.args = args
		self.tempdir = tmpdir
		self.pkmutil = PkmUtil()

	def parse_args(self, args):
		p = ArgumentParser()
		p.add_argument("files", nargs="+")
		p.add_argument("--all", action="store_true", help="Extract all supported types")
		for arg, clsname in self.FORMAT_ARGS.items():
			p.add_argument("--" + arg, action="store_true", help="Extract %s" % clsname)
		p.add_argument("-o", "--outdir", nargs="?", default="", help="Output directory")
		p.add_argument("--as-asset", action="store_true", help="Force open files as Asset format")
		p.add_argument("--filter", nargs="*", help="Filter extraction for a specific name")
		p.add_argument("-n", "--dry-run", action="store_true", help="Skip writing files")
		self.args = p.parse_args(args)

	def run(self):
		self.handle_formats = []
		for a, classname in self.FORMAT_ARGS.items():
			if self.args.all or getattr(self.args, a):
				self.handle_formats.append(classname)
		if self.args.files:
			for file in self.args.files:
				self.try_extract_from_file(file)
		if self.args.indir:
			for root, _, files in os.walk(self.args.indir):
				for fn in files:
					file = os.path.join(root, fn)
					self.try_extract_from_file(file)
		return 0

	def get_output_path(self, filename):
		basedir = os.path.abspath(self.curdir)
		outpath = os.path.join(basedir, filename)
		if os.path.isfile(outpath):
			outpath = other_filepath(outpath)
		dirs = os.path.dirname(outpath)
		if not os.path.isdir(dirs):
			os.makedirs(dirs)
		return outpath

	def match_filters(self, name):
		for f in self.args.filter:
			if f.lower() in name:
				return True
		return False

	def write_to_file(self, filename, contents, mode="w"):
		path = self.get_output_path(filename)
		if self.args.dry_run:
			print("Would write %i bytes to %r" % (len(contents), path))
			return
		with open(path, mode) as f:
			written = f.write(contents)
		print("Written %i bytes to %r" % (written, path))

	def try_extract_from_file(self, file):
		self.curdir = os.path.join(self.args.outdir, split_filename(file))
		if self.args.as_asset or file.endswith(".assets"):
			with open(file, "rb") as fp:
				self.try_extract_asset(fp)
			return
		with open(file, "rb") as fp:
			self.try_extract_bundle(fp)

	def try_extract_bundle(self, fp):
		try:
			bundle = unitypack.load(fp)
		except Exception as e:
			print(e)
			return
		for asset in bundle.assets:
			self.try_extract_items(asset)

	def try_extract_asset(self, fp):
		try:
			asset = Asset.from_file(fp)
		except Exception as e:
			print(e)
			return
		self.try_extract_items(asset)

	def try_extract_items(self, asset):
		try:
			items = asset.objects.items()
		except Exception as e:
			print(e)
			return
		for id, obj in items:
			try:
				self._output_item(obj)
			# except NotImplementedError as e:
			# 	print(e)
			except KeyError as e:
				print('KeyError', e)
			except Exception as e:
				print(e)

	def _output_item(self, obj):
		if obj.type not in self.handle_formats:
			print('uncare obj.type', obj.type)
			return
		d = obj.read()
		if self.args.filter and not self.match_filters(d.name.lower()):
			return

		if obj.type == "AudioClip":
			samples = extract_audioclip_samples(d)
			for filename, sample in samples.items():
				self.write_to_file(filename, sample, mode="wb")

		elif obj.type == "MovieTexture":
			filename = d.name + ".ogv"
			self.write_to_file(filename, d.movie_data, mode="wb")

		elif obj.type == "Shader":
			self.write_to_file(d.name + ".cg", d.script)

		elif obj.type == "Mesh":
			try:
				mesh_data = OBJMesh(d).export()
				self.write_to_file(d.name + ".obj", mesh_data, mode="w")
			except NotImplementedError as e:
				print("WARNING: Could not extract %r (%s)" % (d, e))
				mesh_data = pickle.dumps(d._obj)
				self.write_to_file(d.name + ".Mesh.pickle", mesh_data, mode="wb")

		elif obj.type == "Font":
			self.write_to_file(d.name + ".ttf", d.data, mode="wb")

		elif obj.type == "TextAsset":
			if isinstance(d.script, bytes):
				filename, mode = d.name + ".bin", "wb"
			else:
				filename, mode = d.name + ".txt", "w"
			self.write_to_file(filename, d.script, mode=mode)

		elif obj.type == "Texture2D":
			self._output_texture(d)

	def _output_texture(self, d):
		filename = d.name + ".png"
		try:
			image = d.image
		except NotImplementedError:
			image = self.pkmutil.tex2image(d, self.tempdir, needflip=False)
		if image is None:
			# print("WARNING: %s is an empty image" % filename)
			print("WARNING: Texture format:%s not implemented. Skipping %r." % (d.format, filename))
			return
		# print("Decoding %r" % d)
		# Texture2D objects are flipped
		img = ImageOps.flip(image)
		# PIL has no method to write to a string :/
		output = BytesIO()
		img.save(output, format="png")
		self.write_to_file(filename, output.getvalue(), mode="wb")

class UEArguments:
	def __init__(self, srcdir, dstdir):
		self.files = None
		self.indir = srcdir
		self.outdir = dstdir
		self.all = True
		self.as_asset = False
		self.dry_run = False
		self.filter = None

def sh_unityfs(srcdir, dstdir, tmpdir=None):
	args = UEArguments(srcdir, dstdir)
	app = UnityExtract(args, tmpdir or dstdir)
	app.run()