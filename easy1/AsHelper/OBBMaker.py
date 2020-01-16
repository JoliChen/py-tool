# -*- coding: UTF-8 -*-

import os
import shutil

class Helper:

    @classmethod
    def merge_tree(cls, src, dst, symlinks=False, ignore_hidden=True):
        if not os.path.exists(src):
            print('src dir not exists on mergeing')
            return
        if not os.path.isdir(dst):
            os.makedirs(dst)
        errors = []
        for name in os.listdir(src):
            if ignore_hidden and name[0] == '.':
                continue
            src_name = os.path.join(src, name)
            dst_name = os.path.join(dst, name)
            try:
                if symlinks and os.path.islink(src_name):
                    os.symlink(os.readlink(src_name), dst_name)
                elif os.path.isdir(src_name):
                    cls.merge_tree(src_name, dst_name, symlinks)
                else:
                    if os.path.isfile(dst_name):
                        os.remove(dst_name)
                    shutil.copy2(src_name, dst_name)
            except (IOError, os.error) as why:
                errors.append((src_name, dst_name, str(why)))
            except OSError as err:
                errors.extend(err.args[0])
        if errors:
            raise shutil.Error(errors)

class OBBMaker:

    def __init__(self, assets_root, repl_skin_dir, obb_make_root, assets_name, version, package_name, simple_name):
        self._skin_dir = repl_skin_dir
        self._source_dir = os.path.join(assets_root, assets_name)
        self._build_dir  = os.path.join(assets_root, 'build', assets_name)
        self._simple_dir = os.path.join(obb_make_root, 'simples', simple_name)
        self._output_dir = os.path.join(obb_make_root, 'package', assets_name)
        self._keepup_dir = os.path.join(self._output_dir, 'assets')
        self._version = version
        self._package_name = package_name
        self._keepup_list = None

    def _prepare(self):
        assert (self._source_dir is not None) and (self._simple_dir is not None), 'dir can not be None'

        if os.path.exists(self._output_dir):
            shutil.rmtree(self._output_dir)
        os.makedirs(self._output_dir)
        os.mkdir(self._keepup_dir)

        if os.path.exists(self._build_dir):
            shutil.rmtree(self._build_dir)
        # os.makedirs(self._build_dir)

    def build(self):
        self._prepare()
        self._list_keeps()
        self._copy_source()
        self._strip_keeps()
        self._package_obb()

    def _copy_source(self):
        shutil.copytree(self._source_dir, self._build_dir)
        for (root, dirs, files) in os.walk(self._build_dir):
            for file_name in files:
                if file_name[0] == '.':
                    file_path = os.path.join(root, file_name)
                    os.remove(file_path) # 删除隐藏文件
        merge_dir = os.path.join(self._build_dir, os.path.basename(self._skin_dir))
        if os.path.exists(merge_dir):
            Helper.merge_tree(self._skin_dir, merge_dir)

    def _list_keeps(self):
        keep_arr = []
        node_pos = len(self._simple_dir) + 1
        for (root, dirs, files) in os.walk(self._simple_dir):
            for file_name in files:
                if file_name[0] == '.':
                    continue
                file_path = os.path.join(root, file_name)
                keep_arr.append(file_path[node_pos:])
        # print('file_path:%s' % keep_arr)
        self._keepup_list = keep_arr

    def _strip_keeps(self):
        node_pos = len(self._build_dir) + 1
        for (root, dirs, files) in os.walk(self._build_dir):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                file_ref = file_path[node_pos:]
                if file_ref in self._keepup_list:
                    parent_dir_name = os.path.dirname(file_ref)
                    if len(parent_dir_name) > 0:
                        dst_file_dir = os.path.join(self._keepup_dir, parent_dir_name)
                        if not os.path.exists(dst_file_dir):
                            os.makedirs(dst_file_dir)
                    shutil.move(file_path, os.path.join(self._keepup_dir, file_ref))
        for (root, dirs, files) in os.walk(self._build_dir):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                if len(os.listdir(dir_path)) < 1:
                    os.rmdir(dir_path)

    def _package_obb(self):
        zip_path = shutil.make_archive(self._build_dir, 'zip', self._build_dir)
        shutil.move(zip_path, os.path.join(self._output_dir, self._name_obb_file()))

    def _name_obb_file(self):
        return "main." + self._version + "." + self._package_name + ".obb"

def make_obb():
    proj_root = '/Users/joli/proj/client_hssg/trunk/runtime-src'

    obb_maker = OBBMaker(
        proj_root + '/proj.assets',
        proj_root + '/proj.android-dzg/modules/channel/app_xiaoqihk/src/qyzsg/assets/res',
        '/Users/joli/Desktop/outputs/obb',
        'real_sipu_lang', '5003027', 'com.iyouzhong.qyzsg.x7sy', 'real'
    )

    # obb_maker = OBBMaker(
    #     proj_root + '/proj.assets',
    #     proj_root + '/proj.android-dzg/modules/channel/app_7477/src/syzsg/assets/res',
    #     '/Users/joli/Desktop/outputs/obb',
    #     'kato_orig_lang', '5003025', 'com.acehand.ygsyzsg.gp', 'cartoon'
    # )

    # obb_maker = OBBMaker(
    #     proj_root + '/proj.assets',
    #     proj_root + '/proj.android-dzg/modules/channel/app_soha/src/SG211/assets/res',
    #     '/Users/joli/Desktop/outputs/obb',
    #     'real_soha_211', '5003026', 'com.thienha.tanvuong', 'cartoon'
    # )
    obb_maker.build()