# -*- coding: utf-8 -*-
# @Time    : 2020/12/12 上午11:27
# @Author  : Joli
# @Email   : 99755349@qq.com
import os
import re

RE_MODLEID = re.compile("^[^0]\d+")
SP_BT, SP_TX, SP_UI = '_BT', '_TX', '_UI'

def find_export_proj(folder):
    for name in os.listdir(folder):
        if name.endswith('_daochu.spine'):
            return os.path.join(folder, name)

def find_export_dirs(folder, tags, model_id, proj_set: set):
    for name in os.listdir(folder):
        for tag in tags:
            if not name.endswith(tag):
                continue
            proj_path = find_export_proj(os.path.join(folder, name))
            if not proj_path:
                print('no export project [%s: %s: %s]' % (model_id, tag, folder))
                continue
            proj_set.add(proj_path)

def find_export_models(folder, tags, proj_dict: dict):
    for name in os.listdir(folder):
        token = RE_MODLEID.match(name)
        if not token:
            continue
        model_id = token.group()
        projects = set()
        find_export_dirs(os.path.join(folder, name), tags, model_id, projects)
        if not projects:
            print('no export model [%s: %s]' % (model_id, folder))
            continue
        proj_set: set = proj_dict.get(model_id)
        if not proj_set:
            proj_set = set()
            proj_dict[model_id] = proj_set
        proj_set.update(projects)

def run_export(spine, outcfg, srcdir, dstdir, tags):
    model_dict = {}
    for kind in os.listdir(srcdir):
        kinddir = os.path.join(srcdir, kind)
        if not os.path.isdir(kinddir):
            continue
        find_export_models(kinddir, tags, model_dict)
    if not model_dict:
        print('no export project found: %s' % srcdir)
        return
    topics, index = [], 0
    for model_id, projects in model_dict.items():
        for proj_path in projects:
            index += 1
            print(index, proj_path)
            topics.append('-i "%s"' % proj_path)
            topics.append('-o "%s"' % os.path.join(dstdir, model_id))
            topics.append('-e "%s"' % outcfg)
    if not topics:
        print('no export project found: %s' % srcdir)
        return
    command = '"%s" %s' % (spine, ' '.join(topics))
    print('command:%s' % command)
    errcode = os.system(command)
    print('export spines done, errcode:%d' % errcode)

def main():
    spine = '/Applications/Spine.app/Contents/MacOS/Spine'
    outcfg = '/Users/joli/Work/CS/C/xiyou/特效梳理/SPINE源文件/out.json'
    dstdir = '/Users/joli/Work/CS/C/xiyou/dazhanguo/res/sp'
    # srcdir = '/Users/joli/Work/CS/C/xiyou/特效梳理/SPINE源文件/spine动画/战斗人物最终'
    # run_export(spine, outcfg, srcdir, dstdir, (SP_BT, SP_TX))
    srcdir = '/Users/joli/Work/CS/C/xiyou/特效梳理/SPINE源文件/spine动画/立绘最终'
    run_export(spine, outcfg, srcdir, dstdir, (SP_UI,))

if __name__ == '__main__':
    main()