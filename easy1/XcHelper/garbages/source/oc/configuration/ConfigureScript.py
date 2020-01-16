# -*- coding: UTF-8 -*-
# 脚本桥接口替换

from XcHelper.garbages.source.oc.OCGrammar import *
from XcHelper.garbages.source.oc.OCHelper import JOcHelper

class JConfigureScript(JOcClass):
    def __init__(self, className):
        JOcClass.__init__(self, className)
        self.fileSuffix = '.mm'
        self._api_map = {}  # 接口映射表
        self.__init__imports()
        self.__init__methods()
        self.__sort__methods()

    def get_oc_api_map(self):
        return self._api_map

    def __init__imports(self):
        self.imports = []  # 导入头文件
        self.imports.append('<PlayDrawkit/UNBridge.h>')

    def __init__methods(self):
        self.methods = []  # 函数数组
        # InitToLua
        self._map_method('InitToLua', None)
        # versionUpdateWithAppVersion
        self._map_method('versionUpdateWithAppVersion',
                         'UNBridge::getInstance()->onHotUpdate(dict)',
                         'NSDictionary*', 'dict')
        # InitSDK
        self._map_method('InitSDK',
                         'UNBridge::getInstance()->onLoadGame()')
        # showLogin
        self._map_method('showLogin',
                         'UNBridge::getInstance()->onOpenLogin()')
        # logout
        self._map_method('logout',
                         'UNBridge::getInstance()->onRoleLogout()')
        # enterUserCenter
        self._map_method('enterUserCenter',
                         'UNBridge::getInstance()->onRoleOpenUC()')
        # enterBBS
        self._map_method('enterBBS',
                         'UNBridge::getInstance()->onRoleOpenBBS()')
        # payment
        self._map_method('payment',
                         'UNBridge::getInstance()->onRolePayment(dict)',
                         'NSDictionary*', 'dict')
        # createPlayer
        self._map_method('createPlayer',
                         'UNBridge::getInstance()->onRoleCreated(dict)',
                         'NSDictionary*', 'dict')
        # enterComplete
        self._map_method('enterComplete',
                         'UNBridge::getInstance()->onRoleToScene(dict)',
                         'NSDictionary*', 'dict')
        # roleChange
        self._map_method('roleChange',
                         'UNBridge::getInstance()->onRoleChanged(dict)',
                         'NSDictionary*', 'dict')
        # sendDefaultSid
        self._map_method('sendDefaultSid',
                         'UNBridge::getInstance()->onUsrToServer(dict)',
                         'NSDictionary*', 'dict')
        # tcBindPlayerGift
        self._map_method('tcBindPlayerGift',
                         'UNBridge::getInstance()->onRoleUseGift(dict)',
                         'NSDictionary*', 'dict')
        # initPushMessage
        self._map_method('initPushMessage',
                         'UNBridge::getInstance()->onSettingPush(dict)',
                         'NSDictionary*', 'dict')

        # registerScriptHandler
        self._map_method('registerScriptHandler',
                         'UNBridge::getInstance()->registStaticMethod(dict)',
                         'NSDictionary*', 'dict')
        # getopId
        self._map_method('getopId',
                         'UNBridge::getInstance()->onGetUzoneOPID(dict)',
                         'NSDictionary*', 'dict')
        # getBundleId
        self._map_method('getBundleId',
                         'UNBridge::getInstance()->onGetPackageID(dict)',
                         'NSDictionary*', 'dict')
        # getGameVersion
        self._map_method('getGameVersion',
                         'UNBridge::getInstance()->onGetPackageVersion(dict)',
                         'NSDictionary*', 'dict')
        # getEquipmentModel
        self._map_method('getEquipmentModel',
                         'UNBridge::getInstance()->onGetDeviceModel(dict)',
                         'NSDictionary*', 'dict')
        # getSystemVersion
        self._map_method('getSystemVersion',
                         'UNBridge::getInstance()->onGetSystemVersion(dict)',
                         'NSDictionary*', 'dict')
        # pasteboardString
        self._map_method('pasteboardString',
                         '[UIPasteboard generalPasteboard].string = dict[@"key"]',
                         'NSDictionary*', 'dict')

        # # levelUp
        # self._map_method('levelUp', None, 'NSString*', 'levelUpJson')
        # # enterPayViewFrom
        # self._map_method('enterPayViewFrom', None, 'NSDictionary*', 'dict')
        # # openWeChatShare
        # self._map_method('openWeChatShare', None, 'NSDictionary*', 'dict')

        # # getMobileOperator
        # self._map_method('getMobileOperator',
        #                  'JLuabridge::callTempMehtod(dict, JUniteHelper::getNetOperator())',
        #                  'NSDictionary*', 'dict')
        # # getMobileNetwork
        # self._map_method('getMobileNetwork',
        #                  'JLuabridge::callTempMehtod(dict, JUniteHelper::getNetType())',
        #                  'NSDictionary*', 'dict')
        # # getisNewUser
        # self._map_method('getisNewUser',
        #                  'JLuabridge::callTempMehtod(dict, JUniteHelper::isNewUser())',
        #                  'NSDictionary*', 'dict')
        # # getUUID
        # self._map_method('getUUID',
        #                  'JLuabridge::callTempMehtod(dict, JUniteHelper::getUUID())',
        #                  'NSDictionary*', 'dict')
        # # getIDFA
        # self._map_method('getIDFA',
        #                  'JLuabridge::callTempMehtod(dict, JUniteHelper::getADID())',
        #                  'NSDictionary*', 'dict')


        # # LoginFinished
        # self.__add__meth('LoginFinished',
        #                  'JLuabridge::callStaticMethod(JLuabridge::loginFinshed, loginData)',
        #                  'NSString*', 'loginData')
        # # # gameLogout
        # self.__add__meth('gameLogout',
        #                  'JLuabridge::callStaticMethod(JLuabridge::gameLogout, @"true")')
        # # onWeChatShareFinished
        # self.__add__meth('onWeChatShareFinished',
        #                  'JLuabridge::callStaticMethod(JLuabridge::WeChatShareFinished, jsonStr)',
        #                  'NSString*', jsonStr)
        # # getResVersion
        # self.__add__meth('getResVersion',
        #                  'JLuabridge::callStaticMethod(JLuabridge::getResVersion, @" ")')
        # # getSDKLoginState
        # self.__add__meth('getSDKLoginState',
        #                  'JLuabridge::callStaticMethod(JLuabridge::getSDKLoginState, @"true")')
        # # hideLoadingLayer
        # self.__add__meth('hideLoadingLayer',
        #                  'JLuabridge::callStaticMethod(JLuabridge::hideLoadingLayer, @"true")')

    def __sort__methods(self):
        temps = self.methods
        self.methods = []
        while len(temps) > 0:
            i = int(random.random() * len(temps))
            self.methods.append(temps[i])
            del temps[i]

    def _map_method(self, name, statement, argTypes = None, argNames = None):
        notice = JOcHelper.var(self._api_map.values())
        self._api_map[name] = notice
        method = JOcMethod(self)
        method.scope = '+'
        method.ret = 'void'
        method.messages.append(notice)
        if argTypes is not None:
            method.argTypes = [argTypes]
        if argNames is not None:
            method.argNames = [argNames]
        if statement is not None:
            method.lineTree = self._gen_line(method, statement)
        self.methods.append(method)

    def _gen_line(self, method, statement):
        line = JOcLineTree(method)
        temp = [statement + ';']
        for i in range(random.randint(1, 5)):
            temp.append(JOcHelper.getOCSingleton() + ';')
        stats = []
        while len(temp) > 0:
            i = int(random.random() * len(temp))
            stats.append(temp[i])
            del temp[i]
        for ste in stats:
            line.statements.append(ste)
        return line