# -*- coding: UTF-8 -*-
import os
import sys
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

class AssetsError(Exception):
    pass

class AssetsMaker:
    def __init__(self, build_root, target_name, assets_name):
        self._build_root = build_root
        self._target_name = target_name
        self._assets_name = assets_name
        self._assets_root = os.path.join(build_root, 'buildscript', 'assets')
        self._assets_dir = os.path.join(self._assets_root, assets_name)

    def _predo(self):
        if os.path.exists(self._assets_dir):
            shutil.rmtree(self._assets_dir)
        # os.makedirs(self._assets_dir)

    def _copy_res(self):
        res_dir = os.path.join(self._build_root, 'resource', self._assets_name)
        if not os.path.exists(res_dir):
            raise AssetsError('resource [%s] not exists' % self._assets_name)
        shutil.copytree(res_dir, self._assets_dir)

    def _repl_comm(self):
        comm_dir = os.path.join(self._assets_root, 'common')
        if not os.path.exists(comm_dir):
            return
        Helper.merge_tree(comm_dir, self._assets_dir)

    def _repl_skin(self):
        if not self._target_name:
            return
        skin_dir = os.path.join(self._build_root, 'packing', self._target_name, 'skin')
        if not os.path.exists(skin_dir):
            raise AssetsError('replace [%s] skin not exists' % self._target_name)
        Helper.merge_tree(skin_dir, self._assets_dir)

    def execute(self):
        self._predo()
        self._copy_res()
        self._repl_comm()
        self._repl_skin()
        print('make assets done')

def main(args):
    print(args)
    print(sys.version)

    args_nums = len(args)
    build_root  = args[1]
    target_name = args[2]
    assets_name = args[3]
    AssetsMaker(build_root, target_name, assets_name).execute()

if __name__ == '__main__':
    main(sys.argv)