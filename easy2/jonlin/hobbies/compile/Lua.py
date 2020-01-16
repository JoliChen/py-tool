# -*- coding: utf-8 -*-
# @Time    : 2019/4/11 11:14 AM
# @Author  : Joli
# @Email   : 99755349@qq.com
import re
import traceback
from enum import Enum
from jonlin.utils import Log

log = Log.Logger(__file__)

# 工具
class Kit:
    @staticmethod
    def array_to_hash(*a):
        return {k: True for k in a}

    @staticmethod
    def is_digit(ch):
        return 48 <= ord(ch) <= 57  # ch.charCodeAt(0)

    @classmethod
    def is_alphanumeric_char(cls, ch):
        return cls.is_digit(ch) or cls.is_letter(ch)

    @staticmethod
    def is_letter(ch):
        return Cst.UNICODE_LETTER.match(ch) is not None

    @staticmethod
    def is_unicode_digit(ch):
        return Cst.UNICODE_DIGIT.match(ch) is not None

    @staticmethod
    def is_unicode_combining_mark(ch):
        return Cst.UNICODE_COMBINING_MARK.match(ch) is not None

    @staticmethod
    def is_unicode_connector_punctuation(ch):
        return Cst.UNICODE_PUNCTUATION.match(ch) is not None

    # 是不是合法字符
    @classmethod
    def is_identifier_char(cls, ch):
        if cls.is_identifier_start(ch):
            return True
        if cls.is_unicode_combining_mark(ch):
            return True
        if cls.is_unicode_digit(ch):
            return True
        if cls.is_unicode_connector_punctuation(ch):
            return True
        if ch == '\u200c':  # zero-width non-joiner <ZWNJ>
            return True
        if ch == '\u200d':  # zero-width joiner <ZWJ> (in my ECMA-262 PDF, this is also 200c)
            return True
        return False

    @classmethod
    def is_identifier_start(cls, ch):
        return ch == "_" or cls.is_letter(ch)

    @staticmethod
    def is_token(token, ttype, value):
        return token.ttype == ttype and (value is None or token.value == value)

    @staticmethod
    def is_number(num):
        if Cst.RE_HEX_NUMBER.match(num):
            try:
                return int(num, 16)
            except ValueError:
                traceback.print_stack()
        if Cst.RE_OCT_NUMBER.match(num):
            try:
                return int(num, 8)
            except ValueError:
                traceback.print_stack()
        if Cst.RE_DEC_NUMBER.match(num):
            try:
                # return int(num, 10) if num.find('.') == -1 else float(num)
                return float(num)
            except ValueError:
                traceback.print_stack()

    # 操作符优先级排序
    @staticmethod
    def precedence_sort(*args):
        ret, n = {}, 1
        for i in range(len(args)):
            b = args[i]
            for j in range(len(b)):
                ret[b[j]] = n
            n += 1
        return ret

    @staticmethod
    def throw_parse_error(message, row, col, pos):
        raise LuaParseError(message, row, col, pos)

# 常量
class Cst:
    # 正则表达式
    RE_NEWLINE = re.compile('\r\n?|[\n\u2028\u2029]', re.M | re.S)  # 换行正则
    RE_UTF8SIG = re.compile('^\uFEFF')  # utf-8-sig 标识
    RE_HEX_NUMBER = re.compile('^0x[0-9a-f]+$', re.I)  # 16进制
    RE_OCT_NUMBER = re.compile('^0[0-7]+$')  # 8进制
    RE_DEC_NUMBER = re.compile('^\d*\.?\d*(?:e[+-]?\d*(?:\d\.?|\.?\d)\d*)?$', re.I)  # 10进制
    # Unicode 6.1
    UNICODE_LETTER = re.compile('[\\u0041-\\u005A\\u0061-\\u007A\\u00AA\\u00B5\\u00BA\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02C1\\u02C6-\\u02D1\\u02E0-\\u02E4\\u02EC\\u02EE\\u0370-\\u0374\\u0376\\u0377\\u037A-\\u037D\\u0386\\u0388-\\u038A\\u038C\\u038E-\\u03A1\\u03A3-\\u03F5\\u03F7-\\u0481\\u048A-\\u0527\\u0531-\\u0556\\u0559\\u0561-\\u0587\\u05D0-\\u05EA\\u05F0-\\u05F2\\u0620-\\u064A\\u066E\\u066F\\u0671-\\u06D3\\u06D5\\u06E5\\u06E6\\u06EE\\u06EF\\u06FA-\\u06FC\\u06FF\\u0710\\u0712-\\u072F\\u074D-\\u07A5\\u07B1\\u07CA-\\u07EA\\u07F4\\u07F5\\u07FA\\u0800-\\u0815\\u081A\\u0824\\u0828\\u0840-\\u0858\\u08A0\\u08A2-\\u08AC\\u0904-\\u0939\\u093D\\u0950\\u0958-\\u0961\\u0971-\\u0977\\u0979-\\u097F\\u0985-\\u098C\\u098F\\u0990\\u0993-\\u09A8\\u09AA-\\u09B0\\u09B2\\u09B6-\\u09B9\\u09BD\\u09CE\\u09DC\\u09DD\\u09DF-\\u09E1\\u09F0\\u09F1\\u0A05-\\u0A0A\\u0A0F\\u0A10\\u0A13-\\u0A28\\u0A2A-\\u0A30\\u0A32\\u0A33\\u0A35\\u0A36\\u0A38\\u0A39\\u0A59-\\u0A5C\\u0A5E\\u0A72-\\u0A74\\u0A85-\\u0A8D\\u0A8F-\\u0A91\\u0A93-\\u0AA8\\u0AAA-\\u0AB0\\u0AB2\\u0AB3\\u0AB5-\\u0AB9\\u0ABD\\u0AD0\\u0AE0\\u0AE1\\u0B05-\\u0B0C\\u0B0F\\u0B10\\u0B13-\\u0B28\\u0B2A-\\u0B30\\u0B32\\u0B33\\u0B35-\\u0B39\\u0B3D\\u0B5C\\u0B5D\\u0B5F-\\u0B61\\u0B71\\u0B83\\u0B85-\\u0B8A\\u0B8E-\\u0B90\\u0B92-\\u0B95\\u0B99\\u0B9A\\u0B9C\\u0B9E\\u0B9F\\u0BA3\\u0BA4\\u0BA8-\\u0BAA\\u0BAE-\\u0BB9\\u0BD0\\u0C05-\\u0C0C\\u0C0E-\\u0C10\\u0C12-\\u0C28\\u0C2A-\\u0C33\\u0C35-\\u0C39\\u0C3D\\u0C58\\u0C59\\u0C60\\u0C61\\u0C85-\\u0C8C\\u0C8E-\\u0C90\\u0C92-\\u0CA8\\u0CAA-\\u0CB3\\u0CB5-\\u0CB9\\u0CBD\\u0CDE\\u0CE0\\u0CE1\\u0CF1\\u0CF2\\u0D05-\\u0D0C\\u0D0E-\\u0D10\\u0D12-\\u0D3A\\u0D3D\\u0D4E\\u0D60\\u0D61\\u0D7A-\\u0D7F\\u0D85-\\u0D96\\u0D9A-\\u0DB1\\u0DB3-\\u0DBB\\u0DBD\\u0DC0-\\u0DC6\\u0E01-\\u0E30\\u0E32\\u0E33\\u0E40-\\u0E46\\u0E81\\u0E82\\u0E84\\u0E87\\u0E88\\u0E8A\\u0E8D\\u0E94-\\u0E97\\u0E99-\\u0E9F\\u0EA1-\\u0EA3\\u0EA5\\u0EA7\\u0EAA\\u0EAB\\u0EAD-\\u0EB0\\u0EB2\\u0EB3\\u0EBD\\u0EC0-\\u0EC4\\u0EC6\\u0EDC-\\u0EDF\\u0F00\\u0F40-\\u0F47\\u0F49-\\u0F6C\\u0F88-\\u0F8C\\u1000-\\u102A\\u103F\\u1050-\\u1055\\u105A-\\u105D\\u1061\\u1065\\u1066\\u106E-\\u1070\\u1075-\\u1081\\u108E\\u10A0-\\u10C5\\u10C7\\u10CD\\u10D0-\\u10FA\\u10FC-\\u1248\\u124A-\\u124D\\u1250-\\u1256\\u1258\\u125A-\\u125D\\u1260-\\u1288\\u128A-\\u128D\\u1290-\\u12B0\\u12B2-\\u12B5\\u12B8-\\u12BE\\u12C0\\u12C2-\\u12C5\\u12C8-\\u12D6\\u12D8-\\u1310\\u1312-\\u1315\\u1318-\\u135A\\u1380-\\u138F\\u13A0-\\u13F4\\u1401-\\u166C\\u166F-\\u167F\\u1681-\\u169A\\u16A0-\\u16EA\\u16EE-\\u16F0\\u1700-\\u170C\\u170E-\\u1711\\u1720-\\u1731\\u1740-\\u1751\\u1760-\\u176C\\u176E-\\u1770\\u1780-\\u17B3\\u17D7\\u17DC\\u1820-\\u1877\\u1880-\\u18A8\\u18AA\\u18B0-\\u18F5\\u1900-\\u191C\\u1950-\\u196D\\u1970-\\u1974\\u1980-\\u19AB\\u19C1-\\u19C7\\u1A00-\\u1A16\\u1A20-\\u1A54\\u1AA7\\u1B05-\\u1B33\\u1B45-\\u1B4B\\u1B83-\\u1BA0\\u1BAE\\u1BAF\\u1BBA-\\u1BE5\\u1C00-\\u1C23\\u1C4D-\\u1C4F\\u1C5A-\\u1C7D\\u1CE9-\\u1CEC\\u1CEE-\\u1CF1\\u1CF5\\u1CF6\\u1D00-\\u1DBF\\u1E00-\\u1F15\\u1F18-\\u1F1D\\u1F20-\\u1F45\\u1F48-\\u1F4D\\u1F50-\\u1F57\\u1F59\\u1F5B\\u1F5D\\u1F5F-\\u1F7D\\u1F80-\\u1FB4\\u1FB6-\\u1FBC\\u1FBE\\u1FC2-\\u1FC4\\u1FC6-\\u1FCC\\u1FD0-\\u1FD3\\u1FD6-\\u1FDB\\u1FE0-\\u1FEC\\u1FF2-\\u1FF4\\u1FF6-\\u1FFC\\u2071\\u207F\\u2090-\\u209C\\u2102\\u2107\\u210A-\\u2113\\u2115\\u2119-\\u211D\\u2124\\u2126\\u2128\\u212A-\\u212D\\u212F-\\u2139\\u213C-\\u213F\\u2145-\\u2149\\u214E\\u2160-\\u2188\\u2C00-\\u2C2E\\u2C30-\\u2C5E\\u2C60-\\u2CE4\\u2CEB-\\u2CEE\\u2CF2\\u2CF3\\u2D00-\\u2D25\\u2D27\\u2D2D\\u2D30-\\u2D67\\u2D6F\\u2D80-\\u2D96\\u2DA0-\\u2DA6\\u2DA8-\\u2DAE\\u2DB0-\\u2DB6\\u2DB8-\\u2DBE\\u2DC0-\\u2DC6\\u2DC8-\\u2DCE\\u2DD0-\\u2DD6\\u2DD8-\\u2DDE\\u2E2F\\u3005-\\u3007\\u3021-\\u3029\\u3031-\\u3035\\u3038-\\u303C\\u3041-\\u3096\\u309D-\\u309F\\u30A1-\\u30FA\\u30FC-\\u30FF\\u3105-\\u312D\\u3131-\\u318E\\u31A0-\\u31BA\\u31F0-\\u31FF\\u3400-\\u4DB5\\u4E00-\\u9FCC\\uA000-\\uA48C\\uA4D0-\\uA4FD\\uA500-\\uA60C\\uA610-\\uA61F\\uA62A\\uA62B\\uA640-\\uA66E\\uA67F-\\uA697\\uA6A0-\\uA6EF\\uA717-\\uA71F\\uA722-\\uA788\\uA78B-\\uA78E\\uA790-\\uA793\\uA7A0-\\uA7AA\\uA7F8-\\uA801\\uA803-\\uA805\\uA807-\\uA80A\\uA80C-\\uA822\\uA840-\\uA873\\uA882-\\uA8B3\\uA8F2-\\uA8F7\\uA8FB\\uA90A-\\uA925\\uA930-\\uA946\\uA960-\\uA97C\\uA984-\\uA9B2\\uA9CF\\uAA00-\\uAA28\\uAA40-\\uAA42\\uAA44-\\uAA4B\\uAA60-\\uAA76\\uAA7A\\uAA80-\\uAAAF\\uAAB1\\uAAB5\\uAAB6\\uAAB9-\\uAABD\\uAAC0\\uAAC2\\uAADB-\\uAADD\\uAAE0-\\uAAEA\\uAAF2-\\uAAF4\\uAB01-\\uAB06\\uAB09-\\uAB0E\\uAB11-\\uAB16\\uAB20-\\uAB26\\uAB28-\\uAB2E\\uABC0-\\uABE2\\uAC00-\\uD7A3\\uD7B0-\\uD7C6\\uD7CB-\\uD7FB\\uF900-\\uFA6D\\uFA70-\\uFAD9\\uFB00-\\uFB06\\uFB13-\\uFB17\\uFB1D\\uFB1F-\\uFB28\\uFB2A-\\uFB36\\uFB38-\\uFB3C\\uFB3E\\uFB40\\uFB41\\uFB43\\uFB44\\uFB46-\\uFBB1\\uFBD3-\\uFD3D\\uFD50-\\uFD8F\\uFD92-\\uFDC7\\uFDF0-\\uFDFB\\uFE70-\\uFE74\\uFE76-\\uFEFC\\uFF21-\\uFF3A\\uFF41-\\uFF5A\\uFF66-\\uFFBE\\uFFC2-\\uFFC7\\uFFCA-\\uFFCF\\uFFD2-\\uFFD7\\uFFDA-\\uFFDC]')
    UNICODE_COMBINING_MARK = re.compile('[\\u0300-\\u036F\\u0483-\\u0487\\u0591-\\u05BD\\u05BF\\u05C1\\u05C2\\u05C4\\u05C5\\u05C7\\u0610-\\u061A\\u064B-\\u065F\\u0670\\u06D6-\\u06DC\\u06DF-\\u06E4\\u06E7\\u06E8\\u06EA-\\u06ED\\u0711\\u0730-\\u074A\\u07A6-\\u07B0\\u07EB-\\u07F3\\u0816-\\u0819\\u081B-\\u0823\\u0825-\\u0827\\u0829-\\u082D\\u0859-\\u085B\\u08E4-\\u08FE\\u0900-\\u0903\\u093A-\\u093C\\u093E-\\u094F\\u0951-\\u0957\\u0962\\u0963\\u0981-\\u0983\\u09BC\\u09BE-\\u09C4\\u09C7\\u09C8\\u09CB-\\u09CD\\u09D7\\u09E2\\u09E3\\u0A01-\\u0A03\\u0A3C\\u0A3E-\\u0A42\\u0A47\\u0A48\\u0A4B-\\u0A4D\\u0A51\\u0A70\\u0A71\\u0A75\\u0A81-\\u0A83\\u0ABC\\u0ABE-\\u0AC5\\u0AC7-\\u0AC9\\u0ACB-\\u0ACD\\u0AE2\\u0AE3\\u0B01-\\u0B03\\u0B3C\\u0B3E-\\u0B44\\u0B47\\u0B48\\u0B4B-\\u0B4D\\u0B56\\u0B57\\u0B62\\u0B63\\u0B82\\u0BBE-\\u0BC2\\u0BC6-\\u0BC8\\u0BCA-\\u0BCD\\u0BD7\\u0C01-\\u0C03\\u0C3E-\\u0C44\\u0C46-\\u0C48\\u0C4A-\\u0C4D\\u0C55\\u0C56\\u0C62\\u0C63\\u0C82\\u0C83\\u0CBC\\u0CBE-\\u0CC4\\u0CC6-\\u0CC8\\u0CCA-\\u0CCD\\u0CD5\\u0CD6\\u0CE2\\u0CE3\\u0D02\\u0D03\\u0D3E-\\u0D44\\u0D46-\\u0D48\\u0D4A-\\u0D4D\\u0D57\\u0D62\\u0D63\\u0D82\\u0D83\\u0DCA\\u0DCF-\\u0DD4\\u0DD6\\u0DD8-\\u0DDF\\u0DF2\\u0DF3\\u0E31\\u0E34-\\u0E3A\\u0E47-\\u0E4E\\u0EB1\\u0EB4-\\u0EB9\\u0EBB\\u0EBC\\u0EC8-\\u0ECD\\u0F18\\u0F19\\u0F35\\u0F37\\u0F39\\u0F3E\\u0F3F\\u0F71-\\u0F84\\u0F86\\u0F87\\u0F8D-\\u0F97\\u0F99-\\u0FBC\\u0FC6\\u102B-\\u103E\\u1056-\\u1059\\u105E-\\u1060\\u1062-\\u1064\\u1067-\\u106D\\u1071-\\u1074\\u1082-\\u108D\\u108F\\u109A-\\u109D\\u135D-\\u135F\\u1712-\\u1714\\u1732-\\u1734\\u1752\\u1753\\u1772\\u1773\\u17B4-\\u17D3\\u17DD\\u180B-\\u180D\\u18A9\\u1920-\\u192B\\u1930-\\u193B\\u19B0-\\u19C0\\u19C8\\u19C9\\u1A17-\\u1A1B\\u1A55-\\u1A5E\\u1A60-\\u1A7C\\u1A7F\\u1B00-\\u1B04\\u1B34-\\u1B44\\u1B6B-\\u1B73\\u1B80-\\u1B82\\u1BA1-\\u1BAD\\u1BE6-\\u1BF3\\u1C24-\\u1C37\\u1CD0-\\u1CD2\\u1CD4-\\u1CE8\\u1CED\\u1CF2-\\u1CF4\\u1DC0-\\u1DE6\\u1DFC-\\u1DFF\\u20D0-\\u20DC\\u20E1\\u20E5-\\u20F0\\u2CEF-\\u2CF1\\u2D7F\\u2DE0-\\u2DFF\\u302A-\\u302F\\u3099\\u309A\\uA66F\\uA674-\\uA67D\\uA69F\\uA6F0\\uA6F1\\uA802\\uA806\\uA80B\\uA823-\\uA827\\uA880\\uA881\\uA8B4-\\uA8C4\\uA8E0-\\uA8F1\\uA926-\\uA92D\\uA947-\\uA953\\uA980-\\uA983\\uA9B3-\\uA9C0\\uAA29-\\uAA36\\uAA43\\uAA4C\\uAA4D\\uAA7B\\uAAB0\\uAAB2-\\uAAB4\\uAAB7\\uAAB8\\uAABE\\uAABF\\uAAC1\\uAAEB-\\uAAEF\\uAAF5\\uAAF6\\uABE3-\\uABEA\\uABEC\\uABED\\uFB1E\\uFE00-\\uFE0F\\uFE20-\\uFE26]')
    UNICODE_PUNCTUATION = re.compile('[\\u005F\\u203F\\u2040\\u2054\\uFE33\\uFE34\\uFE4D-\\uFE4F\\uFF3F]')
    UNICODE_DIGIT = re.compile('[\\u0030-\\u0039\\u0660-\\u0669\\u06F0-\\u06F9\\u07C0-\\u07C9\\u0966-\\u096F\\u09E6-\\u09EF\\u0A66-\\u0A6F\\u0AE6-\\u0AEF\\u0B66-\\u0B6F\\u0BE6-\\u0BEF\\u0C66-\\u0C6F\\u0CE6-\\u0CEF\\u0D66-\\u0D6F\\u0E50-\\u0E59\\u0ED0-\\u0ED9\\u0F20-\\u0F29\\u1040-\\u1049\\u1090-\\u1099\\u17E0-\\u17E9\\u1810-\\u1819\\u1946-\\u194F\\u19D0-\\u19D9\\u1A80-\\u1A89\\u1A90-\\u1A99\\u1B50-\\u1B59\\u1BB0-\\u1BB9\\u1C40-\\u1C49\\u1C50-\\u1C59\\uA620-\\uA629\\uA8D0-\\uA8D9\\uA900-\\uA909\\uA9D0-\\uA9D9\\uAA50-\\uAA59\\uABF0-\\uABF9\\uFF10-\\uFF19]')
    # 保留字
    RESERVED_WORDS = Kit.array_to_hash(
        'abstract',
        'boolean',
        'byte',
        'char',
        'class',
        'double',
        'enum',
        'export',
        'extends',
        'final',
        'float',
        'goto',
        'implements',
        'import',
        'int',
        'interface',
        'long',
        'native',
        'package',
        'private',
        'protected',
        'public',
        'short',
        'static',
        'super',
        'synchronized',
        'throws',
        'transient',
        'volatile'
    )
    # 关键字
    KEYWORDS = Kit.array_to_hash(
        'local',
        'do',
        'end',
        'function',
        'if',
        'elseif',
        'else',
        'for',
        'while',
        'repeat',
        'until',
        'then',
        'break',
        'return',
        'false',
        'true',
        'nil',
        'in',
        'or',
        'and',
        'not',
    )
    # ATOM关键字
    KEYWORDS_ATOM = Kit.array_to_hash('false', 'true', 'nil')
    # 操作符
    OPERATORS = Kit.array_to_hash(
        '+' ,
        '-' ,
        '*' ,
        '/' ,
        '%' ,
        '^' ,
        '<' ,
        '>' ,
        '=' ,
        '<=' ,
        '>=' ,
        '==' ,
        '~=' ,
        '+=' ,
        '-=' ,
        '/=' ,
        '*=' ,
        '%=' ,
        '^=' ,
        '..' ,
        '#'  ,
        'in' ,
        'or' ,
        'and' ,
        'not'
    )
    # 操作单字符
    OPERATOR_CHARS = Kit.array_to_hash(
        '=' ,
        '~' ,
        '+' ,
        '-' ,
        '*' ,
        '/' ,
        '%' ,
        '^' ,
        '<' ,
        '>' ,
        '.' ,
        '#'
    )
    # 空白符
    WHITESPACE_CHARS = Kit.array_to_hash(
        ' '  ,
        '\n' ,
        '\r' ,
        '\t' ,
        '\f' ,
        '\u00a0' ,
        '\u000b' ,
        '\u200b' ,
        '\u180e' ,
        '\u2000' ,
        '\u2001' ,
        '\u2002' ,
        '\u2003' ,
        '\u2004' ,
        '\u2005' ,
        '\u2006' ,
        '\u2007' ,
        '\u2008' ,
        '\u2009' ,
        '\u200a' ,
        '\u202f' ,
        '\u205f' ,
        '\u3000'
    )
    # 表达式前的关键字
    # KEYWORDS_BEFORE_EXPRESSION = Kit.array_to_hash('return', 'else')
    # 标点符号开始
    # PUNC_BEFORE_EXPRESSION = Kit.array_to_hash('[', '{' , '(', ',', '.', ';', ':')
    # 标点符号字符
    PUNC_CHARS = Kit.array_to_hash(
        '[' ,
        ']' ,
        '{' ,
        '}' ,
        '(' ,
        ')' ,
        ',' ,
        ';' ,
        ':'
    )
    # 操作符优先级
    PRECEDENCE = Kit.precedence_sort(
        ['not', 'or', 'and'],
        ['==', '~='],
        ['<', '>', '<=', '>=', 'in'],
        ['#', '..'],
        ['+', '-'],
        ['*', '/', '%', '^']
    )
    # 赋值符号
    ASSIGNMENT = Kit.array_to_hash(
        "=", "+=", "-=", "/=", "*=", "%=", "^="
    )
    # 一元操作符
    UNARY_PREFIX = Kit.array_to_hash('-', '#', 'not')

class Token(Enum):
    OPERATOR = 'operator'  # 操作符
    KEYWORD = 'keyword'  # 关键字
    NUMBER = 'number'  # 数字
    STRING = 'string'  # 字符串
    RAWSTR = 'rawstr'  # 原始字符串
    PUNC = 'punc'  # 标点符号
    NAME = 'name'  # 名称
    ATOM = 'atom'  # 原子
    COMMENT_LINE  = 'comment1'  # 单行注释
    COMMENT_BLOCK = 'comment2'  # 区块注释
    EOF = 'eof'

    def __repr__(self):
        return '%s' % self.value

class Statement(Enum):
    TOP = 'top'
    STAT = 'stat'
    IF = 'if'
    FOR = 'for'
    FOR_IN = 'for_in'
    WHILE = 'while'
    DO_WHILE = 'do_while'  # repeat-until
    BREAK = 'break'
    BLOCK = 'block'  # do-end
    FUNCTION = 'function'  # function target.name() end
    RETURN = 'return'
    ASSIGN = 'assign'  # 赋值语句
    LOCAL = 'local'
    TABLE = 'table'  # table
    NAME = 'name'  # 声明或引用名（函数名、for循环变量 等）
    ATOM = 'atom'  # 原子
    ATOM_NUMBER = 'atom_number'  # 数字常量
    ATOM_STRING = 'atom_string'  # 字符串常量
    ATOM_RAWSTR = 'atom_rawstr'  # 原始字符串常量
    ATOM_VA_ARG = 'atom_va_arg'  # 任意参数 ...
    CALL = 'call'  # 调用函数
    CALL_TABLE  = 'call_table'   # 调用函数 传入唯一的table参数并省略圆括号
    CALL_STRING = 'call_string'  # 调用函数 传入唯一的string参数并省略圆括号
    CALL_RAWSTR = 'call_rawstr'  # 调用函数 传入唯一的string参数并省略圆括号
    DOT = 'dot'  # 点
    COLON = 'colon'  # 冒号
    TUPLE = 'tuple'  # 元组 ()
    UNARY = 'unary'  # 一元操作符
    BINARY = 'binary'  # 二元操作符
    SUB_KEY = 'sub_key'  # table中的键运算式 {[${expr}]=?}
    SUB = 'sub'  # table[${expr}]=?
    SEQ = 'seq'
    HOOK = 'hook'  # 自定义插入代码

    def __repr__(self):
        return '%s' % self.value

class TokenData:
    def __init__(self, tokis, value, row, col, pos, endpos, nlb):
        self.tokis = tokis
        self.value = value
        self.row = row
        self.col = col
        self.pos = pos
        self.endpos = endpos
        self.nlb = nlb
        self.comments_before = None

    def __repr__(self):
        return '%s %s' % (self.tokis, self.value)

# 错误基类
class LuaError(Exception):
    def __init__(self):
        pass

# 文件尾错误
class LuaEOFError(LuaError):
    def __init__(self):
        LuaError.__init__(self)

    def __repr__(self):
        return 'EOF' + traceback.format_stack()

    def __str__(self):
        return 'EOF' + traceback.format_stack()

# 解析错误
class LuaParseError(LuaError):
    def __init__(self, message, row, col, pos):
        LuaError.__init__(self)
        self.message = message
        self.row = row
        self.col = col
        self.pos = pos

    def __str__(self):
        return self.message + ' (line: %d, col: %d, pos: %d)' % (self.row, self.col, self.pos)

# 渲染错误
class LuaRenderError(LuaError):
    def __init__(self, message):
        LuaError.__init__(self)
        self.message = message

    def __str__(self):
        return self.message

# 词法分析器
class Tokenizer:
    def __init__(self):
        pass

    def start(self, text):
        self.text = Cst.RE_UTF8SIG.sub('', Cst.RE_NEWLINE.sub('\n', text))
        self.length = len(self.text)
        self.row = 0
        self.col = 0
        self.pos = 0
        self.tokrow = 0
        self.tokcol = 0
        self.tokpos = 0
        self.newline_before = False  # 当前扫描的token中包含了换行
        self.comments_before = None  # 当前token前边的注释
        return self

    # 获取当前扫描位置的字符
    def peek(self):
        return self.text[self.pos] if self.pos < self.length else ''

    # 得到下一个字符
    # signal_eof 是否检测EOF
    # in_string  当前扫描的字符是否在 ['str', [[str]], 'str'] 里边
    def next(self, signal_eof=False, in_string=False):
        if signal_eof and self.is_eof():
            raise LuaEOFError()
        ch = self.text[self.pos]
        self.pos += 1
        if ch == '\n':
            # 当前扫描的token中包含了换行
            self.newline_before = self.newline_before or (not in_string)
            # 重新计算行列
            self.row += 1
            self.col = 0
        else:
            self.col += 1
        return ch

    # 是否到文件末尾
    def is_eof(self):
        return not (self.pos < self.length)

    # 开始扫描前记录
    def start_token(self):
        self.tokrow = self.row
        self.tokcol = self.col
        self.tokpos = self.pos

    # 得到一个token对象
    def token(self, tokis, value='', is_comment=False):
        td = TokenData(
            tokis=tokis,
            value=value,
            row=self.tokrow,
            col=self.tokcol,
            pos=self.tokpos,
            endpos=self.pos,
            nlb=self.newline_before
        )
        # 将注释块赋给注释后面的有效token
        if not is_comment and self.comments_before:
            td.comments_before = self.comments_before
            self.comments_before = None  # token前注释块已经赋给token对象了，这里需要清理状态。
            # make note of any newlines in the comments that came before
            for ct in td.comments_before:
                td.nlb = td.nlb or ct.nlb  # 检查当前token前的注释块是否有换行
        self.newline_before = False
        return td

    # 忽略空白符，直到当前去到的字符不是空白。
    def skip_whitespace(self):
        while self.peek() in Cst.WHITESPACE_CHARS:
            self.next()

    # 辅助函数 用于抛出错误
    def throw_error(self, err_msg):
        Kit.throw_parse_error(err_msg, self.tokrow, self.tokcol, self.tokcol)

    # 辅助函数 从当前位置开始找what出现的位置
    def search(self, what, signal_eof=False):
        pos = self.text.find(what, self.pos)
        if signal_eof and pos == -1:
            raise LuaEOFError()
        return pos

    # 辅助函数 判断下一个字符
    def next_is(self, what, begin=None):
        num = len(what)
        begin = self.pos + 1 if begin is None else begin
        if self.length < (begin + num):
            return False
        for i in range(num):
            if self.text[begin + i] != what[i]:
                return False
        return True

    # 辅助函数，用来读出token对应的字符串。
    # 例如扫描到 1.0002的1的时候，应该把1.0002整个字符串都认为是一个num的token，直到pred回调为false之后。
    def read_while(self, syntax_condition):
        s, i, ch = '', 0, self.peek()
        while ch:
            if syntax_condition(ch, i):
                i += 1
                s += self.next()
                ch = self.peek()
            else:
                break
        return s

    # 辅助函数  eof_error EOF的错误抛出信息
    def with_eof_error(self, syntax_cont, error_msg):
        try:
            return syntax_cont()
        except Exception as exc:
            if isinstance(exc, LuaParseError):
                self.throw_error(error_msg)
            else:
                raise exc

    # 读取数字
    def read_number(self, prefix=''):
        has_dot = prefix == '.'
        has_x = has_e = after_e = False

        def number_condition(ch, i):  # 数字读取条件检测器
            nonlocal has_dot, has_x, has_e, after_e
            if ch == "x" or ch == "X":
                if has_x:
                    return False
                has_x = True
                return True
            if not has_x and (ch == "E" or ch == "e"):
                if has_e:
                    return False
                has_e = after_e = True
                return True
            if ch == "-":
                if after_e or (i == 0 and not prefix):
                    return True
                return False
            if ch == '+':
                return after_e
            after_e = False
            if ch == ".":
                if not has_dot and not has_x and not has_e:
                    has_dot = True
                    return True
                return False
            return Kit.is_alphanumeric_char(ch)

        num = self.read_while(number_condition)
        if prefix:
            num = prefix + num
        if Kit.is_number(num) is None:
            self.throw_error('Invalid syntax: ' + num)
        else:
            return self.token(Token.NUMBER, num)

    # 读取转义符号
    def read_escaped_char(self, in_string=False):
        ch = self.next(True, in_string)
        if ch == 'n':
            return '\\n'
        if ch == 'r':
            return '\\r'
        if ch == 't':
            return '\\t'
        if ch == 'b':
            return '\\b'
        if ch == '0':
            return '\\0'
        if ch == 'f':
            return '\\f'
        if ch == '\\':
            return '\\\\'
        if ch == 'x':
            return chr(self.hex_bytes(2))
        if ch == 'u':
            return chr(self.hex_bytes(4))
        if ch == '\n':
            return ''  # 如果语句的最后跟一个\n表示要跟下一行连在一起 所以返回 ""
        return ch

    def hex_bytes(self, n):
        num = 0
        for n in range(n):
            ch = self.next(True)
            try:
                digit = int(ch, 16)
                num = (num << 4) | digit
            except ValueError:
                self.throw_error('Invalid hex-character pattern in string')
        return num

    # 读取字符串
    def read_string(self):
        return self.with_eof_error(self._string_cont, 'Unterminated string constant')

    def _string_cont(self):
        ret, raw, quote = '', False, self.next()
        if quote == '[':
            raw = True  # 读取原始字符串模式
            quote = ''
            while self.next() != '[':
                quote += '='
            quote += ']'
        while True:
            ch = self.next(True)
            if ch == '\\':  # 遇到\要吃掉后边的字符，例如\n \t \r \123
                # read OctalEscapeSequence(XXX: deprecated if "strict mode")
                octal_len, first = 0, None

                def oct_condition(c, i):  # 是为了读取 \123 这样的八进制字符
                    nonlocal octal_len, first
                    if '0' <= c <= '7':
                        if not first:
                            first = c
                            octal_len += 1
                            return octal_len
                        elif first <= '3' and octal_len <= 2:
                            octal_len += 1
                            return octal_len
                        elif first >= '4' and octal_len <= 1:
                            octal_len += 1
                            return octal_len
                    return False

                ch = self.read_while(oct_condition)
                if octal_len > 0:
                    ch = chr(int(ch, 8))
                else:
                    ch = self.read_escaped_char(True)
            else:
                if raw:
                    if ch == ']' and self.next_is(quote, self.pos):
                        span = len(quote)
                        self.pos += span  # 跳过原始字符串的结尾
                        self.col += span
                        break
                else:
                    if ch == quote:  # 引号配对，字符串读取结束。
                        break
            ret += ch
        return self.token(Token.RAWSTR, ret) if raw else self.token(Token.STRING, ret)  # string_cont() end

    def _block_comment_cont(self):
        i = self.search("]]", True)
        s = self.text[self.pos:i]
        n = len(s.split('\n'))
        self.pos = i + 2
        self.row += n - 1
        self.newline_before = self.newline_before or n > 1
        return self.token(Token.COMMENT_BLOCK, s, True)

    def read_word(self):
        word, backslash, escaped, hex_char, ch = '', False, False, None, None
        while True:
            ch = self.peek()
            if not ch:
                break
            if not backslash:
                if ch == '\\':
                    backslash = escaped = True
                    self.next()
                elif Kit.is_identifier_char(ch):
                    word += self.next()
                else:
                    break
            else:
                # 如果前边是\那后边需要带u 必须UnicodeEscape形式
                if ch != 'u':
                    self.throw_error('Expecting UnicodeEscapeSequence -- uXXXX')
                ch = self.read_escaped_char()
                if not Kit.is_identifier_char(ch):
                    self.throw_error("Unicode char: %d is not valid in identifier" % ord(ch[0]))
                word += ch
                backslash = False
        if escaped and word in Cst.KEYWORDS:  # 如果串中带有\那必须不能是关键字
            hex_char = hex(ord(word[0])).upper()
            word = '\\u' + '0000'[len(hex_char):] + hex_char + word[1:]  # 这里特意对第一个字符变成\uxxxx的形式
        return word

    def read_operator(self, prefix=''):
        def grow(op):
            ch = self.peek()
            if not ch:
                return op
            bigger = op + ch
            if bigger in Cst.OPERATORS:
                self.next()
                return grow(bigger)
            else:
                return op
        return self.token(Token.OPERATOR, grow(prefix or self.next()))

    # 处理点号
    def handle_dot(self):
        self.next()
        ch = self.peek()
        if ch == '.':  # 字符串拼接操作符 ..
            self.next()
            return self.token(Token.OPERATOR, '..')
        if Kit.is_digit(ch):
            return self.read_number('.')
        return self.token(Token.PUNC, '.')

    # 处理减号
    def handle_minus(self):
        self.next()
        if self.peek() == '-':
            comments = self.comments_before
            if comments is None:
                self.comments_before = comments = []
            if self.next_is('[['):  # 多行注释 '--[['
                self.next()  # 吃掉1个'['
                self.next()  # 吃掉1个'['
                comments.append(self.read_multiline_comment())
            else:  # 单行注释 '--'
                comments.append(self.read_line_comment())
            return self.next_token()  # 注释的token不会参与语法解析，所以取下个token返回。
        return self.read_operator('-')

    def read_line_comment(self):
        self.next()
        ret, i = '', self.search('\n')
        if i == -1:
            ret = self.text[self.pos:]
            self.pos = self.length
        else:
            ret = self.text[self.pos:i]
            self.pos = i
        return self.token(Token.COMMENT_LINE, ret, True)

    def read_multiline_comment(self):
        self.next()
        return self.with_eof_error(self._block_comment_cont, 'Unterminated multiline comment')

    # 处理中括号
    def handle_square(self):
        if self.next_is('[') or self.next_is('='):
            return self.read_string()
        self.next()
        return self.token(Token.PUNC, '[')

    # 读一个串 看看是什么token
    def guess_token(self):
        word = self.read_word()
        if word not in Cst.KEYWORDS:
            return self.token(Token.NAME, word)
        if word in Cst.OPERATORS:
            return self.token(Token.OPERATOR, word)
        if word in Cst.KEYWORDS_ATOM:
            return self.token(Token.ATOM, word)
        return self.token(Token.KEYWORD, word)

    def next_token(self):
        self.skip_whitespace()
        self.start_token()
        ch = self.peek()
        if not ch:
            return self.token(Token.EOF)
        if Kit.is_digit(ch):
            return self.read_number()
        if ch == '"' or ch == "'":
            return self.read_string()
        if ch == '[':
            return self.handle_square()
        if ch in Cst.PUNC_CHARS:
            return self.token(Token.PUNC, self.next())
        if ch == '.':
            return self.handle_dot()
        if ch == '-':
            return self.handle_minus()
        if ch in Cst.OPERATOR_CHARS:
            return self.read_operator()
        if ch == '\\' or Kit.is_identifier_start(ch):
            return self.guess_token()
        self.throw_error("Unexpected character '" + ch + "'")

# 语法分析器, 建立AST树.
class SyntaxParser:
    ATOMIC_TOKEN_MAPPIGNG = {
        Token.NUMBER: Statement.ATOM_NUMBER,
        Token.STRING: Statement.ATOM_STRING,
        Token.RAWSTR: Statement.ATOM_RAWSTR,
        Token.ATOM: Statement.ATOM,
        Token.NAME: Statement.NAME
    }

    def __init__(self):
        self._input = Tokenizer()

    def start(self, text, exigent_mode=False):
        self._exigent_mode = exigent_mode  # 严格模式 (exigent_mode=False)
        self._prev = None
        self._peeked = None  # 向前看一个token
        self._in_function = 0
        self._in_va_arg = 0  # 任意参数函数中
        self._in_loop = 0
        self._in_table = 0  # 在table语句中 {}
        self._in_ifbody = 0  # 在if语句中
        self._input.start(text)

    def ast(self):
        array = []
        self._token = self._input.next_token()
        while not self._is(Token.EOF):
            stat = self._statement()
            array.append(stat)
        return self._as(Statement.TOP, array)

    def dump(self):
        array = []
        while True:
            tok = self._input.next_token()
            if tok.tokis == Token.EOF:
                break
            array.append(tok)
        print(array)

    # 将参数转成数组
    @staticmethod
    def _as(*args):
        return args

    # 当前token的类型跟值对不对得上
    def _is(self, tokis, value=None):
        return self._is_token(self._token, tokis, value)

    @staticmethod
    def _is_token(token, tokis, value=None):
        return token.tokis == tokis and (value is None or token.value == value)

    def _peak(self):
        if not self._peeked:
            self._peeked = self._input.next_token()
        return self._peeked

    def _next(self):
        self._prev = self._token
        if self._peeked:
            self._token = self._peeked
            self._peeked = None
        else:
            self._token = self._input.next_token()
        # if self._token.comments_before:
        #     print(self._token.comments_before)
        return self._token

    def _croak(self, msg, row=None, col=None, pos=None):
        row = self._input.tokrow if row is None else row
        col = self._input.tokcol if col is None else col
        pos = self._input.tokpos if pos is None else pos
        Kit.throw_parse_error(msg, row+1, col+1, pos+1)

    def _token_error(self, token, msg):
        self._croak(msg, token.row, token.col)

    def _unexpected(self, token=None):
        if token is None:
            token = self._token
        self._token_error(token, "Unexpected token:(%s %s)" % (token.tokis.value, token.value))

    # 看看当前token是不是符合当前状态，是的话拿出下一个token。
    def _expect_token(self, tokis, value):
        if self._is(tokis, value):
            return self._next()
        self._token_error(self._token, "Unexpected token %s, expected %s" % (self._token.tokis.value, tokis.value))

    def _expect(self, punc):
        return self._expect_token(Token.PUNC, punc)

    # 自动插入分号
    def _can_insert_semicolon(self):
        # 插入分号的条件是exigent_mode = false，严格模式：
        # 1. 当前token与上个token之间是否有换行
        # 2. 遇到end if ${expr} then ${body} end
        # 3. 文件尾
        if self._exigent_mode:
            return True
        if self._token.nlb or self._is(Token.EOF) or self._is(Token.KEYWORD, 'end'):
            return True
        if self._is_token(self._prev, Token.PUNC, ')'):
            return True
        if self._in_ifbody and self._is(Token.KEYWORD, 'else'):
            return True
        return False

    # 状态：分号
    def _semicolon(self, auto_instert=False):
        if self._is(Token.PUNC, ';'):
            self._next()  # 如果当前token是分号 则继续
        elif auto_instert and not self._can_insert_semicolon():
            self._unexpected()  # 如果不能自动插入分号就报错

    # 状态：语句块
    def _statement(self):
        tokis, tokva = self._token.tokis, self._token.value
        if tokis == Token.KEYWORD:
            self._next()  # 吃掉关键字
            if tokva == 'if':
                stat = self._stat_if()
            if tokva == 'for':
                stat = self._stat_for()
            if tokva == 'while':
                stat = self._stat_while()
            if tokva == 'do':
                stat = self._stat_block()
            if tokva == 'function':
                stat = self._stat_function(in_statement=True)
            if tokva == 'return':
                stat = self._stat_return()
            if tokva == 'break':
                stat = self._stat_break(tokva)
            if tokva == 'repeat':
                stat = self._stat_repeat()
            if tokva == 'local':
                stat = self._stat_local()
            self._semicolon()
            return stat
        return self._stat_simple()

    # 最小的语句
    def _stat_simple(self):
        expr = self._expression()
        self._semicolon(auto_instert=True)
        return self._as(Statement.STAT, expr)

    def _stat_local(self):
        # local function
        if self._is(Token.KEYWORD, 'function'):
            self._next()
            stat = self._stat_function(in_statement=True)
            return self._as(Statement.LOCAL, stat)
        # local a, b, c = 1, 2, 3
        vardefs, assigns = [], None
        while self._is(Token.NAME):
            vardefs.append(self._token.value)
            self._next()
            if self._is(Token.PUNC, ','):
                self._next()
            else:
                break
        if self._is(Token.OPERATOR, '='):
            self._next()
            assigns = []
            for i in range(len(vardefs)):
                assigns.append(self._expression(commas=False))
                if self._is(Token.PUNC, ','):
                    self._next()
                else:
                    break
        return self._as(Statement.LOCAL, vardefs, assigns)

    def _stat_name(self):
        ref = self._token.value
        self._next()  # 吃掉这个声明或引用名
        return self._as(Statement.NAME, ref)

    def _stat_if(self):
        def is_in_body(kw=Token.KEYWORD):
            return self._is(kw, 'elseif') or self._is(kw, 'else') or self._is(kw, 'end')
        if_body, elseif_list, else_body = [], [], None
        if_cond = self._expression()
        self._expect_token(Token.KEYWORD, 'then')
        self._in_ifbody += 1
        while not is_in_body():
            if_body.append(self._statement())
        self._in_ifbody -= 1
        while self._is(Token.KEYWORD, 'elseif'):
            self._next()
            cond = self._expression()
            self._expect_token(Token.KEYWORD, 'then')
            self._in_ifbody += 1
            body = []
            while not is_in_body():
                body.append(self._statement())
            self._in_ifbody -= 1
            elseif_list.append((cond, body))
        if self._is(Token.KEYWORD, 'else'):
            self._next()
            self._in_ifbody += 1
            else_body = self._cont_block_end()
            self._in_ifbody -= 1
        else:
            self._expect_token(Token.KEYWORD, 'end')
        return self._as(Statement.IF, (if_cond, if_body or None), elseif_list or None, else_body)

    # for
    def _stat_for(self):
        if not self._is(Token.NAME):
            self._unexpected()
        tok = self._peak()  # check next token
        if self._is_token(tok, Token.OPERATOR, '='):
            return self._for_step()
        if self._is_token(tok, Token.PUNC, ',') or self._is_token(tok, Token.OPERATOR, 'in'):
            return self._for_iter()
        self._unexpected(tok)

    def _for_step(self):
        index = self._stat_name()  # index
        if self._is(Token.OPERATOR):
            opr = self._token.value
            if opr in Cst.ASSIGNMENT:
                self._next()
                right = self._expression(commas=False)
                index = self._as(Statement.ASSIGN, opr, index, right)
            else:
                self._unexpected()
        self._expect(',')
        limit = self._expression()  # limit
        # step
        if self._is(Token.PUNC, ','):
            self._next()  # 吃掉逗号
            step = self._expression()
        else:
            step = None  # 默认step=1
        self._expect_token(Token.KEYWORD, 'do')  # 吃掉 do
        loop = self._in_loop_block('end')
        return self._as(Statement.FOR, index, limit, step, loop)

    def _for_iter(self):
        names = [self._stat_name()]  # 至少有个iter接收变量
        while True:
            if self._is(Token.PUNC, ','):
                self._next()  # 吃掉 ,
                names.append(self._stat_name())
            else:
                break
        self._expect_token(Token.OPERATOR, 'in')  # 吃掉 in
        itr = self._expression()  # 读取迭代器
        self._expect_token(Token.KEYWORD, 'do')  # 吃掉 do
        loop = self._in_loop_block('end')
        return self._as(Statement.FOR_IN, names, itr, loop)

    def _stat_while(self):
        cond = self._expression()
        self._expect_token(Token.KEYWORD, 'do')
        body = self._in_loop_block('end')
        return self._as(Statement.WHILE, cond, body)

    # repeat-until
    def _stat_repeat(self):
        body = self._in_loop_block('until')
        cond = self._expression()
        return self._as(Statement.DO_WHILE, cond, body)

    def _in_loop_block(self, end):
        self._in_loop += 1
        body = self._cont_block_end(end)
        self._in_loop -= 1
        return body

    # do-end
    def _stat_block(self):
        return self._as(Statement.BLOCK, self._cont_block_end())

    def _cont_block_end(self, end='end'):
        body = []
        while not self._is(Token.KEYWORD, end):
            if self._is(Token.EOF):
                self._unexpected()
            else:
                body.append(self._statement())
        self._next()  # 吃掉end
        return body or None

    def _stat_function(self, in_statement):
        # function name
        func_names = None
        if in_statement:
            func_names = []
            while not self._is(Token.PUNC, '('):
                if self._is(Token.NAME) or self._is(Token.PUNC, '.') or self._is(Token.PUNC, ':'):
                    func_names.append(self._token.value)
                    self._next()
                else:
                    self._unexpected()
        # function arguments
        self._expect('(')
        args, first, has_va_arg = [], True, False
        while not self._is(Token.PUNC, ')'):
            if first:
                first = False
            else:
                self._expect(',')
                if self._is(Token.PUNC, ')'):
                    if self._exigent_mode:
                        self._unexpected()  # 严格模式下不允许逗号后面跟右圆括号
                    else:
                        break
            if self._is(Token.NAME):
                args.append(self._token.value)
                self._next()  # 吃掉参数
                continue
            if self._is_va_arg():
                self._next()  # 吃掉两个点
                self._next()  # 吃掉一个点
                if self._is(Token.PUNC, ')'):
                    args.append('...')  # 变长参数
                    has_va_arg = True
                    continue
            self._unexpected()  # 只能是变量名称或任意参数
        self._next()  # 吃掉右括号
        # function body
        in_loop = self._in_loop
        self._in_loop = 0
        self._in_function += 1
        self._in_va_arg += (1 if has_va_arg else 0)
        body = self._cont_block_end()
        self._in_va_arg -= (1 if has_va_arg else 0)
        self._in_function -= 1
        self._in_loop = in_loop
        # pack statement
        return self._as(Statement.FUNCTION, func_names, args or None, body or None)

    def _stat_return(self):
        if self._is(Token.PUNC, ';'):
            self._next()
            expr = None
        else:
            if self._can_insert_semicolon():
                expr = None
            else:
                expr = self._expression()
                self._semicolon()
        stat = self._as(Statement.RETURN, expr)
        if self._in_function or self._in_ifbody or self._is(Token.EOF):
            return stat
        self._croak('"return" outside of function')

    # 状态：循环中断 'break'
    def _stat_break(self, word):
        if self._in_loop == 0:  # 不在循环中肯定不能用break
            self._croak(word + ' not inside a loop or switch')
        self._semicolon()
        return self._as(Statement.BREAK)

    # 表达式
    # commas 遇到逗号是否继续延伸
    def _expression(self, commas=True):
        expr = self._maybe_assign(commas)
        if not commas or not self._is(Token.PUNC, ','):
            return expr  # 不能进行 a, b, c 语句读取
        seq = [expr]
        self._next()
        seq.append(self._maybe_binary(commas))
        while True:
            if self._is(Token.PUNC, ','):
                self._next()
                seq.append(self._maybe_binary(commas))
            else:
                seq = self._as(Statement.SEQ, seq)
                if self._is(Token.OPERATOR, '='):  # a, b = b, a
                    return self._expr_assign(seq, commas)
                return seq

    # 赋值操作表达式
    def _maybe_assign(self, commas):
        left = self._maybe_binary(commas)
        if self._is(Token.OPERATOR) and (self._token.value in Cst.ASSIGNMENT):
            return self._expr_assign(left, commas)
        return left

    # 检查是否是二元操作符
    def _maybe_binary(self, commas, min_prec=0):
        expr = self._maybe_unary(commas)
        return self._expr_op(expr, min_prec, commas)

    # 检查是否是一元操作符
    def _maybe_unary(self, commas):
        if self._is(Token.OPERATOR):
            tokva = self._token.value
            if tokva in Cst.UNARY_PREFIX:
                self._next()
                expr = self._maybe_unary(commas)
                return self._as(Statement.UNARY, tokva, expr)
        return self._expr_atom(commas)

    # 表达式: 二元操作符
    def _expr_op(self, left, min_prec, commas):
        oper = self._token.value if self._is(Token.OPERATOR) else None
        prec = None if oper is None else Cst.PRECEDENCE.get(oper)
        # 大于当前的优先级 才能解析到当前的表达式
        if (prec is not None) and (prec > min_prec):
            self._next()
            # expr = a+b/c;
            right = self._expr_op(self._maybe_unary(commas), prec, commas)
            left2 = self._as(Statement.BINARY, oper, left, right)
            return self._expr_op(left2, min_prec, commas)
        return left

    # 表达式: 赋值
    def _expr_assign(self, left, commas):
        if not self._is_assignable(left):
            self._croak('Invalid assignment')
        oper = self._token.value  # 赋值操作符
        self._next()
        right = self._expression(commas)
        return self._as(Statement.ASSIGN, oper, left, right)

    # 表达式：元表达式
    # 映射成：a.b | a["b"] | a.c() | {a:1} | function x();
    def _expr_atom(self, commas):
        if self._is(Token.PUNC):
            tokva = self._token.value
            if tokva == '(':
                self._next()
                expr = self._expression(commas)
                self._expect(')')
                return self._subscripts(self._as(Statement.TUPLE, expr), commas)
            if tokva == '{':
                self._next()
                return self._subscripts(self._expr_table(), commas)
            if tokva == '[':
                if self._in_table:
                    self._next()
                    expr = self._expression(commas)
                    self._expect(']')
                    return self._subscripts(self._as(Statement.SUB_KEY, expr), commas)
            self._unexpected()
        # 闭包
        if self._is(Token.KEYWORD, 'function'):
            self._next()
            return self._subscripts(self._stat_function(False), commas)
        # 原子常量或变量名
        if self._token.tokis in self.ATOMIC_TOKEN_MAPPIGNG:
            stat_type = self.ATOMIC_TOKEN_MAPPIGNG[self._token.tokis]
            atom = self._as(stat_type, self._token.value)
            self._next()
            return self._subscripts(atom, commas)
        # 任意参数
        if self._in_function and self._in_va_arg and self._is_va_arg():
            atom = self._as(Statement.ATOM_VA_ARG)
            self._next()
            self._next()
            return self._subscripts(atom, commas)
        self._unexpected()

    def _subscripts(self, expr, commas):
        if self._is(Token.PUNC):
            tokva = self._token.value
            if tokva == '.':
                self._next()
                stat = self._as(Statement.DOT, expr, self._as_name())
                return self._subscripts(stat, commas)
            if tokva == ':':
                self._next()
                stat = self._as(Statement.COLON, expr, self._as_name())
                return self._subscripts(stat, commas)
            if tokva == '[':
                self._next()
                sub_expr = self._expression(commas)
                self._expect(']')
                stat = self._as(Statement.SUB, expr, sub_expr)  # table[${expr}]
                return self._subscripts(stat, commas)
            if tokva == '(':
                self._next()
                args = self._as_list(')')  # arguments
                stat = self._as(Statement.CALL, expr, args)
                return self._subscripts(stat, commas)
            if tokva == '{':
                if self._is_callable(expr):  # 函数唯一参数是table时调用可省略圆括号 function {}
                    self._next()  # 吃掉 {
                    args = self._expr_table()
                    stat = self._as(Statement.CALL_TABLE, expr, args)
                    return self._subscripts(stat, commas)
        if self._is(Token.STRING):
            if self._is_callable(expr):  # 函数唯一参数是字符串时调用可省略圆括号 function ""
                stat = self._as(Statement.CALL_STRING, expr, self._token.value)
                self._next()
                return self._subscripts(stat, commas)
        if self._is(Token.RAWSTR):
            if self._is_callable(expr):  # 函数唯一参数是字符串时调用可省略圆括号 function [[]]
                stat = self._as(Statement.CALL_RAWSTR, expr, self._token.value)
                self._next()
                return self._subscripts(stat, commas)
        return expr

    def _expr_table(self):
        array, first = [], True
        self._in_table += 1
        while not self._is(Token.PUNC, '}'):
            if first:
                first = False
            else:
                self._semicolon()
                if self._is(Token.PUNC, ','):
                    self._next()
                if self._is(Token.PUNC, '}'):
                    if self._exigent_mode:
                        self._unexpected()  # 严格模式下不允许逗号后面跟右大括号
                    else:
                        break
            key = self._expression(commas=False)
            if self._is(Token.PUNC, '='):
                self._next()
                val = self._expression(commas=False)
                array.append(self._as(Statement.ASSIGN, '=', key, val))
            else:
                array.append(key)
        self._next()  # 吃掉 }
        self._in_table -= 1
        return self._as(Statement.TABLE, array or None)

    def _as_list(self, closing, allow_trailing_comma=False, allow_empty=False):
        array, first = [], True
        while not self._is(Token.PUNC, closing):
            if first:
                first = False
            else:
                self._expect(',')
                if self._is(Token.PUNC, closing):
                    if allow_trailing_comma:
                        break  # 允许最末尾加逗号 {a,b,c,}
                    else:
                        self._unexpected()
            if self._is(Token.PUNC, ','):
                if allow_empty:
                    array.append(self._as(Statement.ATOM, 'nil'))  # 允许空值 例如[a,,v]
                else:
                    self._unexpected()
            else:
                array.append(self._expression(commas=False))
        self._next()
        return array

    def _as_name(self):
        tokis, tokva = self._token.tokis, self._token.value
        if tokis == Token.NAME:
            self._next()
            return tokva
        if not self._exigent_mode:
            if tokis == Token.KEYWORD or tokis == Token.OPERATOR or tokis == Token.ATOM:
                self._next()
                return tokva
        self._unexpected()

    # 判断是否是任意参数
    def _is_va_arg(self):
        return self._is(Token.OPERATOR, '..') and self._is_token(self._peak(), Token.PUNC, '.')

    # 判断左边是否可以赋值
    def _is_assignable(self, left):
        s = left[0]
        if self._in_table and s == Statement.SUB_KEY:
            return True
        return s == Statement.DOT or s == Statement.SUB or s == Statement.NAME or s == Statement.SEQ

    @staticmethod
    def _is_callable(left):
        # self._is_token(self._prev, Token.NAME)
        s = left[0]
        return s == Statement.DOT or s == Statement.COLON or s == Statement.SUB or s == Statement.NAME

# 语法树渲染器
class AstRenderer:

    def render_ast(self, ast):
        print(ast)
        s = ''
        for stat in ast[1]:
            s += self.render_stat(stat, 0, 1)
        return s

    def render_stat(self, stat, indent, newline):
        s, stat_type = '', stat[0]
        if stat_type == Statement.STAT:
            s = self.render_expr(stat[1], indent)
        elif stat_type == Statement.LOCAL:
            s = self._make_stat_local(stat, indent)
        elif stat_type == Statement.FUNCTION:
            s = self._make_stat_method(stat, indent)
        elif stat_type == Statement.IF:
            s = self._make_stat_if(stat, indent)
        elif stat_type == Statement.FOR:
            s = self._make_stat_for(stat, indent)
        elif stat_type == Statement.FOR_IN:
            s = self._make_stat_forin(stat, indent)
        elif stat_type == Statement.WHILE:
            s = self._make_stat_while(stat, indent)
        elif stat_type == Statement.DO_WHILE:
            s = self._make_stat_dowhile(stat, indent)
        elif stat_type == Statement.BLOCK:
            s = self._make_stat_block(stat, indent)
        elif stat_type == Statement.RETURN:
            s = self._make_stat_return(stat, indent)
        elif stat_type == Statement.BREAK:
            s = 'break'
        elif stat_type == Statement.HOOK:
            s = stat[1]
        else:
            raise LuaRenderError('unsupport stat ' + stat_type)
        return '\t' * indent + s + '\n' * newline

    def render_expr(self, expr, indent):
        s, expr_type = '', expr[0]
        if expr_type == Statement.FUNCTION:
            s = self._make_stat_method(expr, indent)  # closure
        elif expr_type == Statement.CALL:
            s = self._make_expr_call(expr, indent)
        elif expr_type == Statement.CALL_TABLE:
            s = self._make_expr_calltable(expr, indent)
        elif expr_type == Statement.CALL_STRING:
            s = self._make_expr_callstring(expr, indent)
        elif expr_type == Statement.CALL_RAWSTR:
            s = self._make_expr_callrawstr(expr, indent)
        elif expr_type == Statement.ASSIGN:
            s = self._make_expr_assign(expr, indent)
        elif expr_type == Statement.NAME:
            s = expr[1]
        elif expr_type == Statement.ATOM:
            s = expr[1]
        elif expr_type == Statement.ATOM_NUMBER:
            s = expr[1]
        elif expr_type == Statement.ATOM_VA_ARG:
            s = '...'
        elif expr_type == Statement.ATOM_STRING:
            s = self._make_expr_string(expr[1])
        elif expr_type == Statement.ATOM_RAWSTR:
            s = self._make_expr_rawstr(expr[1])
        elif expr_type == Statement.SEQ:
            s = self._make_expr_seq(expr, indent)
        elif expr_type == Statement.SUB:
            s = self._make_expr_sub(expr, indent)
        elif expr_type == Statement.DOT:
            s = self._make_expr_dot(expr, indent)
        elif expr_type == Statement.COLON:
            s = self._make_expr_colon(expr, indent)
        elif expr_type == Statement.UNARY:
            s = self._make_expr_unary(expr, indent)
        elif expr_type == Statement.BINARY:
            s = self._make_expr_binary(expr, indent)
        elif expr_type == Statement.TABLE:
            s = self._make_expr_table(expr, indent)
        elif expr_type == Statement.SUB_KEY:
            s = self._make_expr_subkey(expr, indent)
        elif expr_type == Statement.TUPLE:
            s = self._make_expr_tuple(expr, indent)
        else:
            raise LuaRenderError('unsupport expr ' + expr_type)
        return s

    def _make_stat_method(self, stat, indent):
        s = ''
        if stat[1]:
            s += ''.join(stat[1])
        s += '(' + self._make_expr_seqstr(stat[2]) + ')\n'
        if stat[3]:
            for st in stat[3]:
                s += self.render_stat(st, indent + 1, 1)
        return 'function ' + s + '\t' * indent + 'end'

    def _make_stat_if(self, stat, indent):
        s, if_block, elif_block, else_block = '', stat[1], stat[2], stat[3]
        s += self.render_expr(if_block[0], indent) + ' then\n'
        if if_block[1]:
            for st in if_block[1]:
                s += self.render_stat(st, indent + 1, 1)
        if elif_block:
            for it in elif_block:
                s += '\t' * indent + 'elseif ' + self.render_expr(it[0], indent) + ' then\n'
                for st in it[1]:
                    s += self.render_stat(st, indent + 1, 1)
        if else_block:
            s += '\t' * indent + 'else\n'
            for st in else_block:
                s += self.render_stat(st, indent + 1, 1)
        return 'if ' + s + '\t' * indent + 'end'

    def _make_stat_for(self, stat, indent):
        s = self.render_expr(stat[1], indent) + ', ' + self.render_expr(stat[2], indent)
        if stat[3]:
            s += ', ' + self.render_expr(stat[3], indent)
        s += ' do\n'
        if stat[4]:
            for st in stat[4]:
                s += self.render_stat(st, indent + 1, 1)
        return 'for ' + s + '\t' * indent + 'end'

    def _make_stat_forin(self, stat, indent):
        s = '%s in %s do\n' % (self._make_expr_seqexpr(stat[1], indent), self.render_expr(stat[2], indent))
        if stat[3]:
            for st in stat[3]:
                s += self.render_stat(st, indent + 1, 1)
        return 'for ' + s + '\t' * indent + 'end'

    def _make_stat_while(self, stat, indent):
        s = self.render_expr(stat[1], indent) + ' do\n'
        if stat[2]:
            for st in stat[2]:
                s += self.render_stat(st, indent + 1, 1)
        return 'while ' + s + '\t' * indent + 'end'

    def _make_stat_dowhile(self, stat, indent):
        s = ''
        if stat[2]:
            for st in stat[2]:
                s += self.render_stat(st, indent + 1, 1)
        return 'repeat\n' + s + '\t' * indent + 'until ' + self.render_expr(stat[1], indent)

    def _make_stat_block(self, stat, indent=0):
        s = ''
        if stat[1]:
            for st in stat[1]:
                s += self.render_stat(st, indent + 1, 1)
        return 'do\n' + s + '\t' * indent + 'end'

    def _make_stat_local(self, stat, indent):
        s = ''
        if stat[1][0] == Statement.FUNCTION:
            s += self._make_stat_method(stat[1], indent)
        else:
            s += self._make_expr_seqstr(stat[1])
            if stat[2]:
                s += ' = ' + self._make_expr_seqexpr(stat[2], indent)
        return 'local ' + s

    def _make_stat_return(self, stat, indent):
        s = ''
        if stat[1]:
            s = ' ' + self.render_expr(stat[1], indent)
        return 'return' + s

    def _make_expr_assign(self, expr, indent, sep=' '):
        return self.render_expr(expr[2], indent) + sep + expr[1] + sep + self.render_expr(expr[3], indent)

    def _make_expr_call(self, expr, indent):
        return self.render_expr(expr[1], indent) + '(' + self._make_expr_seqexpr(expr[2], indent) + ')'

    def _make_expr_calltable(self, expr, indent):
        return self.render_expr(expr[1], indent) + ' ' + self._make_expr_table(expr[2], indent)

    def _make_expr_callstring(self, expr, indent):
        return self.render_expr(expr[1], indent) + ' ' + self._make_expr_string(expr[2])

    def _make_expr_callrawstr(self, expr, indent):
        return self.render_expr(expr[1], indent) + ' ' + self._make_expr_rawstr(expr[2])

    def _make_expr_binary(self, expr, indent, sep=' '):
        return self.render_expr(expr[2], indent) + sep + expr[1] + sep + self.render_expr(expr[3], indent)

    def _make_expr_unary(self, expr, indent, sep=' '):
        right = self.render_expr(expr[2], indent)
        return (expr[1] + right) if (expr[1] == '#') else (expr[1] + sep + right)

    def _make_expr_colon(self, expr, indent):
        return self.render_expr(expr[1], indent) + ':' + expr[2]

    def _make_expr_dot(self, expr, indent):
        return self.render_expr(expr[1], indent) + '.' + expr[2]

    def _make_expr_sub(self, expr, indent):
        return self.render_expr(expr[1], indent) + '[' + self.render_expr(expr[2], indent) + ']'

    def _make_expr_tuple(self, expr, indent):
        return '(' + self.render_expr(expr[1], indent) + ')'

    def _make_expr_subkey(self, expr, indent):
        return '[' + self.render_expr(expr[1], indent) + ']'

    def _make_expr_seq(self, expr, indent):
        return self._make_expr_seqexpr(expr[1], indent)

    def _make_expr_table(self, expr, indent, sep=', '):
        if not expr[1]:
            return '{}'
        if len(expr[1]) < 5:
            s = ''
            for item in expr[1]:
                if item[0] == Statement.ASSIGN:
                    s += self._make_expr_assign(item, indent)
                else:
                    s += self.render_expr(item, indent)
                s += sep
            return '{' + s[0: len(s) - len(sep)] + '}'
        else:
            s = ''
            for item in expr[1]:
                s += '\t' * (indent + 1)
                if item[0] == Statement.ASSIGN:
                    s += self._make_expr_assign(item, indent)
                else:
                    s += self.render_expr(item, indent)
                s += sep + '\n'
            return '{\n' + s[0: len(s) - len(sep) - 1] + '\n' + '\t' * indent + '}'

    @staticmethod
    def _make_expr_string(text):
        return '"%s"' % text

    @staticmethod
    def _make_expr_rawstr(text):
        return ('[====[%s]====]' % text) if (text.startswith('[')) else ('[[%s]]' % text)

    @staticmethod
    def _make_expr_seqstr(seq, sep=', '):
        if not seq:
            return ''
        s = ''
        for it in seq:
            s += it + ', '
        return s[0: len(s) - len(sep)]

    def _make_expr_seqexpr(self, seq, indent, sep=', '):
        if not seq:
            return ''
        s = ''
        for it in seq:
            s += self.render_expr(it, indent) + sep
        return s[0: len(s) - len(sep)]