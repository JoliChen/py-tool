# -*- coding: UTF-8 -*-
# Xcode 工程配置

import os
import shutil

from pbxproj import XcodeProject
from pbxproj.pbxextensions import FileOptions, ProjectFiles, TreeType

XCODE_PROJECT_FILE = u'project.pbxproj'

class JXCodeProj:
    def __init__(self, xcodeproj_path):
        self._xcodeproj_path = xcodeproj_path
        self.xcproj = XcodeProject.load(os.path.join(self._xcodeproj_path, XCODE_PROJECT_FILE))

    @staticmethod
    def desc_file_by_path(path):
        ext = str(os.path.splitext(path)[1])
        if (ext not in ProjectFiles._FILE_TYPES):
            ProjectFiles._FILE_TYPES[ext] = (u'file', u'PBXResourcesBuildPhase')

    def safe_save(self):
        temp_path = os.path.join(self._xcodeproj_path, XCODE_PROJECT_FILE + u'.temp')
        self.xcproj.save(temp_path)
        proj_path = os.path.join(self._xcodeproj_path, XCODE_PROJECT_FILE)
        shutil.move(temp_path, proj_path)

    def get_group_by_path(self, path, parent=None):
        xc_groups = self.xcproj.get_groups_by_path(path, parent)
        if len(xc_groups) == 1:
            return xc_groups[0]
        group_name = os.path.split(path)[1]
        xc_groups = self.xcproj.get_groups_by_path(group_name, parent)
        if len(xc_groups) == 1:
            return xc_groups[0]

    def get_or_create_group(self, path, parent=None):
        xc_group = self.get_group_by_path(path, parent)
        if xc_group is None:
            xc_group = self.create_group(path, parent)
        return xc_group

    def create_group(self, path, parent=None):
        group_name = os.path.split(path)[1]
        return self.xcproj.add_group(group_name, path, parent)

    def remove_group_by_path(self, path, parent=None):
        xc_group = self.get_group_by_path(path, parent)
        if xc_group is not None:
            return self.xcproj.fast_remove_group_by_id(xc_group.get_id(), True)
        return True

    def add_folder_group(self, path, parent=None, target_name=None):
        excludes = ['\.(.*?)'] #过滤隐藏文件
        return len(self.xcproj.add_folder(path, parent, excludes, True, True, target_name))

    def add_folder_reference(self, path, parent=None, target_name=None):
        file_count = 0
        push_count = 0
        default_options = FileOptions()
        file_list = os.listdir(path)
        # print('xcode files:', len(file_list))
        for f in file_list:
            if (f[0] == '.'):
                continue  # 过滤隐藏文件
            file_path = os.path.join(path, f)
            n = 0
            if (os.path.isfile(file_path)) :
                self.desc_file_by_path(file_path)
                n = len(self.xcproj.add_file(file_path, parent, TreeType.GROUP, target_name, default_options))
            elif (os.path.isdir(file_path)) :
                n = len(self.xcproj.add_folder(file_path, parent, None, True, False, target_name, default_options))
            push_count += n
            file_count += 1
        assert push_count == file_count, 'add_folder_reference error [%d/%d]' % (push_count, file_count)
        return push_count

    def get_flag(self, flag_name, target_name, configuration_name='Release'):
        xc_flags = self.xcproj.get_flags(flag_name, target_name, configuration_name)
        if len(xc_flags) == 1:
            return xc_flags[0]