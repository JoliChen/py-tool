# -*- coding: utf-8 -*-
# @Time    : 2018/11/13 上午11:27
# @Author  : Joli
# @Email   : 99755349@qq.com
import json
import math
import os
import sys
import re
import shutil
import time
import demjson
import xlrd
from jonlin.utils import Log, Bit, FS, Collect, Text

log = Log.Logger(__file__)

VERSION = 8

class _Fmt:
    NO_DIFF_FLAG = 1
    _RE_WORD = re.compile(r'^[a-z]+?[0-9a-z_]+?$', re.I)
    _RE_JSON = re.compile(r'^(\{|\[)(.*?)(\}|\])$', re.I | re.M | re.S)
    _RE_ESCAPED = re.compile(r'(\\)(n|r|t|f|v|a|b|e)', re.M | re.S)  # 字符串转义符号
    _TAG_TAYPES = ('int', 'long', 'string', 'float', 'json')
    _TAG_CLIENT = 'CLIENT'
    _TAG_SERVER = 'SERVER'
    _TAG_END = 'END'

    @classmethod
    def is_client_tag(cls, text):
        if isinstance(text, str):
            text = text.strip()
            return text and (text.upper() == cls._TAG_CLIENT)

    @classmethod
    def is_server_tag(cls, text):
        if isinstance(text, str):
            text = text.strip()
            return text and (text.upper() == cls._TAG_SERVER)

    @classmethod
    def is_end_tag(cls, text):
        if isinstance(text, str):
            text = text.strip()
            return text and (text.upper() == cls._TAG_END)

    @classmethod
    def to_cast(cls, text, errors):
        if not isinstance(text, str):
            errors.append('incorrect type：' + str(text))
            return
        text = text.strip()
        if not text:
            return
        l_t = text.lower()
        if l_t not in cls._TAG_TAYPES:
            errors.append('incorrect type：' + text)
        else:
            return l_t

    @classmethod
    def to_word(cls, text, errors):
        if not isinstance(text, str):
            errors.append('incorrect key：' + str(text))
            return
        text = text.strip()
        if not text:
            return
        if not cls._RE_WORD.match(text):
            errors.append('incorrect key：' + text)
        else:
            return text

    @staticmethod
    def to_float(value):
        try:
            return float(value)
        except ValueError:
            pass

    @staticmethod
    def to_int(value):
        try:
            return int(value)
        except ValueError:
            pass

    @classmethod
    def is_json(cls, value):
        return cls._RE_JSON.match(value)

    @staticmethod
    def decode_json(value):
        try:
            return demjson.decode(value)
        except demjson.JSONDecodeError:
            pass

    @classmethod
    def guess_value(cls, value, let_type):
        if 'int' == let_type or 'long' == let_type:
            i = cls.to_int(value)
            if i is not None:
                return i
            if isinstance(value, str) and (not value or value.isspace()):
                return 0  # 填空的转为0
            raise _CellError(value, 'can not cast to int')
        elif 'string' == let_type:
            if isinstance(value, str):
                return value
            return str([str(value), int(value)][int(value) == value])  # '{:g}'.format(value)
        elif 'float' == let_type:
            f = cls.to_float(value)
            if f is not None:
                return f
            if isinstance(value, str) and (not value or value.isspace()):
                return 0.0  # 填空的转为0
            raise _CellError(value, 'can not cast to float')
        elif 'json' == let_type:
            if isinstance(value, str):
                s = value.strip()
                if not s:
                    return s  # 兼容空格子
                if _Fmt.is_json(s):
                    return s
            else:
                if 0 == cls.to_int(value):
                    return ''  # 兼容填0
            raise _CellError(value, 'can not cast to json')

    @classmethod
    def trans_str_symb(cls, s):
        return cls._RE_ESCAPED.sub(lambda m: eval(repr(m.group(0)).replace('\\\\', '\\')), s)

class _SheetError(Exception):
    def __init__(self, book_file, sheet_name, sheet_errors):
        super().__init__(self)
        self._book_file = book_file
        self._sheet_name = sheet_name
        self._sheet_errors = sheet_errors

    def __str__(self):
        msg = '\n%s\t-\t%s\n' % (self._book_file, self._sheet_name)
        msg += '\n'.join('%s' % err for err in self._sheet_errors)
        return msg

class _CellError(Exception):
    def __init__(self, value, msg):
        self._msg = msg
        self._val = value

    def __str__(self):
        return '"%s"：%s' % (self._msg, self._val)

class _SheetArea:
    def __init__(self, top, left, lines):
        self.top = top  # row begin index
        self.left = left  # col begin index
        self.lines = lines  # row nums
        self.begin = top + 4  # data begin row
        self.header = None  # _SheetHead

class _SheetHead:
    def __init__(self):
        self.cols = []  # 导出的列
        self.keys = []  # 字段
        self.lets = []  # 数据类型

class SheetBuilder:
    def __init__(self, warndumpable=True, errordumpable=True, alertable=False):
        self._alertable = alertable
        self._warndumpable = warndumpable
        self._errordumpable = errordumpable
        self._excel_warns = {}
        self._excel_errors = {}

    def set_editor(self, out_format='binary'):
        if 'binary' == out_format:
            self._editor = _ULOEditor()
        elif 'lua' == out_format:
            self._editor = _LUAEditor()
        # elif 'txt' == out_format:
        #     self._editor = _TXTEditor()
        assert self._editor, 'unspport export format:' + out_format

    def exit_on_error(self, err_msg='error occurred, please see the console.'):
        if self._alertable:
            from tkinter import messagebox
            messagebox.showinfo('error tips', err_msg)
        else:
            log.e(err_msg)
        sys.exit(1)  # 遇到错误中断

    def build(self, excel_dir, out_path, denylist: list=None, allowlist: list=None):
        if not excel_dir:
            self.exit_on_error('excel dir can not be empty')
            return
        if not out_path:
            self.exit_on_error('output path can not be empty')
            return
        self._lookup_dict = {}
        start_t = time.time()
        metalist = FileMetaList(os.path.join(excel_dir, '.version.o'), hide=True)
        is_force = metalist.isupgrade(VERSION)
        is_force = self._editor.edit_begin(out_path, is_force=is_force)
        for _, _, files in os.walk(excel_dir):
            for filename in files:
                if filename.startswith('~') or not filename.endswith('.xlsx'):
                    continue
                excel_name = os.path.splitext(filename)[0]
                if allowlist:
                    if excel_name not in allowlist:
                        metalist.keep(excel_name)
                        self._lookup_dict[excel_name] = _Fmt.NO_DIFF_FLAG  # 整张表没有变更
                        continue
                elif denylist:
                    if excel_name in denylist:
                        metalist.keep(excel_name)
                        self._lookup_dict[excel_name] = _Fmt.NO_DIFF_FLAG  # 整张表没有变更
                        continue
                excel_path = os.path.join(excel_dir, filename)
                if metalist.diff(excel_name, excel_path, is_force):
                    self._lookup_dict[excel_name] = []  # 这张表需要导出，记录具体导出了哪些sheet。
                    self._make_book(excel_name, excel_path, self._errordumpable)
                else:
                    self._lookup_dict[excel_name] = _Fmt.NO_DIFF_FLAG  # 整张表没有变更
        sheet_nums = self._editor.edit_end(self._lookup_dict, is_force)
        metalist.save(VERSION)
        self._dump_build_logs()
        log.i('export excel done, duration:%.2fs, sheet count:%d' % (time.time() - start_t, sheet_nums))
        if self._excel_errors:
            self.exit_on_error()

    def _dump_build_logs(self):
        # 打印警告
        if self._warndumpable and self._excel_warns:
            num = 0
            for excel_name, warn_dict in self._excel_warns.items():
                for sheet_name, warn_list in warn_dict.items():
                    num += 1
                    log.w(num, excel_name, sheet_name, warn_list)
        # 打印错误
        if self._errordumpable and self._excel_errors:
            for excel_name, error_dict in self._excel_errors.items():
                log.e('======================================== excel:', excel_name)
                for sheet_name, err_list in error_dict.items():
                    log.e('-------------------------------- sheet:', sheet_name)
                    log.e('\n'.join('error [%s]' % err for err in err_list))

    def _make_book(self, excel_name, excel_path, list_error):
        excel_book = xlrd.open_workbook(excel_path, encoding_override='utf-8')
        for sheet_name in excel_book.sheet_names():
            sheet_obj = excel_book.sheet_by_name(sheet_name)
            sheet_errs = []
            sheet_area = self._look_sheet(sheet_obj, sheet_errs)
            if sheet_errs:
                Collect.gen_dict(self._excel_warns, excel_name)[sheet_name] = sheet_errs  # 记录填表格式的错误信息
                continue
            log.i(excel_name, sheet_name)
            self._make_sheet(excel_name, sheet_name, sheet_obj, sheet_area, sheet_errs)
            if sheet_errs:
                if list_error:
                    Collect.gen_dict(self._excel_errors, excel_name)[sheet_name] = sheet_errs  # 记录导表的错误信息
                else:
                    log.e(_SheetError(excel_name, sheet_name, sheet_errs))
                    self.exit_on_error()

    def _make_sheet(self, excel_name, sheet_name, sheet_obj, sheet_area, sheet_errs):
        self._make_header(sheet_obj, sheet_area, sheet_area.top + 1, sheet_errs)
        if sheet_errs:
            return sheet_errs
        if not sheet_area.header.cols:
            return  # 数据列为空
        self._editor.edit(excel_name, sheet_name, sheet_obj, sheet_area, sheet_errs)
        if sheet_errs:
            return sheet_errs
        self._lookup_dict[excel_name].append(sheet_name)  # 记录导出的表

    def _make_header(self, sheet, sheet_area, key_row, sheet_errs):
        header = _SheetHead()
        let_row = sheet_area.top + 2
        for c in range(sheet_area.left + 1, sheet.ncols):
            t = _Fmt.to_cast(sheet.cell_value(let_row, c), sheet_errs)
            if not t:
                continue
            k = _Fmt.to_word(sheet.cell_value(key_row, c), sheet_errs)
            if not k:
                continue
            if k in header.keys:
                sheet_errs.append('duplicate field:' + k)
                continue
            if 'string' == t and self._is_json_col(sheet, c, sheet_area):
                t = 'json'  # 自动检查json格式
            header.keys.append(k)
            header.lets.append(t)
            header.cols.append(c)
        sheet_area.header = header

    def _look_sheet(self, sheet, sheet_errs):
        if sheet.nrows < 1 or sheet.ncols < 1:
            sheet_errs.append('empty sheet')
            return
        top, left = self._find_sheet_origin(sheet)
        if -1 == top or -1 == left:
            sheet_errs.append('can not found %s' % _Fmt._TAG_CLIENT)
            return
        if not _Fmt.is_server_tag(sheet.cell_value(top + 3, left)):
            sheet_errs.append('can not found %s' % _Fmt._TAG_SERVER)
            return
        row_num = sheet.nrows - top
        if (row_num < 5) or (sheet.ncols - left < 2):
            sheet_errs.append('the sheet is not complete')
            return
        lines = self._find_sheet_end(sheet, top + 4, left)
        if (5 == lines - top) and (row_num > 5):
            sheet_errs.append('the sheet is deprecated')
            return
        return _SheetArea(top, left, lines)

    @staticmethod
    def _is_json_col(sheet, col, sheet_area):
        for r in range(sheet_area.begin, sheet_area.lines):
            v = sheet.cell_value(r, col)
            if isinstance(v, str):
                v = v.strip()
                if not v:
                    continue  # 过滤掉空格子
                return _Fmt.is_json(v) and (_Fmt.decode_json(v) is not None)
            else:
                if 0 == _Fmt.to_int(v):
                    continue  # 过滤掉填0的情况
                return False

    @staticmethod
    def _find_sheet_origin(sheet):
        if _Fmt.is_client_tag(sheet.cell_value(1, 0)):
            return 0, 0
        for r in range(sheet.nrows):
            for c in range(sheet.ncols):
                if _Fmt.is_client_tag(sheet.cell_value(r, c)):
                    return max(r - 1, 0), c
        return -1, -1

    @staticmethod
    def _find_sheet_end(sheet, row_0, col_0):
        for r in range(row_0, sheet.nrows):
            if _Fmt.is_end_tag(sheet.cell_value(r, col_0)):
                return r + 1
        return sheet.nrows

class _Lua2:

    class _IndexInfo:
        def __init__(self, row_ns, values, amount, key, let):
            self.row_ns = row_ns
            self.values = values
            self.amount = amount
            self.key = key
            self.let = let

    @classmethod
    def gen_index_info(cls, sheet_obj, sheet_area, errors):
        row_ns = []
        values = []
        col = sheet_area.header.cols[0]
        key = sheet_area.header.keys[0]
        let = sheet_area.header.lets[0]
        for r in range(sheet_area.begin, sheet_area.lines):
            v = sheet_obj.cell_value(r, col)
            if isinstance(v, str):
                v = v.strip()
                if not v:
                    continue
            try:
                values.append(_Fmt.guess_value(v, let))
                row_ns.append(r)
            except _CellError as err:
                errors.append(err)
        amount = len(row_ns)
        if amount > 0:
            return cls._IndexInfo(row_ns, values, amount, key, let)

    @staticmethod
    def is_list_table(index_info):
        for i in range(index_info.amount):
            if index_info.values[i] != i + 1:
                return False
        return True

    @classmethod
    def look_mt_value(cls, row_items, ncols):
        mt = {}
        for i in range(ncols):
            vt = {}
            for items in row_items:
                v = items[i]
                vt[v] = 1 if (v not in vt) else (vt[v] + 1)
            _t, _v = 0, 0
            for v in vt:
                if vt[v] > _t:
                    _t, _v = vt[v], v
            if _t > 1:
                mt[i] = _v
        return mt

class _ULOEditor:

    def __init__(self, forceone=False):
        self._force_one = forceone
        self._json_type = {'nil': 0, 'string': 1, 'int': 2, 'float': 3, 'bool': 4, 'list': 5, 'dict': 6, 'long': 7}
        self._ulo_type = {'int': 1, 'string': 2, 'float': 3, 'json': 4, 'long': 5}

    def edit_begin(self, out_path, is_force):
        self._ulo_path = out_path
        self._new_dict = {}
        if self._force_one:
            if not os.path.isfile(out_path):
                log.d('history exported data lost, need to be re-exported:', out_path)
                return True
        else:
            if not os.path.isdir(out_path):
                log.d('history exported data lost, need to be re-exported:', out_path)
                return True
        return is_force

    def edit_end(self, build_look_map, is_force):
        if self._force_one:
            return self._out_one(build_look_map, is_force)
        else:
            return self._out_pkg(build_look_map)

    def _out_one(self, build_look_map, is_force):
        edit_dict = {}
        # load old sheets
        if not is_force and os.path.isfile(self._ulo_path):
            ba = Bit.ByteArray()
            with open(self._ulo_path, 'rb') as fp:
                ba.init_buffer(fp.read())
            nn = ba.read_u16()
            for i in range(nn):
                excel_name, sheet_name = Text.unpack(ba.read_utf8(), '.')
                sheet_buf = ba.read_bytes(ba.read_u32())
                book_look_map = build_look_map.get(excel_name)
                if not book_look_map:
                    continue  # 这边被剔除了
                new_sheet_dic = Collect.gen_dict(edit_dict, excel_name)
                if book_look_map == _Fmt.NO_DIFF_FLAG:
                    new_sheet_dic[sheet_name] = sheet_buf  # 这个excel没有变更，全部保留。
                    continue
                if sheet_name in book_look_map:
                    new_sheet_dic[sheet_name] = sheet_buf  # 只保留记录过的表
        # merge sheets
        for excel_name, build_dict in self._new_dict.items():
            Collect.gen_dict(edit_dict, excel_name).update(build_dict)
        # output sheets
        sheet_nums = 0
        if edit_dict:
            ba = Bit.ByteArray().init_capacity(1024 * 1024 * 8)
            ba.set_position(2)
            for excel_name, sheet_dict in edit_dict.items():
                sheet_nums += self._build_buf(excel_name, sheet_dict, ba)
                # log.i('write:', sheet_nums, excel_name, sheet_name)
            ba.set_position(0).write_u16(sheet_nums)  # 写入表的数量
            with open(self._ulo_path, 'wb') as fp:
                fp.write(ba.slim_buffer())
        return sheet_nums

    def _out_pkg(self, build_look_map):
        if not os.path.isdir(self._ulo_path):
            os.makedirs(self._ulo_path)
        for excel_name, sheet_dict in self._new_dict.items():
            ba = Bit.ByteArray().init_capacity(1024 * 1024 * 8)
            ba.set_position(2)
            sheet_nums = self._build_buf(excel_name, sheet_dict, ba)
            ba.set_position(0).write_u16(sheet_nums)  # 写入表的数量
            with open(os.path.join(self._ulo_path, excel_name + '.ulo'), 'wb') as fp:
                fp.write(ba.slim_buffer())
        total_nums = 0
        for name in os.listdir(self._ulo_path):
            ulofile = os.path.join(self._ulo_path, name)
            if FS.filename(name) not in build_look_map:
                log.w('delete ulo:', ulofile)
                os.remove(ulofile)
            else:
                with open(ulofile, 'rb') as fp:
                    total_nums += Bit.u16_from(fp.read(2))
        return total_nums

    def _build_buf(self, excel_name, sheet_dict, buffer):
        sheet_nums = 0
        for sheet_name, sheet_buf in sheet_dict.items():
            self._write_string(buffer, excel_name + '.' + sheet_name)
            buffer_len = len(sheet_buf)
            buffer.write_u32(buffer_len)
            buffer.write_bytes(sheet_buf, buffer_len)
            sheet_nums += 1
        return sheet_nums

    def edit(self, excel_name, sheet_name, sheet_obj, sheet_area, errors):
        # 创建索引信息[_IndexInfo]
        index_info = _Lua2.gen_index_info(sheet_obj, sheet_area, errors)
        if not index_info:
            return
        # 检查是否有可导出的数据列
        data_cols = sheet_area.header.cols[1:]
        if not data_cols:
            return
        buffer = self._gen_buffer(sheet_obj, index_info, sheet_area, data_cols, errors)
        if errors:
            pass  # 格子数据格式错误
        else:
            Collect.gen_dict(self._new_dict, excel_name)[sheet_name] = buffer

    def _gen_buffer(self, sheet_obj, index_info, sheet_area, data_cols, errors):
        data_ncol = len(data_cols)
        data_keys = sheet_area.header.keys[1:]
        data_lets = sheet_area.header.lets[1:]
        is_list_t = _Lua2.is_list_table(index_info)
        # write to buffer
        ba = Bit.ByteArray().init_capacity(index_info.amount * data_ncol * 256)
        if is_list_t:
            ba.write_byte(1)
        else:
            ba.write_byte(0)
            ba.write_byte(self._ulo_type[index_info.let])  # write index let type
        ba.write_u8(data_ncol)
        for n in range(data_ncol):
            self._write_string(ba, data_keys[n])
            ba.write_byte(self._ulo_type[data_lets[n]])  # write key let type
        ba.write_u16(index_info.amount)
        for m in range(index_info.amount):
            r = index_info.row_ns[m]
            if not is_list_t:
                try:
                    self._write_cell(ba, index_info.values[m], index_info.let)
                except _CellError as err:
                    errors.append(err)
            for n in range(data_ncol):
                t = data_lets[n]
                try:
                    v = _Fmt.guess_value(sheet_obj.cell_value(r, data_cols[n]), t)
                    self._write_cell(ba, v, t)
                except _CellError as err:
                    errors.append(err)
        return ba.slim_buffer()

    def _write_cell(self, ba, value, let):
        if 'int' == let:
            ba.write_int(value)
        elif 'long' == let:
            ba.write_longlong(value)
        elif 'string' == let:
            self._write_string(ba, value)
        elif 'float' == let:
            ba.write_double(value)
        elif 'json' == let:
            if value:
                json_obj = _Fmt.decode_json(value)
                if json_obj is None:
                    raise _CellError(value, 'json error')
                else:
                    self._write_json(ba, json_obj)
            else:
                ba.write_byte(0)  # write nil json value

    def _write_json(self, ba, data):
        if isinstance(data, str):
            if data:
                ba.write_u8(self._json_type['string'])
                self._write_string(ba, data)
            else:
                ba.write_u8(0)  # write nil json value
        elif isinstance(data, int):
            if data > 2147483647 or data < -2147483648:
                ba.write_u8(self._json_type['long'])
                ba.write_longlong(data)
            else:
                ba.write_u8(self._json_type['int'])
                ba.write_int(data)
        elif isinstance(data, float):
            ba.write_u8(self._json_type['float'])
            ba.write_double(data)
        elif isinstance(data, bool):
            ba.write_u8(self._json_type['bool'])
            ba.write_byte(1 if data else 0)
        elif isinstance(data, list):
            a_len = len(data)
            if a_len > 255:
                raise _CellError(data, 'json list elements must no more than 256')
            ba.write_u8(self._json_type['list'])
            ba.write_u8(a_len)
            for i in range(a_len):
                self._write_json(ba, data[i])
        elif isinstance(data, dict):
            d_len = len(data)
            if d_len > 255:
                raise _CellError(data, 'json dict elements must no more than 256')
            ba.write_u8(self._json_type['dict'])
            ba.write_u8(d_len)
            for k, v in data.items():
                i = _Fmt.to_int(k)  # write dict key
                if i is None:
                    if k:
                        self._write_json(ba, k)
                    else:
                        raise _CellError(data, 'json key must not be none')
                else:
                    self._write_json(ba, i)
                self._write_json(ba, v)  # write dict value
        else:
            raise _CellError(data, 'unknow json value type:' + data)

    @staticmethod
    def _write_string(ba, s):
        # print(s)
        ba.write_utf8(_Fmt.trans_str_symb(s))

class _LUAEditor:
    def __init__(self):
        self._lua_keys = ('local', 'global', 'function', 'end', 'return', 'repeat', 'until', 'for', 'while', 'break')

    def edit_begin(self, out_path, is_force):
        self._out_root = out_path
        if not os.path.isdir(out_path):
            log.d('history exported data lost, need to be re-exported:', out_path)
            return True
        return is_force

    def edit_end(self, build_look_map, is_force):
        lualist = FS.walk_files(self._out_root, ewhites=['.lua'])
        for i in range(len(lualist) - 1, -1, -1):
            tag = lualist[i]
            removed = False
            excel_name = FS.parentname(tag)
            if excel_name in build_look_map:
                book_look_map = build_look_map[excel_name]
                if book_look_map != _Fmt.NO_DIFF_FLAG:  # 这个表没有修改
                    if FS.filename(tag) not in book_look_map:
                        removed = True
            else:
                removed = True
            if removed:
                luafile = os.path.join(self._out_root, tag)
                log.w('delete lua:', luafile)
                os.remove(luafile)
                lualist.pop(i)
        FS.rm_empty_dirs(self._out_root)
        return len(lualist)

    def edit(self, excel_name, sheet_name, sheet_obj, sheet_area, errors):
        index_info = _Lua2.gen_index_info(sheet_obj, sheet_area, errors)
        if not index_info:
            return
        lua_str = self._mk_items(sheet_obj, sheet_area, sheet_name, index_info, errors)
        if lua_str and not errors:
            parent = os.path.join(self._out_root, excel_name)
            FS.make_parent(parent)
            with open(os.path.join(parent, sheet_name + '.lua'), 'wb') as fp:
                fp.write(lua_str.encode('utf-8'))

    def _mk_items(self, sheet, sheet_area, sheet_name, index_info, errors):
        data_cols = sheet_area.header.cols[1:]
        data_ncol = len(data_cols)
        if data_ncol < 1:
            return
        data_lets = sheet_area.header.lets[1:]
        row_items = []
        for r in index_info.row_ns:
            items = []
            for i in range(data_ncol):
                try:
                    v = _Fmt.guess_value(sheet.cell_value(r, data_cols[i]), data_lets[i])
                    items.append(v)
                except _CellError as err:
                    errors.append(err)
            row_items.append(items)
        if errors:
            return
        data_keys = sheet_area.header.keys[1:]
        is_list_t = _Lua2.is_list_table(index_info)
        mt_v_dict = _Lua2.look_mt_value(row_items, data_ncol)
        # row items
        item_s = ''
        for m in range(index_info.amount):
            items = row_items[m]
            word_s = ''
            for n in range(data_ncol):
                v = items[n]
                if mt_v_dict.get(n) != v:
                    try:
                        word_s += self._mk_pair(v, data_keys[n], data_lets[n])
                    except _CellError as err:
                        errors.append(err)
            word_s = word_s[0:-2]
            row_id = index_info.values[m]
            if is_list_t:
                item_s += '--[[%s=%s]]{%s},\n' % (index_info.key, row_id, word_s)
            else:
                if 'string' == index_info.let:
                    row_id = '"%s"' % row_id
                item_s += '\t[%s]={%s},\n' % (row_id, word_s)
        # encoding
        data_s = 'local %s={\n%s\n}\n' % (sheet_name, item_s[0:-2])
        if len(mt_v_dict) > 0:
            data_s += self._mk_gen_meta(mt_v_dict, data_keys, data_lets, data_ncol, errors)
            data_s += self._mk_set_meta(mt_v_dict, sheet_name)
        data_s += 'return ' + sheet_name
        return data_s

    def _mk_gen_meta(self, meta_map, keys, lets, ncols, errors):
        meta_s = ''
        for i in range(ncols):
            if i in meta_map:
                try:
                    meta_s += self._mk_pair(meta_map[i], keys[i], lets[i])
                except _CellError as err:
                    errors.append(err)
        meta_s = 'local meta={%s}\n' % meta_s[0:-2]
        meta_s += 'meta.__index=function(t, k)\n'
        meta_s += '\treturn meta[k]\n'
        meta_s += 'end\n'
        return meta_s

    @staticmethod
    def _mk_set_meta(is_array_table, sheet_name):
        conf_s = ''
        if is_array_table:
            conf_s += 'for i=1, #%s do\n' % sheet_name
            conf_s += '\tsetmetatable(data[i], meta)\n'
            conf_s += 'end\n'
        else:
            conf_s += 'for _, t in pairs(%s) do\n' % sheet_name
            conf_s += '\tsetmetatable(t, meta)\n'
            conf_s += 'end\n'
        return conf_s

    def _mk_pair(self, value, key, cast_type):
        p_k = key if (key not in self._lua_keys) else ('["%s"]' % key)
        p_v = value
        if 'string' == cast_type:
            if value:
                p_v = '"%s"' % value
                # if self._re_chinese.search(value):
                #     with open('/Users/joli/Desktop/test/excel/lang.txt', 'ab') as file_p:
                #         file_p.write((value+'\n').encode('utf-8'))
            else:
                p_v = 'nil'
        elif 'json' == cast_type:
            if value:
                json_obj = _Fmt.decode_json(value)
                if json_obj is None:
                    raise _CellError(value, 'json error')
                else:
                    p_v = self._mk_json(json_obj)
            else:
                p_v = 'nil'
        return '%s=%s, ' % (p_k, p_v)

    def _mk_json(self, data):
        if isinstance(data, str):
            return '"%s"' % data
        elif isinstance(data, bool):
            return 'true' if data else 'false'
        elif isinstance(data, int) or isinstance(data, float):
            return str(data)
        elif isinstance(data, list):
            lua_str = ''
            for i in range(len(data)):
                lua_str += self._mk_json(data[i]) + ','
            return '{' + lua_str[0:-1] + '}'
        elif isinstance(data, dict):
            lua_str = ''
            for k, v in data.items():
                if _Fmt.to_int(k) is None:
                    lua_str += str(k)
                else:
                    lua_str += '[' + str(k) + ']'
                lua_str += '=' + self._mk_json(v) + ','
            return '{' + lua_str[0:-1] + '}'
        else:
            raise _CellError(data, 'unknow json value type:' + data)

class _TXTEditor:
    def __init__(self, txt_dir):
        self._txt_dir = txt_dir

    def edit_begin(self, is_force):
        if os.path.isdir(self._txt_dir):
            if is_force:
                shutil.rmtree(self._txt_dir)
            return is_force
        return True  # 历史输出丢失了，需要全部输出一遍。

    def edit_end(self, export_books, is_force):
        pass

    def edit(self, sheet, sheet_area, sheet_name, excel_name, errors):
        pass

# 文件元数据记录
class FileMetaList:
    def __init__(self, path, hide=False):
        self._path = path
        self._hide = hide
        self._new_map = {'version': 0, 'manifest': {}}
        self._old_map = {}
        self.load()

    def load(self):
        if not os.path.isfile(self._path):
            return
        if self._hide:
            FS.set_file_visible(self._path, True)
        self._old_map = json.loads(FS.read_text(self._path))
        if self._hide:
            FS.set_file_visible(self._path, False)

    def save(self, version):
        self._new_map['version'] = version
        if self._hide:
            FS.set_file_visible(self._path, True)
        FS.write_text(self._path, json.dumps(self._new_map, indent=4))
        if self._hide:
            FS.set_file_visible(self._path, False)

    def keep(self, key):
        old_manifest = self._old_map.get('manifest')
        old_mt = old_manifest.get(key) if old_manifest else None
        if old_mt:
            self._new_map['manifest'][key] = old_mt

    def diff(self, key, filepath, force):  # 对比元数据是否不同
        st = os.stat(filepath)
        new_mt = math.floor(st.st_mtime * 1000)  # FS.md5(filepath)
        self._new_map['manifest'][key] = new_mt
        if force:
            return True
        else:
            old_manifest = self._old_map.get('manifest')
            old_mt = old_manifest.get(key) if old_manifest else None
            return old_mt != new_mt if old_mt else True

    def isupgrade(self, version):  # 是否程序已升级
        return self._old_map.get('version') != version
