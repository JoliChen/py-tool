# -*- coding: utf-8 -*-
# @Time    : 2019/4/11 4:02 PM
# @Author  : Joli
# @Email   : 99755349@qq.com
import re
import socket
import uuid

import psutil
import requests
from scapy import volatile
from jonlin.utils import Cross
from jonlin.cl import Shell


def is_net_ok():
    return 0 == Shell.run('ping www.baidu.com -c 2')

def get_public_ip():
    response = requests.get("http://2019.ip138.com/ic.asp")
    web_html = response.content.decode(errors='ignore')
    pub_ip = re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', web_html).group(0)
    return pub_ip

def list_ifnames():
    if_list = []
    for if_name, family_list in psutil.net_if_addrs().items():
        for fa_info in family_list:
            if (fa_info[0] == socket.AF_INET) and (fa_info[1] != '127.0.0.1'):
                if_list.append(if_name)
    return if_list

def get_mac_address():
    tag = uuid.getnode()
    mac = uuid.UUID(int=tag).hex[-12:]
    mac = ":".join([mac[e:e + 2] for e in range(0, 11, 2)])
    return mac

def get_random_mac_address():
    return volatile.RandMAC()

def set_random_mac_address(user_pwd, if_name):
    mac_addr = get_random_mac_address()  # 'd0:67:e5:2e:07:f1' #
    print('random_mac_addr', mac_addr)
    set_mac_address(user_pwd, if_name, mac_addr)

def set_mac_address(user_pwd, if_name, mac_addr):
    print(user_pwd)
    if Cross.IS_MACOSX:
        ret = Shell.run('echo "%s" | sudo -S ifconfig %s lladdr %s' % (user_pwd, if_name, mac_addr))
        print('set_mac_addr returncode =', ret)
    elif Cross.IS_LINUX:
        pass
    elif Cross.IS_WINDOWS:
        pass

def net_turn_on(user_pwd, if_list):
    print(user_pwd)
    if Cross.IS_MACOSX:
        # networksetup -listallhardwareports
        # networksetup -setairportpower %(HardwareDevice)s on/off
        # ifconfig %(HardwareDevice)s up/down
        for device in if_list:
            ret = Shell.run('echo "%s" | sudo -S ifconfig %s %s' % (user_pwd, device, 'up'))
            print('net_turn_on returncode =', ret)
    elif Cross.IS_LINUX:
        pass
    elif Cross.IS_WINDOWS:
        pass

def net_turn_off(user_pwd, if_list=None):
    print(user_pwd)
    if Cross.IS_MACOSX:
        for device in if_list:
            ret = Shell.run('echo "%s" | sudo -S ifconfig %s %s' % (user_pwd, device, 'down'))
            print('net_turn_off returncode =', ret)
    elif Cross.IS_LINUX:
        pass
    elif Cross.IS_WINDOWS:
        pass