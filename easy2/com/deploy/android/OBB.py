# -*- coding: utf-8 -*-
# @Time    : 2018/10/8 下午2:39
# @Author  : Joli
# @Email   : 99755349@qq.com

import os
import shutil
from jonlin.utils import FS

class ObbBuilder:

    @staticmethod
    def build(work_dir):
        import biplist
        config = biplist.readPlist(os.path.join(work_dir, 'config.plist'))
        curdir = config['work_dir'] if 'work_dir' in config else work_dir

        build_dir = os.path.join(curdir, 'build')
        shutil.rmtree(build_dir)
        shutil.copytree(config['resource_dir'], build_dir)

        assets_dir = os.path.join(config['project_dir'], 'assets')
        for fn in os.listdir(assets_dir):
            if fn in config['keeps']:
                continue
            fp = os.path.join(assets_dir, fn)
            if os.path.isfile(fp):
                os.remove(fp)
            elif os.path.isdir(fp):
                shutil.rmtree(fp)

        skin_dir = os.path.join(config['project_dir'], 'skin')
        FS.merge_tree(skin_dir, build_dir)

        template_dir = os.path.join(curdir, 'template', config['template_name'])
        white_list = FS.walk_files(template_dir, cut=len(template_dir) + 1)
        FS.moveto_dir(build_dir, assets_dir, white_list)
        FS.rm_empty_dirs(build_dir)

        zip_path = shutil.make_archive(build_dir, 'zip', build_dir)
        obb_path = os.path.join(build_dir, 'main.%s.%s.obb' % (config['version'], config['appid']))
        shutil.move(zip_path, obb_path)

        print('make obb done =>', obb_path)