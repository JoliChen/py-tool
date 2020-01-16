# -*- coding: UTF-8 -*-
import os
import platform

class JMachine:



    # 打开包所在的系统文件夹
    @staticmethod
    def open_system_folder(folder_path):
        sys_name = platform.system()
        if (sys_name == 'Windows'):
            os.system('start explorer ' + folder_path)
            return
        if (sys_name == 'Linux'):
            os.system('open ' + folder_path)
            return
        if (sys_name == 'Darwin'):
            os.system('open ' + folder_path)
            return

    # 上传到FTP
    @staticmethod
    def ftp_upload(ip, port, usr, pwd, ftp_path, loc_path, timeout=60, log_level=2):
        ftp_client = None
        local_file = None
        try:
            from ftplib import FTP
            ftp_client = FTP()  # 实例化FTP对象
            ftp_client.set_debuglevel(log_level)
            ftp_client.connect(ip, port, timeout)
            ftp_client.login(usr, pwd)  # 登录
            # print ftp_client.getwelcome()
            local_file = open(loc_path, 'rb')
            ftp_client.storbinary('STOR ' + ftp_path, local_file)
        except:
            print('upload to ftp failed', loc_path)
        finally:
            if ftp_client is not None:
                ftp_client.close()
            if local_file is not None:
                local_file.close()