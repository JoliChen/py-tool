# -*- coding: utf-8 -*-
# @Time    : 2020/8/14 6:45 PM
# @Author  : Joli
# @Email   : 99755349@qq.com
import json
import os
import platform
import shutil
import math

def log_info(*values):
    print(*values)

def log_error(*values):
    print(*values)

def is_meta_modified(src, dst):
    st1 = os.stat(src)
    st2 = os.stat(dst)
    if st1.st_size != st2.st_size:
        return True
    mt1 = math.floor(st1.st_mtime * 1000)
    mt2 = math.floor(st2.st_mtime * 1000)
    return mt1 != mt2

class CCSProject:
    def __init__(self, projdir):
        self.projdir = projdir
        self.shelldir = os.path.join(projdir, 'make')
        self.toolsdir = os.path.join(projdir, 'tools')
        self.builddir = os.path.join(projdir, 'build')
        self.ccsrtdir = os.path.join(projdir, 'dazhanguo')  # cocos runtime dir
        self.ccsuidir = os.path.join(projdir, 'CocosProject')
        log_info('projdir', self.projdir)
        log_info('shelldir', self.shelldir)
        log_info('toolsdir', self.toolsdir)
        log_info('builddir', self.builddir)
        log_info('ccsrtdir', self.ccsrtdir)
        log_info('ccsuidir', self.ccsuidir)
        if 'Windows' in platform.system():
            self.exec_makeccsui = os.path.join(self.toolsdir, 'CLMakeCSUI.exe')
            self.exec_makesheet = os.path.join(self.toolsdir, 'MakeSheet.exe')
        else:
            self.exec_makeccsui = os.path.join(self.toolsdir, 'CLMakeCSUI')
            self.exec_makesheet = os.path.join(self.toolsdir, 'CLMakeSheet')

    def _sh_server_sheet(self, srcdir, dstdir):
        jar = os.path.join(self.toolsdir, "ExcelTool.jar")
        if not os.path.isfile(jar):
            log_error('can not found', jar)
            return
        # if not os.path.isdir(dstdir):
        #     os.makedirs(dstdir)
        cmd = 'java -jar %s -t -d %s -o %s' % (jar, srcdir, dstdir)
        log_info('build_server_sheet', cmd)
        ret = os.system(cmd)
        log_info('build_server_sheet done with code', ret)
        return ret == 0

    def _sh_client_sheet(self, srcdir, dstdir):
        if not os.path.isfile(self.exec_makesheet):
            log_error('can not found', self.exec_makesheet)
            return
        errlog = os.path.join(self.builddir, 'make_client_sheet.log')
        cmd = '%s -i %s -o %s -f binary -e %s' % (self.exec_makesheet, srcdir, dstdir, errlog)
        log_info('build_client_sheet', cmd)
        ret = os.system(cmd)
        log_info('build_client_sheet done with code', ret)
        return ret == 0

    def _sh_ccsui_data(self, srcdir, dstdir):
        if not os.path.isfile(self.exec_makeccsui):
            log_error('can not found', self.exec_makeccsui)
            return
        cmd = '%s --src %s --dst %s' % (self.exec_makeccsui, srcdir, dstdir)
        log_info('build_ccsui_data', cmd)
        ret = os.system(cmd)
        log_info('build_ccsui_data done with code', ret)
        return ret == 0

    @staticmethod
    def _sh_ccsui_atlas(srcdir, dstdir):
        len_src = len(srcdir) + 1
        for root, _, files in os.walk(srcdir):
            parentdir = root[len_src:]
            if parentdir.startswith('.'):
                continue
            parentdir = os.path.join(dstdir, parentdir)
            if not os.path.isdir(parentdir):
                os.makedirs(parentdir)
            for fn in files:
                if fn.startswith('.'):
                    continue
                src = os.path.join(root, fn)
                dst = os.path.join(parentdir, fn)
                if os.path.isfile(dst) and not is_meta_modified(src, dst):
                    continue
                log_info('copy', dst)
                shutil.copy2(src, dst)  # copy file and stat

class CCSBuilder(CCSProject):
    def __init__(self, projdir):
        CCSProject.__init__(self, projdir)

    def make_server_sheet(self, dstdir):
        srcdir = os.path.join(self.projdir, 'docs', 'config')
        if os.path.isdir(srcdir):
            return self._sh_server_sheet(srcdir, dstdir)
        log_error('can not found', srcdir)

    def make_client_sheet(self):
        srcdir = os.path.join(self.projdir, 'docs', 'config')
        if os.path.isdir(srcdir):
            dstdir = os.path.join(self.ccsrtdir, 'res', 'config')
            return self._sh_client_sheet(srcdir, dstdir)
        log_error('can not found', srcdir)

    def make_ccsui(self):
        pass

    def pack_bundle(self):
        self.bundledir = os.path.join(self.builddir, 'bundle')
        srcdir = os.path.join(self.ccsrtdir, 'src')
        resdir = os.path.join(self.ccsrtdir, 'res')
        bigver = 16774
        subver = 86250
        bvmgr = BundleVersionManager(os.path.join(self.bundledir, 'version'))
        bvmgr.load()

class BundleVersionManager:
    kBigV = 'big_version'
    kSubV = 'sub_version'

    def __init__(self, verdir):
        self.verdir = verdir
        self.bigdict = {}

    def load(self, tar_version):
        if not os.path.isdir(self.verdir):
            return

        for fn in os.listdir(self.verdir):
            if not fn.endswith('.json'):
                continue
            if bigversion and not fn.startswith(bigversion + '_'):
                continue
            with open(os.path.join(self.verdir, fn)) as fp:
                config = json.load(fp)
                bigver = config.get(self.kBigV)
                subver = config.get(self.kSubV)
                if bigver and subver:
                    subdict = self.bigdict.get(bigver)
                    if not subdict:
                        subdict = {}
                        self.bigdict[bigver] = subdict
                    subdict[subver] = config

def main():
    builder = CCSBuilder('/Users/joli/Work/LightPro/Client')
    # builder.make_server_sheet()
    builder.make_client_sheet()
    # builder.make_ccsui_atlas(os.path.join(builder.ccsuidir, 'cocosstudio/pic'), os.path.join(builder.builddir, 'cocosstudio/pic'))

    log_info('done')

if __name__ == '__main__':
    main()