# -*- coding: utf-8 -*-
# @Time    : 2021/1/22 12:10 PM
# @Author  : Joli
# @Email   : 99755349@qq.com
import json
import os
from jonlin.utils import FS

class DeDMXKL:  # 大明侠客令
    def __init__(self):
        pass

    def de_json(self):
        # from jonlin.utils import FS
        # gameini = json.loads(FS.read_text('/Users/joli/Downloads/gameini.json'))
        # inidir = '/Users/joli/Downloads/gameini'
        # for key in gameini:
        #     val = gameini[key]
        #     FS.write_text(os.path.join(inidir, key + '.json'), json.dumps(val, indent='\t', ensure_ascii=False))
        # print('done')

        # gameini = json.loads(FS.read_text('/Users/joli/Downloads/event_dialogue.json'))
        # dataparts = gameini.get('data').split('$')
        # datakeys = gameini.get('key').split(',')
        # datatyps = gameini.get('type').split(',')
        # parsekeys = gameini.get('parseKey').split(',')
        # parsetyps = gameini.get('parseType').split(',')

        jdir = '/Users/joli/Downloads/gameini'
        outdir = '/Users/joli/Downloads/gameini1'
        for fn in os.listdir('/Users/joli/Downloads/gameini'):
            if fn.endswith('.json'):
                print('-----------', fn)
                sheet = self.de_sheet(FS.read_text(os.path.join(jdir, fn)))
                # print(sheet)
                sheet = json.dumps(sheet, indent='\t', ensure_ascii=False)
                FS.write_text(os.path.join(outdir, fn), sheet)
        print('done')

    @staticmethod
    def toint(v):
        try:
            return int(v)
        except:
            pass

    @staticmethod
    def tofloat(v):
        try:
            return float(v)
        except:
            pass

    def de_sheet(self, source):
        sheet = []
        jo = json.loads(source)
        data_vals = jo.get('data').split('$')
        data_keys = jo.get('key').split(',')
        data_types = jo.get('type').split(',')
        data_end = len(data_keys) - 1
        parse_keys, parse_types = None, None
        if 'parseKey' in jo:
            parse_keys = jo.get('parseKey').split(',')
        if 'parseType' in jo:
            parse_types = jo.get('parseType').split(',')
        ki, line = 0, None
        for i in range(len(data_vals)):
            if ki == 0:
                line = {}
                sheet.append(line)
            t = int(data_types[ki])
            k = data_keys[ki]
            v = data_vals[i]
            if t == 1:
                line[k] = self.toint(v)
            elif t == 2:
                line[k] = self.tofloat(v)
            elif t == 3:
                if parse_keys and v.find('&') != -1:
                    ss = v.split('&')
                    sd = {}
                    for n in range(len(ss)):
                        st = int(parse_types[n])
                        sv = ss[n]
                        sk = parse_keys[n]
                        if st == 1:
                            sd[sk] = self.toint(sv)
                        elif st == 2:
                            sd[sk] = self.tofloat(sv)
                        elif st == 3:
                            sd[sk] = sv
                        else:
                            sd[sk] = sv
                    line[k] = sd
                else:
                    line[k] = v
            else:
                line[k] = v
            if ki == data_end:
                ki = 0
            else:
                ki += 1
        return sheet