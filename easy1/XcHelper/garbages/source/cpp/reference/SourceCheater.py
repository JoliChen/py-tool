# -*- coding: UTF-8 -*-
# 欺骗代码

from XcHelper.garbages.source.cpp.CppClass import JCppClass
from XcHelper.garbages.source.cpp.reference.cheat.CheatMaker import JCheatMaker

class JSourceCheater(JCppClass):
    def __init__(self, assets_info=None, oc_bridge_cls=None):
        JCppClass.__init__(self)
        self.head_desc = '// 兵者诡道也'
        self.className = 'JTeapot'
        # 生成欺骗函数
        self.add_header_to_implement('<PlayEasyuse/Http.h>')
        self.add_header_to_implement('<PlayEasyuse/Helper.h>')

        self.add_implement_macros('__httpPOST(url, args, cb)',  'UB::Http::postData(url, args, cb)')
        self.add_implement_macros('__http_GET(url, args, cb)',  'UB::Http::getData(url, args, cb)')
        self.add_implement_macros('__makeText(length)',         'UB::Helper::randString(length)')
        self.add_implement_macros('__readFile(path, limit)',    'UB::Helper::readData(path, limit)')
        self.add_implement_macros('__saveFile(path, bytes)',    'UB::Helper::writeData(path, bytes)')

        JCheatMaker.cheat_net_io(self)
        JCheatMaker.cheat_disk_input(self, assets_info)
        JCheatMaker.cheat_disk_output(self)
        # 注入混淆配置
        JCheatMaker.inject_assets(self, assets_info)
        JCheatMaker.inject_script(self, oc_bridge_cls)