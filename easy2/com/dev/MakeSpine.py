# -*- coding: utf-8 -*-
# @Time    : 2020/12/12 上午11:27
# @Author  : Joli
# @Email   : 99755349@qq.com
import os
import re
import lupa

RE_MODLEID = re.compile("^[^0]\d+")
RE_DATAKEY = re.compile("^data\d+$")
RE_TX_TAIL = re.compile("_0\d_front$")
SP_BT, SP_TX, SP_UI = '_BT', '_TX', '_UI'
ATLAS_EXT = '.atlas'
DATAS_EXT = '.skel'

def get_filename(fp):
    return fp[fp.rfind(os.sep) + 1: fp.rfind('.')]

class Exportor:
    def __init__(self, spine: str):
        self._spine = spine

    @staticmethod
    def find_export_proj(folder):
        for name in os.listdir(folder):
            if name.endswith('_daochu.spine'):
                return os.path.join(folder, name)

    def find_export_dirs(self, folder, tags, model_id, proj_set: set):
        for name in os.listdir(folder):
            for tag in tags:
                if not name.endswith(tag):
                    continue
                proj_path = self.find_export_proj(os.path.join(folder, name))
                if proj_path:
                    proj_set.add(proj_path)
                else:
                    print('no export project [%s: %s: %s]' % (model_id, tag, folder))

    def find_export_models(self, folder, tags, proj_dict: dict):
        for name in os.listdir(folder):
            token = RE_MODLEID.match(name)
            if not token:
                continue
            modeldir = os.path.join(folder, name)
            if not os.path.isdir(modeldir):
                continue
            model_id = token.group()
            projects = set()
            self.find_export_dirs(modeldir, tags, model_id, projects)
            if not projects:
                print('no export model [%s: %s]' % (model_id, folder))
                continue
            proj_set: set = proj_dict.get(model_id)
            if not proj_set:
                proj_set = set()
                proj_dict[model_id] = proj_set
            proj_set.update(projects)

    def find_export_kinds(self, srcdir, tags):
        outmap = {}
        for kind in os.listdir(srcdir):
            kinddir = os.path.join(srcdir, kind)
            if os.path.isdir(kinddir):
                self.find_export_models(kinddir, tags, outmap)
        return outmap

    def run_spine(self, outmap, outcfg, srcdir, dstdir):
        topics, index = [], 0
        for model_id, projects in outmap.items():
            for proj_path in projects:
                index += 1
                print(index, proj_path)
                topics.append('-i "%s"' % proj_path)
                topics.append('-o "%s"' % os.path.join(dstdir, model_id))
                topics.append('-e "%s"' % outcfg)
        if not topics:
            print('no export project found: %s' % srcdir)
            return
        command = '"%s" %s' % (self._spine, ' '.join(topics))
        print('command:%s' % command)
        errcode = os.system(command)
        print('export spines done, errcode:%d' % errcode)

    def export(self, outcfg, srcdir, dstdir, tags):
        outmap = self.find_export_kinds(srcdir, tags)
        if outmap:
            self.run_spine(outmap, outcfg, srcdir, dstdir)
        else:
            print('no export project found: %s' % srcdir)

class Configor:
    def __init__(self, cfgroot):
        self._cfgroot = cfgroot
        self._luart = lupa.LuaRuntime()
        self._luart.execute('cc={exports={}}')
        self._luart.execute(self.load_script(os.path.join(cfgroot, 'SPM.lua')))
        self._luart.execute('SPM=cc.exports.SPM')

    @staticmethod
    def load_script(filepath):
        if not os.path.isfile(filepath):
            return
        with open(filepath, 'r') as fp:
            return fp.read()

    @staticmethod
    def save_script(filepath, content):
        with open(filepath, 'w') as fp:
            return fp.write(content)

    @staticmethod
    def find_atlasfile(model_id, resroot, old_path: str):
        name = old_path[old_path.rfind(os.sep) + 1: old_path.rfind('.')]
        new_path = '%s/%s_daochu.atlas' % (model_id, name)
        if os.path.isfile(os.path.join(resroot, new_path)):
            return new_path

    @staticmethod
    def find_datasfile(model_id, resroot, old_path: str):
        name = old_path[old_path.rfind(os.sep) + 1: old_path.rfind('.')]
        new_path = '%s/%s_daochu.skel' % (model_id, name)
        if os.path.isfile(os.path.join(resroot, new_path)):
            return new_path

    def check_bt(self, segment, resroot, model_id):
        resdir = os.path.join(resroot, model_id)
        for k, v in segment.items():
            if k == 'atlas':
                if not os.path.isfile(os.path.join(resroot, v)):
                    new_path = None
                    for name in os.listdir(resdir):
                        if name.endswith(ATLAS_EXT):
                            shortname = get_filename(name)
                            if shortname.endswith('_front') and not RE_TX_TAIL.search(shortname):
                                new_path = '%s/%s' % (model_id, name)
                                break
                    if new_path:
                        self.add_modify_item(v, new_path)
                    else:
                        print('未找到bt图集文件: %s - %s' % (model_id, k))
            elif RE_DATAKEY.match(k):
                if not os.path.isfile(os.path.join(resroot, v)):
                    new_path = None
                    for name in os.listdir(resdir):
                        if name.endswith(DATAS_EXT):
                            shortname = get_filename(name)
                            if shortname.endswith('_front') and not RE_TX_TAIL.search(shortname):
                                new_path = '%s/%s' % (model_id, name)
                                break
                    if new_path:
                        self.add_modify_item(v, new_path)
                    else:
                        print('未找到bt数据文件: %s - %s' % (model_id, k))

    def check_tx(self, segment, resroot, model_id):
        resdir = os.path.join(resroot, model_id)
        for k, v in segment.items():
            if k == 'atlas':
                if not os.path.isfile(os.path.join(resroot, v)):
                    new_path = None
                    for name in os.listdir(resdir):
                        if name.endswith(ATLAS_EXT):
                            shortname = get_filename(name)
                            if shortname.endswith('TX_daochu') or RE_TX_TAIL.search(shortname):
                                new_path = '%s/%s' % (model_id, name)
                                break
                    if new_path:
                        self.add_modify_item(v, new_path)
                    else:
                        print('未找到tx图集文件: %s - %s' % (model_id, k))
            elif RE_DATAKEY.match(k):
                if not os.path.isfile(os.path.join(resroot, v)):
                    new_path = None
                    for name in os.listdir(resdir):
                        if name.endswith(DATAS_EXT):
                            shortname = get_filename(name)
                            if shortname.endswith('TX_daochu') or RE_TX_TAIL.search(shortname):
                                new_path = '%s/%s' % (model_id, name)
                                break
                    if new_path:
                        self.add_modify_item(v, new_path)
                    else:
                        print('未找到tx数据文件: %s - %s' % (model_id, k))

    def check_ui(self, segment, resroot, model_id):
        resdir = os.path.join(resroot, model_id)
        for k, v in segment.items():
            if k == 'atlas':
                if not os.path.isfile(os.path.join(resroot, v)):
                    new_path = None
                    for name in os.listdir(resdir):
                        if name.endswith(SP_UI + ATLAS_EXT):
                            new_path = '%s/%s' % (model_id, name)
                            break
                    if new_path:
                        self.add_modify_item(v, new_path)
                    else:
                        print('未找到ui图集文件: %s - %s' % (model_id, k))
            elif RE_DATAKEY.match(k):
                if not os.path.isfile(os.path.join(resroot, v)):
                    new_path = None
                    for name in os.listdir(resdir):
                        if name.endswith(SP_UI + DATAS_EXT):
                            new_path = '%s/%s' % (model_id, name)
                            break
                    if new_path:
                        self.add_modify_item(v, new_path)
                    else:
                        print('未找到ui数据文件: %s - %s' % (model_id, k))

    def add_modify_item(self, olds, news):
        self._modifieds.append((olds, news))

    def verify_model(self, resroot, model_id, modifyable=False):
        cfglua = os.path.join(self._cfgroot, 'model', 'M_%s.lua' % model_id)
        script = self.load_script(cfglua)
        if not script:
            print('script not exists: %s', cfglua)
            return
        config = self._luart.execute(script)
        if not config:
            print('script parse fail: %s', cfglua)
            return
        self._modifieds = []
        if config.bt:
            self.check_bt(config.bt, resroot, model_id)
        if config.tx:
            self.check_tx(config.tx, resroot, model_id)
        if config.ui:
            self.check_ui(config.ui, resroot, model_id)
        if self._modifieds:
            if modifyable:
                for item in self._modifieds:
                    script = script.replace(item[0], item[1], 1)
                print('modify: %s' % cfglua)
                self.save_script(cfglua, script)
            else:
                for item in self._modifieds:
                    print('modify: %s - %s' % (cfglua, item))

    def verify_roots(self, resroot, modifyable=False):
        for name in os.listdir(resroot):
            if not RE_MODLEID.match(name):
                continue
            self.verify_model(resroot, name, modifyable)

def parse_sounds(root):
    import json
    import shutil
    from jonlin.utils import FS
    skels = {}
    for (par, _, files) in os.walk(root):
        for name in files:
            if not name.endswith('.json'):
                continue
            skel = json.loads(FS.read_text(os.path.join(par, name)))
            if not skel:
                continue
            anis = skel.get('animations')
            if not anis:
                continue
            for ani_name, ani_data in anis.items():
                for it_name, item in ani_data.items():
                    if it_name != 'events':
                        continue
                    for evt in item:
                        if evt.get('name') != 'sound':
                            continue
                        snd = evt.get('string')
                        if snd:
                            skel_node = skels.setdefault(name, {})
                            ani_node = skel_node.setdefault(ani_name, {})
                            it_node = ani_node.setdefault(it_name, {})
                            it_node[snd] = True
                        else:
                            # print('no sound name', name, ani_name, it_name)
                            pass
    fromdir = '/Users/joli/Downloads/sound'
    todir = '/Users/joli/Desktop/sounds/'
    for name, skel_node in skels.items():
        for ani_name, ani_node in skel_node.items():
            for it_name, it_node in ani_node.items():
                for snd in it_node:
                    fp = os.path.join(fromdir, snd + '.mp3')
                    if os.path.isfile(fp):
                        shutil.copyfile(fp, todir + snd + '.mp3')
                        pass
                    else:
                        print(f'{name}:{ani_name}:sound:{snd}')
    # print('----------------------总共:%d' % len(sounds))

def main():
    spiner = Exportor('/Applications/Spine.app/Contents/MacOS/Spine')
    outcfg = '/Users/joli/Work/CS/C/xiyou/特效梳理/SPINE源文件/out.json'
    dstdir = '/Users/joli/Work/CS/C/xiyou/dazhanguo/res/sp'
    # outcfg = '/Users/joli/Work/CS/C/xiyou/特效梳理/SPINE源文件/out_text.json'
    # dstdir = '/Users/joli/Desktop/spine_json'

    # srcdir = '/Users/joli/Work/CS/C/xiyou/特效梳理/SPINE源文件/spine动画/战斗人物最终'
    # spiner.export(outcfg, srcdir, dstdir, (SP_BT, SP_TX))
    # srcdir = '/Users/joli/Work/CS/C/xiyou/特效梳理/SPINE源文件/spine动画/立绘最终'
    # spiner.export(outcfg, srcdir, dstdir, (SP_UI,))

    outcfg = '/Users/joli/Work/CS/C/xiyou/特效梳理/SPINE源文件/out_tx.json'
    srcdir = '/Users/joli/Work/CS/C/xiyou/特效梳理/SPINE源文件/spine动画/战斗人物最终'
    spiner.export(outcfg, srcdir, dstdir, (SP_TX,))

    cfger = Configor('/Users/joli/Work/CS/C/xiyou/dazhanguo/res/scripts/cfgs')
    cfger.verify_roots(dstdir)

    # parse_sounds(dstdir)

if __name__ == '__main__':
    main()