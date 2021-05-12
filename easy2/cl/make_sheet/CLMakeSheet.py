# -*- coding: utf-8 -*-
# @Time    : 2019/11/1 11:13 PM
# @Author  : Joli
# @Email   : 99755349@qq.com
import os
import sys
import optparse
from scripts.MakeSheet import ConfigExportor, TargetRequest

def do_test():
    server_dir = ''
    client_dir = ''
    excels_dir = ''
    ConfigExportor().export(excels_dir=excels_dir,
                            excels_manifest=os.path.join(excels_dir, '0.manifest'),
                            client_data_dir=client_dir,
                            client_data_format=ConfigExportor.SINGLE_JSON_LINE,
                            client_code_dir=os.path.join(self.root, 'excel/clientclass'),
                            client_template='/Users/joli/Work/StonePro/stonedocs/Tools/MakeSheet/template_csharp.json',
                            server_data_dir=server_dir,
                            server_date_format=ConfigExportor.SINGLE_BINARY,
                            server_code_dir=None,
                            server_template=None,
                            interruptible=False)

def do_export(opts):
    client = TargetRequest()
    client.data_dir = opts.ClientDataDir
    client.data_fmt = opts.ClientDataFormat
    client.code_dir = opts.ClientClassDir
    client.code_template = opts.ClientClassTemplate
    client.dejson = opts.ClientDejson
    server = TargetRequest()
    server.data_dir = opts.ServerDataDir
    server.data_fmt = opts.ServerDataFormat
    server.code_dir = opts.ServerClassDir
    server.code_template = opts.ServerClassTemplate
    server.dejson = opts.ServerDejson
    ConfigExportor().export(opts.ExcelsDir, opts.Manifest, client, server, opts.interruptible)

def main():
    parser = optparse.OptionParser(description='make sheet tool')
    parser.add_option('-i',
                      dest='ExcelsDir',
                      type='string',
                      default=optparse.NO_DEFAULT,
                      help='Excel文件夹')
    parser.add_option('-m',
                      dest='Manifest',
                      type='string',
                      default=optparse.NO_DEFAULT,
                      help='Excel修改记录清单，用于增量导表。')
    parser.add_option('--CDD',
                      dest='ClientDataDir',
                      type='string',
                      default=optparse.NO_DEFAULT,
                      help='前端数据目录')
    parser.add_option('--CDF',
                      dest='ClientDataFormat',
                      type='string',
                      default=optparse.NO_DEFAULT,
                      help='前端数据格式[packet_binary, single_binary, packet_json, single_json, single_json_line]')
    parser.add_option('--CCD',
                      dest='ClientClassDir',
                      type='string',
                      default=optparse.NO_DEFAULT,
                      help='前端代码目录')
    parser.add_option('--CCT',
                      dest='ClientClassTemplate',
                      type='string',
                      default=optparse.NO_DEFAULT,
                      help='前端代码模版')
    parser.add_option('--clientdejson',
                      dest='ClientDejson',
                      action="store_true",
                      default=False,
                      help='前段是否展开json')
    parser.add_option('--SDD',
                      dest='ServerDataDir',
                      type='string',
                      default=optparse.NO_DEFAULT,
                      help='后端数据目录')
    parser.add_option('--SDF',
                      dest='ServerDataFormat',
                      type='string',
                      default=optparse.NO_DEFAULT,
                      help='后端数据格式[packet_binary, single_binary, packet_json, single_json, single_json_line]')
    parser.add_option('--SCD',
                      dest='ServerClassDir',
                      type='string',
                      default=optparse.NO_DEFAULT,
                      help='后端代码目录')
    parser.add_option('--SCT',
                      dest='ServerClassTemplate',
                      type='string',
                      default=optparse.NO_DEFAULT,
                      help='后端代码模版')
    parser.add_option('--serverdejson',
                      dest='ServerDejson',
                      action="store_true",
                      default=False,
                      help='后端是否展开json')
    parser.add_option('--interruptible',
                      dest='interruptible',
                      action="store_true",
                      default=False,
                      help='错误立即中断')
    (opts, args) = parser.parse_args(sys.argv[1:])
    if opts and opts.ExcelsDir:
        do_export(opts)
    else:
        do_test()


if __name__ == '__main__':
    main()