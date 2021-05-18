# -*- coding: utf-8 -*-
# @Time    : 2019/5/5 7:10 PM
# @Author  : Joli
# @Email   : 99755349@qq.com
import os
import shutil
import time

from jonlin.utils import FS, Collect, Log, Bit

log = Log.Logger(__file__)

def test_lupa():
    import lupa
    print(lupa.version)
    file = '/Users/joli/proj/sdk_uzone/trunk/projects/luandou/runtime/src/csb/Activity/acLimintTimeHero.lua'
    text = FS.read_text(file)
    lua = lupa.LuaRuntime()
    ast = lua.compile(text)
    print(ast)

def test_ttf2xml():
    from fontTools.ttLib import TTFont
    font = TTFont('/Users/joli/Desktop/test/swf/premuiltalpha/AdobeHeit.ttf')
    font.saveXML('/Users/joli/Desktop/test/font/AdobeHeit.xml')
    font.close()

def test_batch_refactor_xcplist():
    import biplist

    # 重构plist
    def _refactor_xcode_plist(p):
        print('refactor:', p)
        plist = biplist.readPlist(p)
        # print(plist)
        Collect.safe_pop(plist, 'CFBundleIcons')
        Collect.safe_pop(plist, 'CFBundleIcons~ipad')
        Collect.safe_pop(plist, 'CFBundleSignature')
        Collect.safe_pop(plist, 'LSApplicationCategoryType')
        Collect.safe_pop(plist, 'UIPrerenderedIcon')
        Collect.safe_pop(plist, 'UIViewControllerBasedStatusBarAppearance')
        plist['UIRequiredDeviceCapabilities'] = ['armv7']
        biplist.writePlist(plist, p, binary=False)

    # 批量重构plist
    def _batch_refactor(root_dir, version=2):
        for root, dirs, _ in os.walk(root_dir):
            for dn in dirs:
                if version == 2 and dn != 'package':
                    continue
                # print(os.path.join(root, dn))
                plists = FS.walk_files(os.path.join(root, dn), ewhites=['.plist'])
                for pp in plists:
                    if version == 2:
                        if pp.endswith('copyright.plist'):
                            continue
                        if pp.endswith('yzadmin.plist'):
                            FS.moveto(pp, pp.replace('yzadmin.plist', 'copyright.plist'))
                            continue
                        if FS.parentname(pp) != FS.filename(pp):
                            continue
                    elif version == 1:
                        if not FS.parentname(pp).endswith(FS.filename(pp)):
                            continue
                    _refactor_xcode_plist(pp)

    _batch_refactor('/Users/joli/proj/client_hssg/trunk/runtime-src/proj.ios_mac/packing', version=1)

# 根据plist分解图片
def test_split_images():
    from com.arts import ImageTailor
    # SplitImages.tp('/Users/joli/Desktop/snsgz/effect/effect_beifa_2/effect_beifa_2.plist')
    pro_root = '/Users/joli/Downloads/effect'
    for f in FS.walk_files(pro_root, ewhites=['.png']):
        ImageTailor.cocos_bytes(f)

    # src = os.path.join(pro, 'snxyj')
    # for f in FS.walk_files(src, ewhites=['.plist'], cut=len(src) + 1):
    #     d = os.path.join(pro, 'snxyj_ef', os.path.dirname(f), FS.filename(f))
    #     SplitImages.tp(os.path.join(src, f), outputdir=d)

    # for filename in FS.walk_files('/Users/joli/Desktop/apps/玄元剑仙/xiuxianRes/UI_effect', ext_whites=['.sk']):
    #     print(filename)
    #     SplitImages.laya_sk(filename)

    # SplitImages.spine('/Users/joli/Downloads/spine/E21032/action.atlas', fixwhite=True)
    # for f in FS.walk_files('/Users/joli/Downloads/zk', ext_whites=['.atlas']):
    #     print(f)
    #     SplitImages.spine(f, fixwhite=False)

# 测试星词典
def test_stardict():
    ts = time.time()
    from extension.ECDICT import stardict
    ecdict_resdir = '/Users/joli/proj/master/python/easy2/extension/ECDICT/res'
    sd = stardict.StarDict(os.path.join(ecdict_resdir, 'stardict.db'), False)
    print('connect db:', time.time() - ts)
    # sd.delete_all(True)

    ts = time.time()
    import re
    re_nline = re.compile('\r|\n')
    re_space = re.compile('\s')
    re_noabc = re.compile('[^a-zA-Z\s]')
    noun_set, verb_set = set(), set()
    for i in range(sd.count(), 0, -1):
        item = sd.query(i)
        word = item.get('word')
        if not word:
            continue
        tran = item.get('translation')
        if not tran:
            continue
        word = re_noabc.sub('', word.strip())
        stat = len(word)
        if not word or 3 > stat or 12 < stat:
            continue
        stat = 0
        for s in re_nline.split(tran.strip()):
            s = s.strip()
            if s.startswith('n.') or s.startswith('na.'):
                stat = 1
                break
            if s.startswith('v.') or s.startswith('vt.'):
                stat = 2
                break
        if 0 == stat:
            continue
        w = ''
        for s in re_space.split(word):
            w += s.capitalize()
        w = w[0].lower() + w[1:]
        if 1 == stat:
            noun_set.add(w)
            print(i, 'add noun:', w)
        if 2 == stat:
            verb_set.add(w)
            print(i, 'add verb:', w)
    sd.close()
    # write noun
    noun_txt = os.path.join(ecdict_resdir, 'starnoun.txt')
    if os.path.isfile(noun_txt):
        os.remove(noun_txt)
    with open(noun_txt, 'a') as fp:
        for w in noun_set:
            fp.write(w + '\n')
    # write verb
    verb_txt = os.path.join(ecdict_resdir, 'starverb.txt')
    if os.path.isfile(verb_txt):
        os.remove(verb_txt)
    with open(verb_txt, 'a') as fp:
        for w in verb_set:
            fp.write(w + '\n')
    print('create lib:', time.time() - ts)
    return 0

def test_modify_csd():
    from com.dev import MakeCSD
    MakeCSD.main()

def test_build_resource():
    from PIL import Image

    def _build_file(src, dst):
        FS.make_parent(dst)
        if src.endswith('.jpg'):
            im = Image.open(src)
            try:
                im.save(dst)
            except:
                print('convert', src)
                im.convert('RGB').save(dst)
            return
        if src.endswith('.png'):
            im = Image.open(src)
            try:
                im.save(dst)
            except:
                print('convert', src)
                im.convert('RGBA').save(dst)
            return
        shutil.copyfile(src, dst)

    def _extract_file(src, dst):
        if src.endswith('.jpg') or src.endswith('.png'):
            FS.make_parent(dst)
            shutil.copyfile(src, dst)

    def _batch_build():
        dst_dir = '/Users/joli/Downloads/Hack/slim/shan'
        res_dir = '/Users/joli/proj/sdk_uzone/trunk/projects/luandou/resource/shan'
        shutil.rmtree(dst_dir)
        file_count = 0
        for fn in sorted(FS.walk_files(res_dir, cut=len(res_dir)+1)):
            print(file_count + 1, fn)
            src = os.path.join(res_dir, fn)
            dst = os.path.join(dst_dir, fn)
            # _build_file(src, dst)
            _extract_file(src, dst)
            file_count = file_count + 1
        print('build %d file done' % file_count)
    # _batch_build()

    _build_file('/Users/joli/Downloads/Hack/slim/0.png',
                '/Users/joli/Downloads/Hack/slim/1.png')

# 检查图片后缀是否与格式相符
def test_check_images():
    from simples.rob import RobCom
    res_dir = '/Users/joli/proj/sdk_uzone/trunk/projects/luandou/resource/shan/res'
    jpg_err, png_err = {}, {}
    for (parent, _, files) in os.walk(res_dir):
        for name in files:
            if name.endswith('.jpg'):
                fn = os.path.join(parent, name)
                with open(fn, 'rb') as fp:
                    magic = fp.read(2)
                    if magic != RobCom.JPG_BEG:
                        jpg_err[fn] = magic
            elif name.endswith('.png'):
                fn = os.path.join(parent, name)
                with open(fn, 'rb') as fp:
                    magic = fp.read(8)
                    if magic != RobCom.PNG_BEG:
                        png_err[fn] = magic
    for k in sorted(jpg_err.keys()):
        print(k, jpg_err[k])
    print('-------------------------------------')
    for k in sorted(png_err.keys()):
        print(k, png_err[k])

# 检查特效图是否重名
def test_check_flashx():
    # import biplist
    # flashx_dir = '/Users/joli/Work/LightPro/Client/dazhanguo/res/dest'
    # itemname_map = {}
    # bad_name_map = {}
    # for (parent, _, files) in os.walk(flashx_dir):
    #     for name in files:
    #         if name.endswith('.plist'):
    #             fn = os.path.join(parent, name)
    #             plist = biplist.readPlist(fn)
    #             for k in plist['frames']:
    #                 if k in itemname_map:
    #                     array = bad_name_map.get(k)
    #                     if not array:
    #                         array = []
    #                         bad_name_map[k] = array
    #                         array.append(itemname_map[k])
    #                     array.append(fn)
    #                 else:
    #                     itemname_map[k] = fn
    # for k, v in bad_name_map.items():
    #     print('-----------', k)
    #     print('\n'.join(v))
    # print('done')

    fxdir = '/Users/joli/Work/CS/C/xiuxian_new/dazhanguo/res/dest'
    fbf = os.path.join(fxdir, 'SheetPackage.fbf')
    with open(fbf, 'rb') as fp:
        ba = Bit.ByteArray()
        ba.init_buffer(fp.read())
        count = ba.read_u32()
        for i in range(count):
            sheetid = ba.read_u32()
            if sheetid == 2555296662:
                print(sheetid)
            ba.read_float()
            n = ba.read_short()
            for j in range(n):
                ba.read_byte()
                ba.read_float()
                ba.read_float()
        print(ba.get_available())
        print(count)


def main():
    # test_lupa()
    # test_ttf2xml()
    # test_batch_refactor_xcplist()
    # test_split_images()
    # test_stardict()
    # test_modify_csd()
    # test_build_resource()
    # test_check_images()
    test_check_flashx()
    pass
