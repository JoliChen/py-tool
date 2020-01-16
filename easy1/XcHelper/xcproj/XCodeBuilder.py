# -*- coding: UTF-8 -*-
# Xcode 命令行打包

import os
import shutil
import time
from XcHelper.xcproj.XCodeProj import JXCodeProj
from XcHelper.xcproj.options_configs.XCodeOptions import JOptionsPlist, JExportOptions
from machine.Machine import JMachine
from machine.Network import JNetwork

class XCFatalError(Exception):
    pass

class JXcodeBuilder:
    MY_USER_PASSWORD = '6666'
    MY_IF_NAMES_LIST = ['en0']
    UNIVERSAL_PROVIS = ['uzone-dev-all', 'CC52DevAll']  # 通用签名证书名称

    @staticmethod
    def no_universal(specifier):
        return specifier not in JXcodeBuilder.UNIVERSAL_PROVIS

    def __init__(self, proj_root, proj_name, scheme_name, output_dir, configuration='Release'):
        self.proj_path = os.path.join(proj_root, proj_name + u'.xcodeproj')
        self.proj_name = proj_name
        self.scheme_name = scheme_name
        self.configuration = configuration
        self.build_title = None
        self.options_dir = os.path.join(output_dir, 'options')
        self.archive_dir = os.path.join(output_dir, 'archive')
        self.package_dir = os.path.join(output_dir, 'package')
        self.zipfile_dir = os.path.join(output_dir, 'zipfile')
        self.dev_options_path = None
        self.dis_options_path = None
        self.dev_package_path = None
        self.dis_package_path = None

    def build_archive(self):
        self._prepare()
        self._export_archive()
        print('build archive done')

    def build_ipa(self, exist_archive_file=None, package_file=True, upload_package=True):
        self._prepare()
        # 导出未签名包
        temp_archive = False
        archive_path = None
        if (exist_archive_file is None):
            archive_path = self._export_archive()
            temp_archive = True
        else:
            archive_path = exist_archive_file
        # 导出签名ipa
        self._export_package(archive_path)
        # 删除临时archive资源
        if temp_archive:
            shutil.rmtree(archive_path)
        # zip打包备份
        if package_file:
            zip_file = self._zip_package_archive()
            self._ethernet_turn_on()
            if upload_package:
                self._upload_ftp(zip_file)
            JMachine.open_system_folder(self.zipfile_dir)
        else:
            self._ethernet_turn_on()
            JMachine.open_system_folder(self.package_dir)
        print('build ipa done')

    def _prepare(self):
        self._ethernet_turn_off()
        self._modify_mac_addr()
        self._setup_env()
        self._config_ts()
        self._config_options()

    def _setup_env(self):
        if not os.path.exists(self.options_dir):
            os.makedirs(self.options_dir)
        if not os.path.exists(self.archive_dir):
            os.makedirs(self.archive_dir)
        if not os.path.exists(self.package_dir):
            os.makedirs(self.package_dir)
        if not os.path.exists(self.zipfile_dir):
            os.makedirs(self.zipfile_dir)
        os.system('python -V')
        os.system('xcodebuild -version')

    def _config_ts(self):
        build_date = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
        self.build_title = build_date + '_' + self.proj_name + '_' + self.scheme_name

    def _config_options(self):
        xcode = JXCodeProj(self.proj_path)
        dev_specifier = xcode.get_flag('PROVISIONING_PROFILE_SPECIFIER', self.scheme_name, 'Debug')
        print('dev_provisioning_profile_specifier:%s' % dev_specifier)
        assert self.no_universal(dev_specifier), 'universal provisioning profile:%s' % dev_specifier

        dis_specifier = xcode.get_flag('PROVISIONING_PROFILE_SPECIFIER', self.scheme_name)
        print('dis_provisioning_profile_specifier:%s' % dis_specifier)
        team_id = xcode.get_flag('DEVELOPMENT_TEAM', self.scheme_name)
        print('development_team:%s' % team_id)
        identifier = xcode.get_flag('PRODUCT_BUNDLE_IDENTIFIER', self.scheme_name)
        print('product_identifier:%s' % identifier)

        self.dev_options_path = os.path.join(self.options_dir, 'export_development.plist')
        self.dis_options_path = os.path.join(self.options_dir, 'export_appstore.plist')
        plist = JOptionsPlist()
        # output developer options
        plist.reset(JExportOptions.DEVELOPMENT)
        plist.set_sign(identifier, team_id, dev_specifier)
        plist.write_to_file(self.dev_options_path)
        # output appstore options
        plist.reset(JExportOptions.APPSTORE)
        plist.set_sign(identifier, team_id, dis_specifier)
        plist.write_to_file(self.dis_options_path)

    def _export_archive(self):
        archive_path = os.path.join(self.archive_dir, self.build_title + '.xcarchive')
        self._cmd_clean()
        self._cmd_archive(archive_path)
        return archive_path

    def _export_package(self, archive_path=None):
        self.dev_package_path = os.path.join(self.package_dir, self.build_title, 'dev')
        self.dis_package_path = os.path.join(self.package_dir, self.build_title, 'dis')
        # export developer ipa
        self._cmd_export_archive(archive_path, self.dev_package_path, self.dev_options_path)
        # export distribution ipa
        self._cmd_export_archive(archive_path, self.dis_package_path, self.dis_options_path)
        # clean after export ipa
        self._cmd_clean()

    def _cmd_clean(self):
        cmd = 'xcodebuild clean -project %s -scheme %s -configuration %s' % \
              (self.proj_path, self.scheme_name, self.configuration)
        print('cmd:%s' % cmd)
        exit_code = os.system(cmd)
        assert exit_code == 0, '_cmd_clean error:%d' % exit_code

    def _cmd_archive(self, archive_path):
        cmd = 'xcodebuild archive -project %s -scheme %s -configuration %s -archivePath %s' % \
              (self.proj_path, self.scheme_name, self.configuration, archive_path)
        print('cmd:%s' % cmd)
        exit_code = os.system(cmd)
        assert exit_code == 0, '_cmd_archive error:%d' % exit_code

    def _cmd_export_archive(self, archive_path, export_path, option_path):
        cmd = 'xcodebuild -exportArchive -archivePath %s -exportPath %s -exportOptionsPlist %s' % \
              (archive_path, export_path, option_path)
        print('cmd:%s' % cmd)
        exit_code = os.system(cmd)
        assert exit_code == 0, '_cmd_export_ipa error:%d' % exit_code

    def _zip_package_archive(self):
        # 创建zip包文件夹
        zip_dir = os.path.join(self.zipfile_dir, self.build_title)
        if not os.path.exists(zip_dir):
            os.makedirs(zip_dir)
        # 移动ipa到zip文件夹
        for file_name in os.listdir(self.dev_package_path):
            file_info = os.path.splitext(file_name)
            if (file_info[1] == '.ipa'):
                file_path = os.path.join(self.dev_package_path, file_name)
                shutil.move(file_path, os.path.join(zip_dir, file_info[0] + '_test.ipa'))
                break
        for file_name in os.listdir(self.dis_package_path):
            file_info = os.path.splitext(file_name)
            if (file_info[1] == '.ipa'):
                file_path = os.path.join(self.dis_package_path, file_name)
                shutil.move(file_path, os.path.join(zip_dir, file_info[0] + '.ipa'))
                break
        # zip
        shutil.make_archive(zip_dir, 'zip', zip_dir)
        # 删除 package/build_title
        shutil.rmtree(os.path.join(self.package_dir, self.build_title))
        # 删除 zipfile/build_title
        shutil.rmtree(zip_dir)
        return zip_dir + '.zip'

    # 上传到内网FTP
    @staticmethod
    def _upload_ftp(package_path):
        host = '10.16.254.16'
        port = 21
        user = 'ttans'
        pswd = 'ttans'
        path = 'ttans_bak/products/ios/' + os.path.split(package_path)[1]
        JMachine.ftp_upload(host, port, user, pswd, path, package_path)

    # 打包之前关闭网络
    @staticmethod
    def _ethernet_turn_off():
        if not JNetwork.is_net_ok():
            return
        JNetwork.net_turn_off(JXcodeBuilder.MY_USER_PASSWORD, JXcodeBuilder.MY_IF_NAMES_LIST)
        for i in range(10):
            if not JNetwork.is_net_ok():
                return
            time.sleep(1)
        raise XCFatalError('please turn off network before archive')

    # 上传备份之前打开网络
    @staticmethod
    def _ethernet_turn_on():
        if JNetwork.is_net_ok():
            return
        JNetwork.net_turn_on(JXcodeBuilder.MY_USER_PASSWORD, JXcodeBuilder.MY_IF_NAMES_LIST)
        for i in range(10):
            if JNetwork.is_net_ok():
                return
            time.sleep(1)
        raise XCFatalError('please turn on network before upload')

    # 修改mac地址
    @staticmethod
    def _modify_mac_addr():
        for if_name in JXcodeBuilder.MY_IF_NAMES_LIST:
            JNetwork.set_random_mac_address(JXcodeBuilder.MY_USER_PASSWORD, if_name)