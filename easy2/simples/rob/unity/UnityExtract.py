import pickle
import unitypack
import fsb5
from unitypack import export
from unitypack.engine.texture import TextureFormat
from PIL import Image
import os

ETC_SERIES = (
	TextureFormat.ETC_RGB4,
	TextureFormat.ETC2_RGB,
	TextureFormat.ETC2_RGBA8,
	TextureFormat.ETC2_RGBA1,
	TextureFormat.EAC_R,
	TextureFormat.EAC_RG,
	TextureFormat.EAC_R_SIGNED,
	TextureFormat.EAC_RG_SIGNED,
)

ETCPACK = "/Users/joli/source/mac/app/hack/MTCT/bin/etcpack"

def save_text(filename, dirpath, buffer, mode="wb", encoding="utf-8"):
	if not os.path.isdir(dirpath):
		os.makedirs(dirpath)
	filepath = os.path.join(dirpath, filename)
	with open(filepath, mode=mode, encoding=encoding) as fp:
		fp.write(buffer)
	return filepath

def save_binary(filename, dirpath, buffer, mode="wb"):
	if not os.path.isdir(dirpath):
		os.makedirs(dirpath)
	filepath = os.path.join(dirpath, filename)
	with open(filepath, mode=mode) as fp:
		fp.write(buffer)
	return filepath

def read_samples_from_fsb(fsb):
	for sample in fsb.samples:
		try:
			yield sample.name, fsb.rebuild_sample(sample)
		except ValueError as e:
			print('FAILED to extract %r: %s' % (sample.name, e))

def to_pkm_format(tformat):
	if tformat == TextureFormat.ETC_RGB4:
		pkm_fmt = 0
	elif tformat == TextureFormat.ETC2_RGB:
		pkm_fmt = 1
	elif tformat == TextureFormat.ETC2_RGBA8:
		pkm_fmt = 3
	elif tformat == TextureFormat.ETC2_RGBA1:
		pkm_fmt = 4
	elif tformat == TextureFormat.EAC_R:
		pkm_fmt = 5
	elif tformat == TextureFormat.EAC_RG:
		pkm_fmt = 6
	elif tformat == TextureFormat.EAC_R_SIGNED:
		pkm_fmt = 7
	elif tformat == TextureFormat.EAC_RG_SIGNED:
		pkm_fmt = 8
	else:
		pkm_fmt = 0
	return pkm_fmt

def build_pkm_header(width, height, tformat):
	magic = b"\x50\x4B\x4D\x20"
	pkm_fmt = to_pkm_format(tformat)
	if pkm_fmt == 0:
		version = b"10"
	else:
		version = b"20"
	f_bytes = pkm_fmt.to_bytes(2, byteorder="big")
	w_bytes = width.to_bytes(2, byteorder="big")
	h_bytes = height.to_bytes(2, byteorder="big")
	buffer = (magic + version + f_bytes + w_bytes + h_bytes + w_bytes + h_bytes)
	return buffer

def extract_asset_item(pid, obj, dist):
	data = obj.read()
	if obj.type == "AudioClip":
		print(obj.type, data.name)
		bindata = data.data
		while bindata:
			fsb = fsb5.load(bindata)
			ext = fsb.get_sample_extension()
			bindata = bindata[fsb.raw_size:]
			for filename, buffer in read_samples_from_fsb(fsb):
				filename = data.name + "--" + filename + '.' + ext
				save_text(filename, dist, buffer)

	elif obj.type == "Texture2D":
		print(obj.type, data.name, "[" + str(data.format) + "]")
		filename = data.name + ".png"
		if data.format in ETC_SERIES:
			bindata = build_pkm_header(data.width, data.height, data.format) + data.image_data
			pkmname = data.name + ".pkm"
			pkmpath = os.path.join(dist, pkmname)
			save_binary(pkmname, dist, bindata)
			if os.path.isfile(pkmpath):
				os.system("%s %s %s" % (ETCPACK, pkmpath, dist))
				os.remove(pkmpath)
			ppmpath = os.path.join(dist, data.name + ".ppm")
			if os.path.isfile(ppmpath):
				image = Image.open(ppmpath)
				os.remove(ppmpath)
		else:
			image = data.image
		if not image:
			print("WARNING: %s is an empty image" % filename)
			return
		image = image.transpose(Image.ROTATE_180)
		image = image.transpose(Image.FLIP_LEFT_RIGHT)  # 左右对换
		if not os.path.isdir(dist):
			os.makedirs(dist)
		image.save(os.path.join(dist, filename), format='png')

	elif obj.type == "MovieTexture":
		print(obj.type, data.name)
		filename = data.name + ".ogv"
		save_binary(filename, dist, data.movie_data)

	# elif obj.type=="Shader":
	# 	print(obj.type,":",data.name)
	# 	filename=data.name+".cg"
	# 	putFile(filename,savepath,data.script)

	elif obj.type == "Mesh":
		print(obj.type, ":", data.name)
		try:
			meshdata = unitypack.export.OBJMesh(data).export()
			filename = data.name + ".obj"
			save_binary(filename, dist, meshdata)
		except NotImplementedError as e:
			print("WARNING: Could not extract %r (%s)" % (data, e))
			meshdata = pickle.dumps(data._obj)
			filename = data.name + ".Mesh.pickle"
			save_binary(filename, dist, meshdata)

	elif obj.type == "Font":
		print(obj.type, ":", data.name)
		filename = data.name + ".ttf"
		save_binary(filename, dist, data.data)

	elif obj.type == "TextAsset":
		print(obj.type, ":", data.name)
		filename = data.name
		if isinstance(data.script, bytes):
			save_binary(filename, dist, data.script, mode="wb")
		else:
			save_text(filename, dist, data.script, mode="w", encoding="utf-8")

def unityfs(fs, outdir):
	dist = os.path.join(outdir, os.path.basename(fs))
	with open(fs, 'rb') as fp:
		try:
			bundle = unitypack.load(fp)
		except Exception as e:
			print(e)
			return
		for asset in bundle.assets:
			try:
				assetobjs = asset.objects.items()
			except Exception as e:
				print(e)
				continue
			for pid, obj in assetobjs:
				try:
					extract_asset_item(pid, obj, dist)
				except Exception as e:
					print(e)
					continue