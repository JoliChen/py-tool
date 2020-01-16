# -*- coding: UTF-8 -*-
import socket
import os
import platform
import psutil
import requests
import re
import subprocess
import uuid

class JNetwork:

    @staticmethod
    def get_mac_address():
        tag = uuid.getnode()
        mac = uuid.UUID(int=tag).hex[-12:]
        mac = ":".join([mac[e:e + 2] for e in range(0, 11, 2)])
        return mac

    @staticmethod
    def get_random_mac_address():
        # mac = []
        # for i in range(6):
        #     mac.append('%02x' % random.randint(0, 255))
        # return ':'.join(mac)
        from scapy.volatile import RandMAC
        return RandMAC()

    @classmethod
    def set_random_mac_address(cls, user_pwd, if_name):
        mac_addr = cls.get_random_mac_address() # 'd0:67:e5:2e:07:f1' #
        print('random_mac_addr', mac_addr)
        cls.set_mac_address(user_pwd, if_name, mac_addr)

    @classmethod
    def set_mac_address(cls, user_pwd, if_name, mac_addr):
        sys_name = platform.system()
        if (sys_name == 'Windows'):
            print("Call Windows tasks")
            return
        if (sys_name == 'Linux'):
            print("Call Linux tasks")
            return
        if (sys_name == 'Darwin'):
            cls._set_macaddr_for_mac(user_pwd, if_name, mac_addr)

    @staticmethod
    def _set_macaddr_for_mac(user_pwd, if_name, mac_addr):
        cmd = 'echo "%s" | sudo -S ifconfig %s lladdr %s' % (user_pwd, if_name, mac_addr)
        ret = subprocess.run(cmd, shell=True)
        print(user_pwd)
        print('set_mac_addr returncode =', ret.returncode)

    @staticmethod
    def get_public_ip():
        response = requests.get("http://2018.ip138.com/ic.asp")
        web_html = response.content.decode(errors='ignore')
        pub_ip = re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', web_html).group(0)
        return pub_ip

    # 检查网络连接
    @staticmethod
    def is_net_ok():
        cmd = 'ping www.baidu.com -c 2'
        ret = os.system(cmd)
        return 0 == ret

    @classmethod
    def net_turn_on(cls, user_pwd, if_list):
        sys_name = platform.system()
        if (sys_name == 'Windows'):
            print("Call Windows tasks")
            return
        if (sys_name == 'Linux'):
            print("Call Linux tasks")
            return
        if (sys_name == 'Darwin'):
            cls._net_turn_on_for_mac(user_pwd, if_list)

    @classmethod
    def net_turn_off(cls, user_pwd, if_list=None):
        sys_name = platform.system()
        if if_list is None:
            if_list = cls.list_ifnames()
        if (sys_name == 'Windows'):
            print("Call Windows tasks")
            return
        if (sys_name == 'Linux'):
            print("Call Linux tasks")
            return
        if (sys_name == 'Darwin'):
            cls._net_turn_off_for_mac(user_pwd, if_list)

    @staticmethod
    def _net_turn_on_for_mac(user_pwd, if_list):
        # networksetup -listallhardwareports
        # networksetup -setairportpower %(HardwareDevice)s on/off
        # ifconfig %(HardwareDevice)s up/down
        for device in if_list:
            cmd = 'echo "%s" | sudo -S ifconfig %s %s' % (user_pwd, device, 'up')
            ret = subprocess.run(cmd, shell=True)
            print(user_pwd)
            print('net_turn_on returncode =', ret.returncode)

    @staticmethod
    def _net_turn_off_for_mac(user_pwd, if_list):
        for device in if_list:
            cmd = 'echo "%s" | sudo -S ifconfig %s %s' % (user_pwd, device, 'down')
            ret = subprocess.run(cmd, shell=True)
            print(user_pwd)
            print('net_turn_off returncode =', ret.returncode)

    @staticmethod
    def list_ifnames():
        if_list = []
        for if_name, family_list in psutil.net_if_addrs().items():
            for fa_info in family_list:
                if (fa_info[0] == socket.AF_INET) and (fa_info[1] != '127.0.0.1'):
                    if_list.append(if_name)
        return if_list