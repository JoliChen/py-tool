# -*- coding: UTF-8 -*-
# 欲盖弥彰

import random

from XcHelper.common.WordUtils import JWords
from XcHelper.garbages.source.cpp.reference.cheat.CheatExtension import JThirdPartyNetApi
from XcHelper.garbages.source.oc.OCGrammar import ST, SN


class JCheatMaker:
    _net_io_size = (1, 3)
    _disk_i_size = (1, 15)
    _disk_o_size = (1, 5)
    _net_io_func = 'checkNetwork'
    _disk_i_func = 'preloadRes'
    _disk_o_func = 'cacheTempData'
    _assets_func = 'injectAssets'
    _script_func = 'injectScript'

    @classmethod
    def get_net_io_func(cls):
        return cls._net_io_func

    @classmethod
    def get_disk_i_func(cls):
        return cls._disk_i_func

    @classmethod
    def get_disk_o_func(cls):
        return cls._disk_o_func

    @classmethod
    def get_assets_func(cls):
        return cls._assets_func

    @classmethod
    def get_script_func(cls):
        return cls._script_func

    # 网络请求欺骗函数
    @classmethod
    def cheat_net_io(cls, ref, indent=1):
        weight = random.randint(cls._net_io_size[0], cls._net_io_size[1])
        node = None
        func = None
        for i in range(weight, 0, -1):
            if (i != 1):
                func = JWords.hump(8, 16)
            else:
                func = cls._net_io_func
            # tim = round(random.random() * (10 * i) + 0.3, 2)
            tim = max(round(random.random() * 10, 2), 1)
            req = JThirdPartyNetApi.randReq()
            ref.add_function(func, cls._cheat_net_io_implement(node, req, tim, indent))
            node = func
    # 网络请求欺骗函数实现
    @classmethod
    def _cheat_net_io_implement(cls, node, request, time, indent):
        s = ''
        s += ST(indent) + 'dispatch_time_t t = dispatch_time(DISPATCH_TIME_NOW,' + str(
            time) + '*NSEC_PER_SEC);' + SN
        s += ST(
            indent) + 'dispatch_after(t, dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^ {' + SN

        var_args = JWords.hump(6, 9)
        s += ST(indent + 1) + 'NSDictionary *' + var_args + ' = nil;' + SN
        args_var = request['args']
        if (args_var is not None):
            s += ST(indent + 1) + var_args + ' = [NSDictionary dictionaryWithObjectsAndKeys:' + SN
            for k in args_var:
                v = args_var[k]
                s += ST(indent + 2) + '@"' + str(v) + '", ' + '@"' + k + '", ' + SN
            s += ST(indent + 1) + 'nil];' + SN

        s += ST(indent + 1) + ('__http_GET' if ('UBGET' == request['method']) else '__httpPOST')
        s += '(@"' + request['url'] + '", ' + var_args + ', ^(NSData* data, NSURLResponse *resp) {' + SN
        if node is None:
            s += ST(indent + 2) + 'NSLog(@"check net done");' + SN
        else:
            s += ST(indent + 2) + node + '();' + SN
        s += ST(indent + 1) + '});' + SN

        s += ST(indent) + '});' + SN
        return s

    # 硬盘输出欺骗函数
    @classmethod
    def cheat_disk_output(cls, ref, indent=1):
        weight = random.randint(cls._disk_o_size[0], cls._disk_o_size[1])
        config = {}
        for i in range(weight):
            n = None
            while (True):
                n = JWords.hump(32, 64)
                if (n not in config):
                    break
            config[n] = random.randint(1, 20000)
        ref.add_function(cls._disk_o_func, cls._cheat_disk_output_implement(config, indent))
    # 硬盘输出欺骗函数实现
    @classmethod
    def _cheat_disk_output_implement(cls, config, indent):
        s = ''
        s += ST(indent) + 'NSString *doc_root = NSSearchPathForDirectoriesInDomains' \
                          '(NSDocumentDirectory, NSUserDomainMask, YES)[0];' + SN
        s += ST(indent) + 'NSString *tmp_path = nil;' + SN + SN
        for f in config:
            w = config[f]
            s += ST(indent) + 'tmp_path = [NSString stringWithFormat:@"%@/%s", doc_root, "' + f + '"];' + SN
            s += ST(indent) + 'if (![[NSFileManager defaultManager] fileExistsAtPath:tmp_path]) {' + SN
            s += ST(indent + 1) + '__saveFile(tmp_path, __makeText(' + str(w) + ')' + str(random.randint(512, 2048)) + ');' + SN
            s += ST(indent) + '}' + SN
        return s

    # 硬盘读取欺骗函数
    @classmethod
    def cheat_disk_input(cls, ref, assets_info, indent=1):
        if (assets_info is None) or (assets_info.garbage_list is None):
            ref.add_function(cls._disk_i_func, '')
            return
        weight = min(len(assets_info.garbage_list), random.randint(cls._disk_i_size[0], cls._disk_i_size[1]))
        config = []
        junks_copy = assets_info.garbage_list[:]
        for i in range(weight):
            n = random.choice(junks_copy)
            junks_copy.remove(n)
            config.append(n)
        ref.add_function(cls._disk_i_func, cls._cheat_disk_input_implement(config, indent))
    # 硬盘读取欺骗函数实现
    @classmethod
    def _cheat_disk_input_implement(cls, config, indent):
        s = ''
        s += ST(indent) + 'NSString *tmp_path = nil;' + SN
        for f in config:
            s += ST(indent) + 'tmp_path = [[NSBundle mainBundle] pathForResource:@"' + f + '" ofType:nil];' + SN
            s += ST(indent) + 'if (tmp_path) {' + SN
            s += ST(indent + 1) + '__readFile(tmp_path, ' + str(random.randint(256, 2048)) + ');' + SN
            s += ST(indent) + '}' + SN
        return s

    # 注入资源配置
    @classmethod
    def inject_assets(cls, ref, assets_info, indent=1):
        if (assets_info is None) or ((assets_info.package_list is None) and (assets_info.mapping_dict is None)):
            ref.add_function(cls._assets_func, '')
            return
        # ref.add_header_to_implement('ABKit.h')
        s = cls._inject_assets_implement(assets_info.package_list, assets_info.mapping_dict, indent)
        ref.add_function(cls._assets_func, s)
    # 注入资源配置实现
    @classmethod
    def _inject_assets_implement(cls, packages, res_map, indent):
        var_urlstr = JWords.hump(6, 9)
        var_bundle = JWords.hump(6, 9)
        s = ''
        s += ST(indent) + 'NSString* ' + var_urlstr + ' = nil;' + SN
        s += ST(indent) + 'NSBundle* ' + var_bundle + ' = [NSBundle mainBundle];' + SN
        # 注入重命名映射
        if (res_map is not None):
            dir_name_map = {
                'music':JWords.hump(6, 9),
                'bgm':JWords.hump(6, 9),
                'sound':JWords.hump(6, 9),
                'juqing':JWords.hump(6, 9),
            }
            file_suffixs = {
                '.mp3': JWords.hump(6, 9)
            }
            for d_name in dir_name_map:
                s += ST(indent) + 'const char* ' + dir_name_map[d_name] + ' = "' + d_name + '";' + SN
            for suffix in file_suffixs:
                s += ST(indent) + 'const char* ' + file_suffixs[suffix] + ' = "' + suffix + '";' + SN
            for old_name in res_map:
                res_name = cls._crypt_assets_path(old_name[4:], dir_name_map, file_suffixs) # 去除 'res/'
                new_name = res_map[old_name]
                s += ST(indent) + 'CCEngine::resMapping(' + res_name + ', "' + new_name + '");' + SN
        # 注入 assets bin
        if (packages is not None):
            for pi in packages:
                s += ST(indent) + var_urlstr + ' = [' + var_bundle + ' pathForResource:@"' + pi.pack_bin_path + '" ofType:nil];' + SN
                s += ST(indent) + 'if (' + var_urlstr + ') {' + SN
                s += ST(indent + 1) + 'CCEngine::resPackage(' + var_urlstr  + ', ' + \
                     str(pi.pack_bin_sign) + ', ' + str(pi.pack_bin_version) + ');' + SN
                s += ST(indent) + '}' + SN
        return s
    # 隐藏映射的资源路径
    @classmethod
    def _crypt_assets_path(cls, assets_path, dir_name_map, file_suffix_map):
        parts = assets_path.split('/')
        format = ''
        inputs = ''
        for part in parts:
            format += '/%s'
            if part in dir_name_map:
                inputs += ', ' + dir_name_map[part]
            else:
                pot_pos = part.find(".")
                if pot_pos != -1:
                    suffix = part[pot_pos:]
                    if suffix in file_suffix_map:
                        format += '%s'
                        inputs += ', "' + part[0:pot_pos] + '"'
                        inputs += ', ' + file_suffix_map[suffix]
                        continue
                inputs += ', "' + part + '"'
        return '[NSString stringWithFormat:@"' + format[1:] + '"' + inputs + ']'

    # 注入脚本替换接口
    @classmethod
    def inject_script(cls, ref, oc_bridge_cls, indent=1):
        if (oc_bridge_cls is None):
            ref.add_function(cls._script_func, '')
            return
        ref.add_header_to_implement('<PlayDrawkit/CCEngine.h>')
        ref.add_function(cls._script_func,
                         cls._inject_script_implement(oc_bridge_cls.className, oc_bridge_cls.get_oc_api_map(), indent))
    # 注入脚本替换接口实现
    @classmethod
    def _inject_script_implement(cls, oc_bridge_name, oc_api_map, indent):
        SSN = ' \\' + SN
        lua = 'if cc.exports then' + SSN
        lua += ST(indent + 1) + 'cc.exports.g_OCFuncNameMap = {}' + SSN
        lua += ST(indent) + 'else' + SSN
        lua += ST(indent + 1) + 'g_OCFuncNameMap = {}' + SSN
        lua += ST(indent) + 'end'  + SSN
        lua += ST(indent) + 'g_OCFuncNameMap.UniteInterface = ' + '\\"' + oc_bridge_name + '\\"' + SSN
        for oc in oc_api_map:
            lua += ST(indent) + 'g_OCFuncNameMap.' + oc + ' = ' + '\\"' + oc_api_map[oc] + '\\"' + SSN
        lua = lua[:-3]  # 去除最后的追加符号

        var_script = JWords.hump(6, 9)
        s = ''
        s += ST(indent) + 'const char* ' + var_script + ' = "' + lua + '";' + SN
        s += ST(indent) + 'CCEngine::eval(' + var_script + ');' + SN
        s += '#if defined(DEBUG)' + SN
        s += ST(indent) + 'CCEngine::eval("print = release_print");' + SN
        s += '#else' + SN
        s += ST(indent) + 'CCEngine::eval("print = function(...) end");' + SN
        s += ST(indent) + 'CCEngine::eval("release_print = function(...) end");' + SN
        s += '#endif' + SN
        return s