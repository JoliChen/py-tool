# -*- coding: utf-8 -*-
# @Time    : 2019/10/25 4:19 PM
# @Author  : Joli
# @Email   : 99755349@qq.com
import gc
import os
import sys
import re
import json
import time

import demjson
import xlrd
from jonlin.utils import FS, Log, Bit

LOG = Log.Logger(__file__)

def c2abc(n):
    return chr(65 + (n % 26)) * (int(n / 26) + 1)  # 将列号转成大写字母

# 流程异常
class OptError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

# 表异常
class SheetError(Exception):
    def __init__(self, excel, sheet, message):
        self.excel = excel
        self.sheet = sheet
        self.message = message

    def __str__(self):
        return f'{FS.filename(self.excel)}/{self.sheet} {self.message}'

# 格子异常
class CellError(Exception):
    def __init__(self, excel, sheet, row, col, message):
        self.excel = excel
        self.sheet = sheet
        self.message = message
        self.row = row
        self.col = col

    def __str__(self):
        return f'{FS.filename(self.excel)}/{self.sheet} [{self.row+1}:{c2abc(self.col)}] {self.message}'

# Excel信息
class ExcelInfo:
    def __init__(self, path, sheets, errors):
        self.path = path
        self.name = FS.filename(path)
        self.sheets = sheets
        self.errors = errors
        self.epxort_sheets = {}

    def check_exports(self, k_index):
        skdict = {}
        for si in self.sheets:
            keys = si.keysat(k_index)
            if not keys:
                continue
            skdict[si] = keys
        self.epxort_sheets[k_index] = skdict
        return skdict

# 数据表签名
class SheetSign:
    def __init__(self):
        self.tagcol = 0  # 标签列
        self.desc = 0  # 字段描述行
        self.client = 0  # 前端标签行
        self.server = 0  # 后端标签行
        self.vtype = 0  # 数据类型行
        self.databegin = 0  # 数据开始行
        self.dataend = 0  # 数据结束行

# 数据表信息
class SheetInfo:
    def __init__(self, name):
        self.name = name
        self.ckeys = None  # 前端键数组
        self.skeys = None  # 后端键数组
        self.descs = None  # 字段描述数组
        self.types = None  # 字段类型数组
        self.datas = None  # 数据

    def keysat(self, i):
        return (self.ckeys, self.skeys)[i]

# 字段
class SheetKey:
    def __init__(self, k, i):
        self.k = k  # 字段名称
        self.i = i  # 字段列索引

# 导出编码器
class SheetBuilder:
    def __init__(self, encoder, ext, packet=True):
        self.encoder = encoder
        self.ext = ext
        self.packet = packet

# 代码编码器
class CodeBuilder:
    def __init__(self, coder, mode, ext):
        self.coder = coder
        self.mode = mode
        self.ext = ext

# 文件夹增量导出清单
class ExcelManifest:
    def __init__(self, diskpath):
        self.excel_infos = None
        self.excel_names = []
        self.fsm = FS.FileStatManifest(diskpath)

class TargetRequest:
    def __init__(self):
        self.data_dir = ''
        self.data_fmt = ''
        self.code_dir = ''
        self.code_template = ''  # 代码模板配置路径
        self.dejson = True

# 导表工具
class ConfigExportor:
    FMT = '.xlsx'
    ID = 'Id'
    END = 'END'
    CLIENT = 'CLIENT'
    SERVER = 'SERVER'

    PACKET_BINARY = 'packet_binary'
    PACKET_JSON = 'packet_json'
    SINGLE_BINARY = 'single_binary'
    SINGLE_JSON = 'single_json'
    SINGLE_JSON_LINE = 'single_json_line'

    RE_FNAME = re.compile(r'^[A-Z][A-Za-z0-9]*?$')  # 文件名称
    RE_KNAME = re.compile(r'^[a-z][a-z0-9_]+?$', re.I)  # 键名称
    # RE_JSON = re.compile(r'^(\{|\[)(.*?)(\}|\])$', re.I | re.M | re.S)  # JSON匹配

    def __init__(self):
        self.convert_dict = {
            'int':     self.tointeger,
            'long':    self.tointeger,
            'float':   self.tofloat,
            'string':  self.totext,
            'dict':    self.tojsondict,
            'list':    self.tojsonlist,
        }
        self.maker_dict = {}
        self.coder_dict = {}
        self.unique_dict = {}  # 字段重名检查字典
        self.interruptible = False  # 是否遇到错误立即中断流程
        self.curr_excel = None
        self.curr_sheet = None

    def new_sheeterror(self, msg):
        return SheetError(self.curr_excel, self.curr_sheet, msg)

    def new_cellerror(self, row, col, msg):
        return CellError(self.curr_excel, self.curr_sheet, row, col, msg)

    def export(self, excels_dir, manifest_path, client, server, interruptible=False):
        start_t = time.time()
        if not excels_dir or not os.path.isdir(excels_dir):
            raise OptError(f'表文件夹不存在:"{excels_dir}"')
        if not client.data_dir and not server.data_dir:
            raise OptError(f'请提供至少一个目标输出文件夹')
        self.interruptible = interruptible
        LOG.i('mainfest:' + manifest_path)
        manifest = ExcelManifest(manifest_path)
        self.load_excels(excels_dir, manifest)
        if manifest.excel_infos:
            if client.data_dir:
                LOG.i('-' * 50)
                self.gen_data(manifest, self.CLIENT, client)
            if server.data_dir:
                LOG.i('-' * 50)
                self.gen_data(manifest, self.SERVER, server)
            if client.code_dir:
                LOG.i('-' * 50)
                self.gen_code(manifest, self.CLIENT, client)
            if server.code_dir:
                LOG.i('-' * 50)
                self.gen_code(manifest, self.SERVER, server)
        LOG.i('-' * 50)
        manifest.fsm.flush()
        self.dump_errors(manifest)
        LOG.i('finish %.3fs' % (time.time() - start_t))

    @staticmethod
    def dump_errors(manifest):
        for ei in manifest.excel_infos:
            for e in ei.errors:
                LOG.e(e)

    def load_excels(self, excelsdir, manifest):
        flist = []
        for fn in os.listdir(excelsdir):
            exts = os.path.splitext(fn)
            if fn.startswith('~') or exts[1] != self.FMT:
                continue
            if not self.RE_FNAME.match(exts[0]):
                # LOG.d(f'excel{{{fn}}}名称不符合规范')
                continue
            manifest.excel_names.append(exts[0])  # 不包含后缀
            fn = os.path.join(excelsdir, fn)
            if manifest.fsm.ismodified(fn):
                flist.append(fn)
        if not flist:
            LOG.w('空文件夹或没有做任何修改')
            manifest.excel_infos = []
        else:
            manifest.excel_infos = self.parse_batch(flist)

    def parse_batch(self, files):
        gc.disable()
        excel_infos = [self.parse_excel(fp) for fp in files]
        gc.enable()
        return excel_infos

    def parse_excel(self, fp):
        LOG.i(f'parse {fp}')
        self.curr_excel, sheets, errors = fp, [], []
        for sb in xlrd.open_workbook(fp, encoding_override='utf-8').sheets():
            if sb.nrows < 1 or sb.ncols < 1:
                continue
            if not self.RE_FNAME.match(sb.name):
                LOG.d(f'sheet{{{sb.name}}}名称不符合规范')
                continue
            try:
                si = self.parse_sheet(sb)
                if si:
                    sheets.append(si)
            except (SheetError, CellError) as e:
                if self.interruptible:
                    LOG.e(e)
                    sys.exit(1)
                else:
                    errors.append(e)
        LOG.d(f'sheet {len(sheets)}\terror {len(errors)}')
        return ExcelInfo(fp, sheets, errors)

    def parse_sheet(self, sb):
        self.curr_sheet = sb.name
        try:
            ss = self.check_sheet_sign(sb)
        except Exception as e:
            LOG.w(e)
            return
        si = SheetInfo(self.curr_sheet)
        cols = self.check_sheet_cols(sb, ss, si)  # 有效数据列
        if not cols:
            return
        if 'int' != si.types[0]:
            LOG.e(f'{self.curr_sheet} {self.ID}列的数据类型必须为int')
            return
        si.datas = self.parse_sheet_data(sb, ss, si.types, cols)
        return si

    def check_sheet_sign(self, sb):
        client = self.check_sheed_client(sb)
        if client is None:
            raise self.new_sheeterror(f'未找到{{{self.CLIENT}}}标签')
        begin = client[0] + 3  # 数据起始行
        if sb.nrows <= begin:
            raise self.new_sheeterror(f'有效行数太少')
        server = client[0] + 2
        if not self.isserver(sb.cell_value(server, client[1])):
            raise self.new_sheeterror(f'未找到{{{self.SERVER}}}标签')
        end = self.check_sheet_end(sb, begin, client[1])
        if 0 == end:
            raise self.new_sheeterror(f'只有一行数据必须添加{{{self.END}}}标签')
        ss = SheetSign()
        ss.tagcol = client[1]
        ss.desc = client[0] - 1
        ss.client = client[0]
        ss.server = server
        ss.vtype = client[0] + 1
        ss.databegin = begin
        ss.dataend = end
        return ss

    def check_sheed_client(self, sb):
        for r in range(sb.nrows):
            for c in range(sb.ncols):
                if self.isclient(sb.cell_value(r, c)):
                    return r, c

    def check_sheet_end(self, sb, row, col):
        end = sb.nrows
        for r in range(row, end):
            if self.isend(sb.cell_value(r, col)):
                return r + 1
        return 0 if end - row == 1 else end  # 只有一行数据的情况下，必须填END标签，否则不会导出。

    def check_sheet_cols(self, sb, ss, si):
        i, cid, sid, cols, descs, types, ckeys, skeys = 0, False, False, [], [], [], [], []
        for c in range(ss.tagcol + 1, sb.ncols):
            t = self.totype(sb.cell_value(ss.vtype, c))
            if not t:
                continue
            ck = self.tokey(sb.cell_value(ss.client, c))
            sk = self.tokey(sb.cell_value(ss.server, c))
            if not ck and not sk:
                continue
            if ck:
                ckeys.append(SheetKey(ck, i))
            if sk:
                skeys.append(SheetKey(sk, i))
            descs.append(str(sb.cell_value(ss.desc, c)))
            types.append(t)
            cols.append(c)
            i += 1
        ckeys = self.check_sheet_keys(ckeys, self.CLIENT)
        skeys = self.check_sheet_keys(skeys, self.SERVER)
        if not ckeys and not skeys:
            return
        si.types = types
        si.ckeys = ckeys
        si.skeys = skeys
        si.descs = descs
        return cols

    def check_sheet_keys(self, keys, target):
        if len(keys) < 2:
            LOG.w(f'{target} 至少需要两列有效字段才能导出')
            return
        if keys[0].k != self.ID:
            if keys[0].k:
                LOG.w(f'{self.curr_sheet} {target} 第一列字段 {keys[0].k}!={self.ID}')
            return
        dic = self.unique_dict
        dic.clear()
        for k in keys:
            n = k.k
            if n not in dic:
                dic[n] = k
                continue
            raise self.new_sheeterror(f'{target} {c2abc(dic[n].i)}与{c2abc(k.i)}字段重名')
        return keys

    def parse_sheet_data(self, sb, ss, types, cols):
        ncols, nrows = len(cols), ss.dataend - ss.databegin
        array = [[0] * ncols for i in range(nrows)]
        lines = self.check_sheet_ids(sb, ss, array, cols[0], types[0])
        riter = range(len(lines))
        for i in range(1, ncols):  # ID列已经解析完了，无需再解析一遍。
            c, t = cols[i], types[i]
            f = self.convert_dict[t]
            for j in riter:
                r = lines[j]
                v = f(sb.cell_value(r, c))
                if v is None:
                    raise self.new_cellerror(r, c, f'{{{sb.cell_value(r, c)}}}不是{t}类型')
                array[j][i] = v
        return array

    def check_sheet_ids(self, sb, ss, data, c, t):
        rows, unique, i = [], self.unique_dict, 0
        unique.clear()
        for r in range(ss.databegin, ss.dataend):
            v = self.toid(sb.cell_value(r, c), t)
            if v is None:
                LOG.w(f'{sb.name} [{r}:{c}] {self.ID}{{{sb.cell_value(r, c)}}}不是{t}类型')
                data.pop(i)  # 删除没有ID的行
                continue
            if v in unique:
                raise self.new_cellerror(r, c, f'{self.ID}{{{v}}}重复')
            unique[v] = True
            rows.append(r)
            data[i][0] = v
            i += 1
        return rows

    def toid(self, v, t):
        if t == 'int' or t == 'long':
            return self.guessint(v)
        if t == 'string':
            return self.totext(v)  # 字符串需要兼容填数字的情况。
        raise OptError(f'未支持的ID类型{t}')

    def tointeger(self, v):
        i = self.guessint(v)
        if i is not None:
            return i
        i = self.guesstext(v)
        if (i is not None) and ('' == i):
            return 0  # 空格的转为0

    def tofloat(self, v):
        f = self.guessfloat(v)
        if f is not None:
            return f
        f = self.guesstext(v)
        if (f is not None) and ('' == f):
            return 0  # 空格的转为0

    def totext(self, v):
        s = self.guesstext(v)
        if s is not None:
            return s
        v = self.guessfloat(v)
        if v is not None:
            i = int(v)
            return str(i if i == v else v)  # 将数字转成字符串，小数点后是0会被转成整数。如：1.0, 2.0

    def tojsondict(self, v):
        s = self.guesstext(v)
        if s is None:
            return {}  # 兼容填空的情况
        s = self.guessjson(s)
        return {} if s is None else s

    def tojsonlist(self, v):
        s = self.guesstext(v)
        if s is None:
            return []  # 兼容填空的情况
        s = self.guessjson(s)
        return [] if s is None else s

    def toarray(self, v):
        s = self.guesstext(v)
        if s is None:
            return []  # 兼容填空的情况
        v = self.guessjson(v)
        return [] if v is None else v

    @staticmethod
    def guessint(v):
        try:
            return int(v)
        except ValueError:
            pass

    @staticmethod
    def guessfloat(v):
        try:
            return float(v)
        except ValueError:
            pass

    @staticmethod
    def guesstext(v):
        return v.strip() if isinstance(v, str) else None

    @staticmethod
    def guessjson(v):
        try:
            return demjson.decode(v)
        except demjson.JSONDecodeError:
            pass

    def tokey(self, v):
        if not isinstance(v, str):
            return
        v = v.strip()
        return v if self.RE_KNAME.match(v) else None

    def totype(self, t):
        if not isinstance(t, str):
            return
        t = t.strip().lower()
        if not t:
            return
        if t in self.convert_dict:
            return t
        if t.endswith('[]'):
            self.convert_dict[t] = self.toarray
            return t

    # def create_array_convert(self, v):
    #     t, d, i = '', 0, len(v)-1
    #     while i > -1:
    #         c = v[i]
    #         if c == ']':
    #             if v[i-1] != '[':
    #                 return
    #             d += 1
    #             i += 2
    #             continue
    #         t = v[0: i]
    #         break
    #     return lambda x: self.toarray(x, t, d)

    def isclient(self, v):
        return v.strip().upper() == self.CLIENT if isinstance(v, str) else False

    def isserver(self, v):
        return v.strip().upper() == self.SERVER if isinstance(v, str) else False

    def isend(self, v):
        return v.strip().upper() == self.END if isinstance(v, str) else False

    def gen_data(self, manifest, target, req):
        LOG.i(f'make data {target} {req.data_dir}')
        if not os.path.isdir(req.data_dir):
            os.makedirs(req.data_dir)
        # 导出修改的Excel
        builder, k_index = self.get_data_builder(req.data_fmt), self.get_keyindex(target)
        for ei in manifest.excel_infos:
            sk_dict = ei.check_exports(k_index)
            if not sk_dict:
                continue
            if not builder.packet:
                for si, keys in sk_dict.items():
                    if not req.dejson:
                        self._json_to_string(si)  # 强语言不支持自动展开json，所以讲json对象转成字符串。
                    data = builder.encoder.pack_one(si, keys)
                    if not data:
                        continue
                    fp = os.path.join(req.data_dir, si.name + builder.ext)
                    LOG.d(f'export {target} {fp}')
                    with open(fp, 'wb') as f:
                        f.write(data)
            else:
                data = builder.encoder.pack_all(sk_dict)
                if not data:
                    continue
                fp = os.path.join(req.data_dir, ei.name + builder.ext)
                LOG.d(f'export {target} {fp}')
                with open(fp, builder.mode) as f:
                    f.write(data)
                # LOG.i(f'sheets {len(smap)}')
        # Excel被删除后对应的导出文件也要删除
        if builder.packet:
            for fn in os.listdir(req.data_dir):
                exts = os.path.splitext(fn)
                if exts[1] != builder.ext:
                    continue
                if exts[0] in manifest.excel_names:
                    continue
                LOG.d(f'{target} remove {fn}')
                os.remove(os.path.join(req.data_dir, fn))
        # 导出文件丢失需要重新导出 (未完待续...)

    def gen_code(self, manifest, target, req):
        LOG.i(f'make code {target} {req.code_dir}')
        template = json.loads(FS.read_text(req.code_template))
        if not os.path.isdir(req.code_dir):
            os.makedirs(req.code_dir)
        k_index = self.get_keyindex(target)
        for ei in manifest.excel_infos:
            sk_dict = ei.epxort_sheets[k_index]
            if not sk_dict:
                continue
            for si, keys in sk_dict.items():
                data = self.build_class_template(template, si, keys)
                if not data:
                    continue
                fp = os.path.join(req.code_dir, si.name + template['ext'])
                LOG.d(f'class {target} {fp}')
                with open(fp, 'wb') as f:
                    f.write(data)

    @staticmethod
    def _json_to_string(si):
        for c in range(len(si.types)):
            t = si.types[c]
            if t == 'list' or t == 'dict':
                for r in range(len(si.datas)):
                    si.datas[r][c] = json.dumps(si.datas[r][c], ensure_ascii=False)

    @staticmethod
    def build_class_template(template, si, keys):
        tlist = []
        tmapping = template['types']
        for i in range(len(si.types)):
            t = si.types[i]
            if t in tmapping:
                tlist.append(tmapping[t])
            else:
                tlist.append(t)
        fed = [template['fieldTemplate'] % {'type': tlist[k.i], 'name': k.k} for k in keys]
        s = template['classTemplate'] % {'ClassName': si.name, 'FieldList': '\n'.join(fed)}
        return s.encode(encoding='utf-8')

    def get_keyindex(self, target):
        if target == self.CLIENT:
            return 0
        if target == self.SERVER:
            return 1
        raise OptError(f'未支持的导出平台{target}')

    def get_data_builder(self, fmt):
        builder = self.maker_dict.get(fmt)
        if builder is not None:
            return builder
        if fmt == self.PACKET_BINARY:
            builder = SheetBuilder(BinaryEncoder(), '.bytes')
        elif fmt == self.SINGLE_BINARY:
            builder = SheetBuilder(BinaryEncoder(), '.bytes', packet=False)
        elif fmt == self.PACKET_JSON:
            builder = SheetBuilder(JsonEncoder(), '.json')
        elif fmt == self.SINGLE_JSON:
            builder = SheetBuilder(JsonEncoder(), '.txt', packet=False)
        elif fmt == self.SINGLE_JSON_LINE:
            builder = SheetBuilder(JsonLineEncoder(), '.txt', packet=False)
        else:
            raise OptError(f'未支持的编码格式{fmt}')
        self.maker_dict[fmt] = builder
        return builder

# 二进制格式导出
class BinaryEncoder:
    def __init__(self):
        self.writer_dict = {
            'int':      self._write_int,
            'long':     self._write_long,
            'float':    self._write_float,
            'string':   self._write_text,
            'dict':     self._write_json,
            'list':     self._write_json,
        }
        self.itypes = {
            'int': 1,
            'long': 2,
            'float': 3,
            'string': 4,
            'list': 5,
            'dict': 6,
            'bool': 7,
            'null': 8
        }
        self.RE_ESCAPED = re.compile(r'(\\)(n|r|t|f|v|a|b|e)', re.M | re.S)  # 字符串转义符号

    def pack_all(self, source):
        ba = Bit.ByteArray().init_capacity(1024 * 1024 * 2)
        ba.write_u16(len(source))  # 写入表的数量
        for si, keys in source.items():
            buff = self.pack_one(si, keys)
            size = len(buff)
            ba.write_utf8(si.name)
            ba.write_u32(size)
            ba.write_bytes(buff, size)
        return ba.slim_buffer()

    def pack_one(self, si, keys):
        ncols, nrows = len(keys), len(si.datas)
        ba = Bit.ByteArray().init_capacity(ncols * nrows * 32)
        ba.write_u16(nrows)
        ba.write_u8(ncols)
        for k in keys:
            c = k.i
            t = si.types[c]
            if t.endswith('[]'):
                f = self._write_json
            else:
                f = self.writer_dict[t]
            ba.write_utf8(k.k)  # 字段
            ba.write_u8(self.itypes[t])  # 类型
            for line in si.datas:
                f(ba, line[c])
        return ba.slim_buffer()

    @staticmethod
    def _write_int(ba, v):
        ba.write_int(v)

    @staticmethod
    def _write_long(ba, v):
        ba.write_longlong(v)

    @staticmethod
    def _write_float(ba, v):
        ba.write_double(v)  # float 不精确，这里使用double。

    def _write_text(self, ba, v):
        ba.write_utf8(self._escape(v))

    # def _write_json(self, ba, v):
    #     if not v:
    #         ba.write_utf8('')
    #     else:
    #         self._write_text(ba, json.dumps(v))

    def _write_json(self, ba, v):
        if isinstance(v, str):
            if v:
                ba.write_u8(self.itypes['string'])
                self._write_text(ba, v)
            else:
                ba.write_u8(self.itypes['null'])
        elif isinstance(v, int):
            if v > 2147483647 or v < -2147483648:
                ba.write_u8(self.itypes['long'])
                self._write_long(ba, v)
            else:
                ba.write_u8(self.itypes['int'])
                self._write_int(ba, v)
        elif isinstance(v, float):
            ba.write_u8(self.itypes['float'])
            self._write_float(ba, v)
        elif isinstance(v, bool):
            ba.write_u8(self.itypes['bool'])
            ba.write_byte(1 if v else 0)
        elif isinstance(v, list):
            ba.write_u8(self.itypes['list'])
            ba.write_u8(len(v))
            for i in v:
                self._write_json(ba, i)
        elif isinstance(v, dict):
            ba.write_u8(self.itypes['dict'])
            ba.write_u8(len(v))
            for k, i in v.items():
                self._write_json(ba, k)
                self._write_json(ba, i)
        else:
            raise OptError(f'未支持的json元素类型{v}')

    def _escape(self, s):
        return self.RE_ESCAPED.sub(lambda m: eval(repr(m.group(0)).replace('\\\\', '\\')), s)

# JSON格式导出
class JsonEncoder:
    def __init__(self):
        pass

    def pack_all(self, source):
        obj = {si.name: self.gen_sheet(si, keys) for si, keys in source.items()}
        txt = json.dumps(obj, ensure_ascii=False, indent='\t')
        return txt.encode(encoding='utf-8')

    def pack_one(self, si, keys):
        txt = json.dumps(self.gen_sheet(si, keys), ensure_ascii=False, indent='\t')
        return txt.encode(encoding='utf-8')

    @staticmethod
    def gen_sheet(si, keys):
        return [{k.k: line[k.i] for k in keys} for line in si.datas]

# 每行JSON格式
class JsonLineEncoder:
    def __init__(self):
        pass

    def pack_all(self, source):
        pass  # 这种格式无法导出

    def pack_one(self, si, keys):
        txt = '\n'.join([json.dumps(self.gen_line(line, keys), ensure_ascii=False) for line in si.datas])
        return txt.encode(encoding='utf-8')

    @staticmethod
    def gen_line(line, keys):
        return {k.k: line[k.i] for k in keys}