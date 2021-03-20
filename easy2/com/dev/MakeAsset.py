# -*- coding: utf-8 -*-
# @Time    : 2018/5/24 11:19 AM
# @Author  : Joli
# @Email   : 99755349@qq.com

import os
import re
import shutil
import time
import random
from jonlin.utils import Log, FS, Bit, Math, Rand, Crypto

log = Log.Logger(__file__)

# 命名规则
class Ruler:
    # C语言关键字
    _KEYWORDS = (
        'alignas',
        'alignof',
        'and',
        'and_eq',
        'asm',
        'atomic_cancel',
        'atomic_commit',
        'atomic_noexcept',
        'auto',
        'bitand',
        'bitor',
        'bool',
        'break',
        'case',
        'catch',
        'char',
        'char16_t',
        'char32_t',
        'class',
        'compl',
        'concept',
        'const',
        'constexpr',
        'const_cast',
        'continue',
        'decltype',
        'default',
        'delete',
        'do',
        'double',

        'dynamic_cast',
        'else',
        'enum',
        'explicit',
        'export',
        'extern',
        'false',
        'float',
        'for',
        'friend',
        'free',
        'goto',
        'if',
        'import',
        'inline',
        'int',
        'long',
        'malloc',
        'module',
        'mutable',
        'namespace',
        'new',
        'noexcept',
        'not',
        'not_eq',
        'nullptr',
        'operator',
        'or',
        'or_eq',
        'private',
        'protected',
        'public',
        'register',

        'reinterpret_cast',
        'requires',
        'return',
        'short',
        'signed',
        'sizeof',
        'static',
        'static_assert',
        'static_cast',
        'struct',
        'switch',
        'synchronized',
        'template',
        'this',
        'thread_local',
        'throw',
        'true',
        'try',
        'typedef',
        'typeid',
        'typename',
        'union',
        'unsigned',
        'using',
        'virtual',
        'void',
        'volatile',
        'wchar_t',
        'while',
        'xor',
        'xor_eq',

        'nil',
        'null',
        'self',
        'super',
        'alloc',
        'dealloc',
        'retain',
        'release',
        'nonatomic',
        'readwrite',
        'readonly',
        'assign',
        'atomic',
        'strong',
        'copy'
    )
    # 危险词
    _BADWORDS = (
        'qq', 'wx', 'weixin', 'wechat', 'alipay', 'alipays',
        'ios', 'apple', 'android', 'google', 'facebook',
        'http', 'https', 'webview', 'webkit', 'web', 'ftp', 'cdn', 'url', 'h5',  'remote',
        'javascript', 'lua', 'python', 'php',
        'dlopen', 'dlsym', 'respondsToSelector', 'performSelector', 'safari', 'shell',
        'test', 'beta', 'demo', 'alpha', 'debug', 'bug',
        'pay', 'paid', 'payment', 'recharge', 'purchase', 'money', 'buy', 'rmb',
        'gift', 'puke', 'poker', 'fuck',
        'load', 'download', 'hotfix', 'confuse', 'hybrid', 'rollout'
    )
    # 敏感词
    _UNSAFEWORDS = _BADWORDS + _KEYWORDS

    # 诊断危险词
    @classmethod
    def isbad(cls, s):
        if s in cls._BADWORDS:
            return True
        for w in cls._BADWORDS:
            if s.find(w) != -1:
                return True
        return False

    # 诊断敏感词
    @classmethod
    def isunsafe(cls, s):
        return s in cls._UNSAFEWORDS

    # 生成小写字母串
    @classmethod
    def lowers(cls, size):
        s = ''
        for i in range(size):
            s += '%c' % random.randint(97, 122)
        return cls.lowers(size) if cls.isunsafe(s) else s

    # 生成大写字母串
    @classmethod
    def uppers(cls, size):
        return cls.lowers(size).upper()  # random.randint(65, 90)

    # 生成数字串
    @classmethod
    def digits(cls, size):
        s = ''
        for i in range(size):
            s += '%d' % random.randint(0, 9)
        return s

    # 生成字母和数字混合串
    @classmethod
    def alphas(cls, size):
        s = ''
        for i in range(size):
            s += '%d' % random.randint(0, 9) if random.random() < 0.5 else '%c' % random.randint(97, 122)
        return cls.alphas(size) if cls.isunsafe(s) else s

# 垃圾文件生成器
class LitterBuilder:

    def build(self, files, size, magic=b'xxtea'):
        nums = len(files)
        mlen = len(magic)
        size = size * 1024 * 1024
        for i in range(nums):
            fsize = Rand.bonus(size, nums-i, 1024)
            size -= fsize
            fbuff = self._build_buffer(fsize, magic, mlen)
            fpath = files[i]
            log.i('make litter %04d:%s' % (i+1, fpath))
            with open(fpath, 'wb') as fp:
                fp.write(fbuff)

    @staticmethod
    def _build_buffer(size, magic, mlen=0):
        ba = bytearray(size)
        for i in range(mlen):
            ba[i] = magic[i]
        for i in range(mlen, size):
            ba[i] = random.randint(0, 0xFF)
        # assert len(ba) == size, 'litter buffer wrong'
        return ba

# 资源包生成器
class AssetBuilder:
    # 资源包垃圾填充器
    class Filler:
        def __init__(self, size, nums):
            self._nums = nums
            self._size = round(size * 1024 * 1024)  # 剩余未填充的字节数
            self._less = random.randint(5, 15)

        def consume(self, fp):
            assert self._size > 0, 'fill overflow:%d' % self._size
            size = Rand.bonus(self._size, self._nums, self._less)
            assert size > 0, 'fill little:' % size
            log.d('fill consume:', self._nums, size)
            self._size -= size
            self._nums -= 1
            ba = bytearray(size)
            for i in range(size):
                ba[i] = random.randint(0, 0xFF)
            fp.write(ba)

    # 资源包文件加密器
    class Blurer:
        def __init__(self, blurkb):
            self._let = blurkb  # 加密阀值
            self._keylen = random.randint(65, 0xFF)
            self._key = bytearray(self._keylen)  # 秘钥
            for i in range(self._keylen):
                self._key[i] = random.randint(1, 0xFF)  # 不包括0

        def submit(self, buffer):  # 将加密信息记录到资源包
            buffer.append(self._keylen)
            buffer.extend(self._key)
            buffer.extend(Bit.u32_bytes(self._let))

        def encode(self, buf):
            size = len(buf)
            assert size > 0, 'encode empty buffer'
            if size > self._let:
                buf = self._encode_partion(buf, size, self._let)
            else:
                buf = Crypto.xor_bytes(buf, self._key)
            return buf

        def _encode_partion(self, buf, size, blur):
            p1 = int(blur * 0.5)
            p2 = size - (blur - p1)
            head = Crypto.xor_bytes(buf[:p1], self._key)
            body = buf[p1:p2]
            tail = Crypto.xor_bytes(buf[p2:], self._key)
            return head + body + tail

    def __init__(self, magic=b'asset', hseed=131, blend=False):
        self._magic = magic  # 魔数
        self._blend = blend  # 是否打乱文件排序
        self._hseed = hseed  # hash seed
        self._blurer = self._filler = None

    def pack(self, pkgfile, source, blurkb=0, fillmb=0):
        start_t = time.time()
        if blurkb > 0:
            self._blurer = self.Blurer(blurkb)
        self._filemap = {}
        with open(pkgfile, 'wb') as fp:
            self._fp = fp
            self._build(source, fillmb)
            self._fp = None
        self._dump_fileinfo(pkgfile)
        log.i('pack bale done, 耗时:%.2fs' % (time.time() - start_t))

    def _dump_fileinfo(self, pkgfile):
        if not self._filemap:
            return
        path = os.path.join(os.path.dirname(pkgfile), FS.filename(pkgfile) + '.txt')
        with open(path, 'w') as fp:
            for hashcode in self._filemap:
                tag = self._filemap[hashcode]
                fp.writelines('%d\t%s\n' % (hashcode, tag))

    def _load_taglist(self, source):
        taglist = FS.walk_files(source, cut=len(source) + 1)
        for i in range(len(taglist)-1, -1, -1):
            tag = taglist[i]
            if tag.endswith('.DS_Store') or tag.startswith('.svn'):
                log.d('ignore file:', tag)
                taglist.pop(i)
                continue
        if self._blend:
            random.shuffle(taglist)
        else:
            taglist.sort()
        return taglist

    def _build(self, source, fillmb):
        taglist = self._load_taglist(source)
        filenum = len(taglist)
        assert filenum <= 0xFFFF, 'file nums exceeds %u' % 0xFFFF
        self._hashmap = {}
        self._fp.write(self._magic)
        self._fp.write(b'0000')
        if fillmb > 0:
            self._filler = AssetBuilder.Filler(fillmb, filenum + 2)
            self._filler.consume(self._fp)
        for tag in taglist:
            self._add_file(tag, os.path.join(source, tag))
        offset = self._fp.tell()
        print('header offset:', offset)
        self._fp.seek(len(self._magic))
        self._fp.write(Bit.u32_bytes(offset))
        self._fp.seek(offset)
        self._fp.write(self._gen_header(filenum))
        if self._filler is not None:
            self._filler.consume(self._fp)

    def _gen_header(self, filenum):
        header = bytearray()
        if self._blurer is None:
            header.append(0)
        else:
            self._blurer.submit(header)
        header.extend(Bit.u16_bytes(self._hseed))
        header.extend(Bit.u16_bytes(filenum))
        for hashcode in self._hashmap:
            info = self._hashmap[hashcode]
            header.extend(Bit.u32_bytes(hashcode))
            header.extend(Bit.u32_bytes(info[0]))
            header.extend(Bit.u32_bytes(info[1]))
        return header

    def _add_file(self, tag, path):
        hashcode = Math.hash_bkdr(tag, self._hseed)
        log.i('pack file:', hashcode, tag)
        assert self._hashmap.get(hashcode) is None, 'file hashcode conflict:' + path
        with open(path, 'rb') as fp:
            fbuffer = fp.read()
        if fbuffer:
            if self._blurer is not None:
                fbuffer = self._blurer.encode(fbuffer)
            pos = self._fp.tell()
            self._hashmap[hashcode] = (pos, len(fbuffer))
            self._filemap[hashcode] = tag
            self._fp.write(fbuffer)
            if self._filler is not None:
                self._filler.consume(self._fp)

# 资源包
class AssetPackage:
    # 资源包文件解码器
    class Parser:
        def __init__(self, keylen):
            self._keylen = keylen

        def load(self, buffer):
            self._key = buffer[:self._keylen]
            self._let = Bit.u32_from(buffer[self._keylen:])

        def decode(self, buf):
            size = len(buf)
            if size > self._let:
                buf = self._decode_partion(buf, size, self._let)
            else:
                buf = Crypto.xor_bytes(buf, self._key)
            return buf

        def _decode_partion(self, buf, size, blur):
            p1 = int(blur * 0.5)
            p2 = size - (blur - p1)
            head = Crypto.xor_bytes(buf[:p1], self._key)
            body = buf[p1:p2]
            tail = Crypto.xor_bytes(buf[p2:], self._key)
            return head + body + tail

    def __init__(self, source, magic=b'asset'):
        self._source = source
        self._magic = magic
        self._parser = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._fp is not None:
            self._fp.close()
            self._fp = None
        self._parser = None

    def __enter__(self):
        self._fp = open(self._source, 'rb')
        self._check_magic()
        self._read_header()
        return self

    def _check_magic(self):
        m = self._fp.read(len(self._magic))
        assert self._magic == m, 'magic error: %s!=%s' % (self._magic, m)

    def _read_header(self):
        offset = Bit.u32_from(self._fp.read(4))
        self._fp.seek(offset)
        # 读取秘钥
        keylen = self._fp.read(1)[0]
        if keylen > 0:
            self._parser = self.Parser(keylen)
            self._parser.load(self._fp.read(keylen + 4))
        # 读取hash种子和文件数量
        buffer = self._fp.read(4)
        self._hseed = Bit.u16_from(buffer)
        filenum = Bit.u16_from(buffer[2:])
        # 读取文件表
        buffer = self._fp.read(filenum * 12)  # tag+pos+len=12
        offset = 0
        self._hashmap = {}
        for i in range(filenum):
            tag = Bit.u32_from(buffer[offset:offset+4])
            offset += 4
            pos = Bit.u32_from(buffer[offset:offset+4])
            offset += 4
            size = Bit.u32_from(buffer[offset:offset+4])
            offset += 4
            self._hashmap[tag] = (pos, size)
        log.d('unpack bale files:', filenum)

    def _read(self, info):
        self._fp.seek(info[0])
        buf = self._fp.read(info[1])
        if self._parser is not None:
            buf = self._parser.decode(buf)
        return buf

    def find(self, tag):
        tag = Math.hash_bkdr(tag, self._hseed)
        return self._hashmap.get(tag)

    def load(self, tag):
        info = self.find(tag)
        if info is not None:
            return self._read(info)

    def unpack(self, dest, refer, output=False):
        start_t = time.time()
        filenum, filemap = 0, {}
        for tag in FS.walk_files(refer, cut=len(refer) + 1):
            filemap[Math.hash_bkdr(tag, self._hseed)] = tag
        for hashcode in self._hashmap:
            if hashcode not in filemap:
                continue
            filename = filemap[hashcode]
            fileinfo = self._hashmap[hashcode]
            log.i('unpack file:', filename)
            buffer = self._read(fileinfo)
            if output:
                pos = os.path.join(dest, filename)
                FS.make_parent(pos)
                with open(pos, 'wb') as fp:
                    fp.write(buffer)
            else:
                assert len(buffer) == fileinfo[1], 'file error:' + filename
            filenum += 1
        log.i('unpack bale done, 数量:%d, 耗时:%.2fs' % (filenum, time.time() - start_t))

class EnDict:
    def __init__(self):
        # self._generate()
        self._resdir = os.path.abspath(os.path.join(__file__, '../../../../resource'))
        self._nounlist = FS.read_text(os.path.join(self._resdir, 'endict/starnoun1.txt')).split('\n')
        self._verblist = FS.read_text(os.path.join(self._resdir, 'endict/starnoun1.txt')).split('\n')
        self._nounimax = len(self._nounlist) - 1
        self._verbimax = len(self._verblist) - 1
        log.d(f'noun:{self._nounimax+1}, verb:{self._verbimax+1}')

    def _generate(self):
        re_lower = re.compile('^[a-z]+?$')

        def load(src, wlen):
            if not os.path.isfile(src):
                return []
            ws = FS.read_text(src).split('\n')
            for i in range(len(ws) - 1, -1, -1):
                w = ws[i]
                if not re_lower.match(w):
                    ws.pop(i)
                    continue
                n = len(w)
                if n < 2 or n > wlen:
                    ws.pop(i)
                    continue
                if Ruler.isbad(w):
                    ws.pop(i)
            return tuple(ws)

        ns = load(os.path.join(self._resdir, 'endict/starnoun.txt'), 7)
        vs = load(os.path.join(self._resdir, 'endict/starverb.txt'), 6)
        with open(os.path.join(self._resdir, 'endict/starnoun1.txt'), 'w') as f:
            f.write('\n'.join(ns))
        with open(os.path.join(self._resdir, 'endict/starverb1.txt'), 'w') as f:
            f.write('\n'.join(vs))

    def noun(self):  # 随机名词
        s = self._nounlist[random.randint(0, self._nounimax)]
        return self.noun() if Ruler.isunsafe(s) else s

    def verb(self):  # 随机动词
        s = self._verblist[random.randint(0, self._verbimax)]
        return self.verb() if Ruler.isunsafe(s) else s

    def sel(self, factor=0.8):
        return self.noun() if random.random() < factor else self.verb()
# 词典
ABC = EnDict()
# 垃圾代码生成器
class FakerBuilder:
    def __init__(self, liemb):
        self.max_liebytes = liemb * 1024 * 1024
        self.use_liebytes = 0
        self.cpp_helper = 'DataSupport'
        self.helper_ext = random.choice(('Helper', 'Utils', 'Tool', 'Kit', 'Mgr', 'Act'))
        self.noabc_bits = tuple([i for i in range(65) if i != 53 and i != 58] + [i for i in range(123, 256)])  # 单词后面不允许出现数字5，避免出现H5的情况。
        self.noabc_imax = len(self.noabc_bits) - 1

    def build(self, root, num_ac=1, num_ui=15, num_vc=10, num_md=8):
        FS.cleanup_dir(root)
        for i in range(num_md-1):
            fname, hbody, mbody = self._oc_md(random.randint(6, 20))
            FS.write_text(os.path.join(root, fname + '.h'), hbody)
            FS.write_text(os.path.join(root, fname + '.mm'), mbody)
        for i in range(num_ui):
            fname, hbody, mbody = self._oc_ui(random.randint(3, 15), random.randint(1, 9))
            FS.write_text(os.path.join(root, fname + '.h'), hbody)
            FS.write_text(os.path.join(root, fname + '.mm'), mbody)
        for i in range(num_vc):
            fname, hbody, mbody = self._oc_vc(random.randint(3, 10), random.randint(1, 9))
            FS.write_text(os.path.join(root, fname + '.h'), hbody)
            FS.write_text(os.path.join(root, fname + '.mm'), mbody)
        for i in range(num_ac):
            fname, hbody, mbody = self._oc_ac(random.randint(0, 5), random.randint(0, 5))
            FS.write_text(os.path.join(root, fname + '.h'), hbody)
            FS.write_text(os.path.join(root, fname + '.mm'), mbody)
        self._oc_bridge(root)

    def _oc_bridge(self, root):
        apis, maps = {}, {}
        for name, impl in {
            'showLogin': 'CPKit::singleton()->login()',
            'logout': 'CPKit::singleton()->logout()',
            'enterUserCenter': 'CPKit::singleton()->openUserCenter()',
            'createPlayer': 'CPKit::singleton()->onRoleCreated(UzoneBridge::transf(${dict}))',
            'enterComplete': 'CPKit::singleton()->onRoleLogin(UzoneBridge::transf(${dict}))',
            'tcBindPlayerGift': 'CPKit::singleton()->onRoleUseGift(UzoneBridge::transf(${dict}))',
            'roleChange': 'UzoneAdmin::singleton()->tagPlayer(UzoneBridge::transf(${dict}))',
            'sendDefaultSid': 'UzoneAdmin::singleton()->tagServer(UzoneBridge::transf(${dict}))',
            'uFeedback': 'UzoneAdmin::singleton()->feedback()',
            'initPushMessage': 'LocalPush::regist(UzoneBridge::transf(${dict}))',
            'registerScriptHandler': 'UzoneBridge::singleton()->registLuaHandler(${dict})',
            'versionUpdateWithAppVersion': 'UzoneBridge::singleton()->hotPatch(${dict})',
            'payment': 'UzoneBridge::payOrder(${dict})',
            'pasteboardString': 'UzoneBridge::setPasteboard(${dict})',
            'getopId': 'UzoneBridge::callLuaListener(${dict}, UzoneAdmin::singleton()->opid())',
            'getBundleId': 'UzoneBridge::callLuaListener(${dict}, Helper::getAppBundleId())',
            'getGameVersion': 'UzoneBridge::callLuaListener(${dict}, Helper::getAppVersion())',
            'getEquipmentModel': 'UzoneBridge::callLuaListener(${dict}, Helper::getDeviceModel())',
            'getSystemVersion': 'UzoneBridge::callLuaListener(${dict}, Helper::getSystemVersion())',
            'getMobileOperator': 'UzoneBridge::callLuaListener(${dict}, Helper::getNetOperator())',
            'getMobileNetwork': 'UzoneBridge::callLuaListener(${dict}, Helper::getNetStyle())',
            'getUUID': 'UzoneBridge::callLuaListener(${dict}, Helper::getUUID())',
            'getIDFA': 'UzoneBridge::callLuaListener(${dict}, Helper::getUUID())'
        }.items():
            func_name = self._oc_nf()
            if impl.find('${dict}') != -1:
                dict_name = ABC.noun()
                impl_text = impl.replace('${dict}', dict_name)
                func_text = f'NSLog(@"%s => %@", __func__, {dict_name});\n\t{impl_text};'
                func_body = f'+(void){func_name}:(NSDictionary*){dict_name}\n{{\n\t{func_text}\n}}'
            else:
                func_text = f'NSLog(@"%s", __func__);\n\t{impl};'
                func_body = f'+(void){func_name}\n{{\n\t{func_text}\n}}'
            apis[func_name] = func_body
            maps[func_name] = name
        # build body
        body_text = ''
        for i in range(random.randint(1, 3)):
            body_text += self._oc_function(host='+', size=random.randint(1, 3))
        for func_text in apis.values():
            body_text += func_text + '\n\n'
            body_text += self._oc_function(host='+', size=random.randint(1, 3))
        # write to disk
        fname = ABC.sel().capitalize() + self.helper_ext
        hbody = f'@interface {fname} : NSObject\n@end'
        mbody = f'''#import "{fname}.h"
#import "{self.cpp_helper}.h"
#import "UzoneBridge.h"
USING_NS_YOU;
\n
@implementation {fname}
{body_text}
@end'''
        FS.write_text(os.path.join(root, fname + '.h'), hbody)
        FS.write_text(os.path.join(root, fname + '.mm'), mbody)
        # print mapping
        print('--------------------------------------')
        for func_name in maps:
            s = ','.join([f'@"{c}"' for c in maps[func_name]])
            print(f'[md setObject:@"{func_name}" forKey:sumStr({s})];')
        print('UniteInterface', fname)

    def _oc_ac(self, num_funs=0, num_vars=0):
        memb_text, body_text = '', ''
        # 成员变量
        if num_vars > 0:
            for i in range(num_vars):
                t, n = self._oc_type(), f'_{ABC.sel(0.9)}'
                memb_text += f'\t{t} {n};\n'
            memb_text = memb_text[0:-1]
        # 必须实现接口
        body_text += f'-(BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions\n{{\n{self._oc_block(random.randint(1, 10))}\n\treturn YES;\n}}\n\n'
        body_text += f'-(void)applicationWillResignActive:(UIApplication *)application\n{{\n{self._oc_block(random.randint(1, 5), )}\n}}\n\n'
        body_text += f'-(void)applicationDidBecomeActive:(UIApplication *)application\n{{\n{self._oc_block(random.randint(1, 5))}\n}}\n\n'
        body_text += f'-(void)applicationDidEnterBackground:(UIApplication *)application\n{{\n{self._oc_block(random.randint(1, 5))}\n}}\n\n'
        body_text += f'-(void)applicationWillEnterForeground:(UIApplication *)application\n{{\n{self._oc_block(random.randint(1, 5))}\n}}\n\n'
        # 添加的函数
        for i in range(num_funs):
            body_text += self._oc_function(size=random.randint(1, 5))
        # 生成
        fname = self._oc_nc() + 'Controller'
        hbody = f'@interface {fname} : NSObject<UIApplicationDelegate>\n@end'
        mbody = f'''#import "{fname}.h"
#import "{self.cpp_helper}.h"
\n
@implementation {fname} 
{{
{memb_text}
}}\n
{body_text}
@end'''
        return fname, hbody, mbody

    def _oc_vc(self, num_funs=8, num_vars=8):
        memb_text, body_text = '', ''
        # 成员变量
        if num_vars > 0:
            for i in range(num_vars):
                t, n = self._oc_type(), f'_{ABC.sel(0.9)}'
                memb_text += f'\t{t} {n};\n'
            memb_text = memb_text[0:-1]
        # 必须实现接口
        body_text += f'-(void)loadView\n{{\n{self._oc_block(random.randint(1, 5))}\n}}\n\n'
        body_text += f'-(void)viewDidLoad\n{{\n\t[super viewDidLoad];\n{self._oc_block(random.randint(1, 5))}\n}}\n\n'

        body_text += f'-(void)viewWillAppear:(BOOL)animated\n{{\n\t[super viewWillAppear:animated];\n{self._oc_block(random.randint(1, 5))}\n}}\n\n'
        body_text += f'-(void)viewDidDisappear:(BOOL)animated\n{{\n\t[super viewDidDisappear:animated];\n{self._oc_block(random.randint(1, 5))}\n}}\n\n'

        body_text += '#ifdef __IPHONE_6_0\n'
        body_text += f'-(NSUInteger)supportedInterfaceOrientations\n{{\n\treturn {random.choice(("UIInterfaceOrientationMaskAllButUpsideDown", "UIInterfaceOrientationMaskLandscape"))};\n}}\n\n'
        body_text += f'-(BOOL)shouldAutorotate\n{{\n\treturn YES;\n}}\n\n'
        body_text += '#endif /* __IPHONE_6_0 */\n\n'

        body_text += '#ifdef __IPHONE_8_0\n'
        body_text += f'-(void)viewWillTransitionToSize:(CGSize)size withTransitionCoordinator:(id<UIViewControllerTransitionCoordinator>)coordinator\n{{\n{self._oc_block(random.randint(1, 5))}\n\t[super viewWillTransitionToSize:size withTransitionCoordinator:coordinator];\n}}\n\n'
        body_text += '#else\n'
        body_text += f'-(void)didRotateFromInterfaceOrientation:(UIInterfaceOrientation)fromInterfaceOrientation\n{{\n\t[super didRotateFromInterfaceOrientation:fromInterfaceOrientation];\n{self._oc_block(random.randint(1, 5))}\n}}\n\n'
        body_text += '#endif /* __IPHONE_8_0 */\n\n'

        body_text += f'-(BOOL)prefersStatusBarHidden\n{{\n\treturn YES;\n}}\n\n'
        body_text += f'-(BOOL)prefersHomeIndicatorAutoHidden\n{{\n\treturn YES;\n}}\n\n'
        body_text += f'-(void)didReceiveMemoryWarning\n{{\n\t[super didReceiveMemoryWarning];\n{self._oc_block(random.randint(1, 5))}\n}}\n\n'
        # 添加的函数
        for i in range(num_funs):
            body_text += self._oc_function(size=random.randint(1, 5))
        # 生成
        fname = self._oc_nc() + 'ViewController'
        hbody = f'@interface {fname} : UIViewController\n@end'
        mbody = f'''#import "{fname}.h"
#import "{self.cpp_helper}.h"
\n
@implementation {fname} 
{{
{memb_text}
}}\n
{body_text}
@end'''
        return fname, hbody, mbody

    def _oc_ui(self, num_funs=8, num_vars=8):
        memb_text, body_text = '', ''
        # 成员变量
        if num_vars > 0:
            for i in range(num_vars):
                t, n = self._oc_type(), f'_{ABC.sel(0.9)}'
                memb_text += f'\t{t} {n};\n'
            memb_text = memb_text[0:-1]
        # 添加的函数
        for i in range(num_funs):
            body_text += self._oc_function(size=random.randint(2, 5))
        # 生成
        fname = self._oc_nc() + 'View'
        hbody = f'@interface {fname} : UIView\n@end'
        mbody = f'''#import "{fname}.h"
#import "{self.cpp_helper}.h"
\n
@implementation {fname} 
{{
{memb_text}
}}\n
{body_text}
@end'''
        return fname, hbody, mbody

    def _oc_md(self, num_funs=8):
        # 添加的函数
        body_text = ''
        for i in range(num_funs):
            body_text += self._oc_function(host='+', size=random.randint(2, 6))
        # 生成
        if random.random() < 0.45:
            fname = self._oc_nc() + self.helper_ext
        else:
            fname = self._oc_nc() + ABC.noun().capitalize()
        hbody = f'@interface {fname} : NSObject\n@end'
        mbody = f'''#import "{fname}.h"
#import "{self.cpp_helper}.h"
\n
@implementation {fname}\n
{body_text}
@end'''
        return fname, hbody, mbody

    def _oc_function(self, host='-', size=4, context=None, ret=None):
        n = self._oc_nf(0 if random.random() < 0.70 else (1 if random.random() < 0.70 else (2 if random.random() < 0.80 else 3)))
        ret = self._oc_return() if ret is None else ret
        if ret == 'void':
            s = host + f'({ret}){n}\n{{\n{self._oc_block(size, context)}\n}}\n\n'
        else:
            s = host + f'({ret}){n}\n{{\n{self._oc_block(size, context)}\n\treturn {self._oc_value(ret)};\n}}\n\n'
        return s

    def _oc_block(self, size=4, context=None):
        array = []
        for i in range(size):
            s = self._oc_statement(context)
            while s in array:
                s = self._oc_statement(context)
            array.append(s)
        return ';\n'.join([('\t' + s) for s in array]) + ';'

    def _oc_statement(self, context=None):
        if random.random() < 0.03:
            if self.use_liebytes < self.max_liebytes:
                return self._oc_lie_data()
        array = (
            f'[[NSBundle mainBundle] pathForResource:@"{ABC.noun()}" ofType:nil]',
            f'[[NSBundle mainBundle] objectForInfoDictionaryKey:@"{ABC.noun()}"]',
        ) + (
            f'[[NSFileManager defaultManager] fileExistsAtPath:@"{ABC.noun()}/{ABC.noun()}.{random.choice(("jpg", "png", "plist"))}"]',
            f'[[NSFileManager defaultManager] contentsAtPath:@"{ABC.noun()}/{ABC.noun()}.{random.choice(("jpg", "png", "plist"))}"]',
            # f'[[NSFileManager defaultManager] displayNameAtPath:@"{ABC.noun()}/{ABC.noun()}.{random.choice(("jpg", "png", "plist"))}"]',
        ) + (
            f'[[NSUserDefaults standardUserDefaults] objectForKey:@"{ABC.sel()}"]',
            f'[[NSUserDefaults standardUserDefaults] arrayForKey:@"{ABC.sel()}"]',
            f'[[NSUserDefaults standardUserDefaults] stringForKey:@"{ABC.sel()}"]',
            # f'[[NSUserDefaults standardUserDefaults] boolForKey:@"{ABC.sel()}"]',
            f'[[NSUserDefaults standardUserDefaults] integerForKey:@"{ABC.sel()}"]',
            # f'[[NSUserDefaults standardUserDefaults] setFloat:{random.randint(0, 100)}.0f forKey:@"{ABC.sel()}"]',
            # f'[[NSUserDefaults standardUserDefaults] setDouble:{random.randint(0, 100)}.0 forKey:@"{ABC.sel()}"]',
            f'[[NSUserDefaults standardUserDefaults] setInteger:{random.randint(0, 100)} forKey:@"{ABC.sel()}"]',
            f'[[NSUserDefaults standardUserDefaults] setObject:@"{ABC.sel()}" forKey:@"{ABC.sel()}"]',
        ) + (
            f'[[NSThread currentThread] valueForKey:@"{ABC.sel()}"]',
            # f'[[NSThread currentThread] valueForUndefinedKey:@"{ABC.sel()}"]',
            # f'[[NSThread currentThread] valueForUndefinedKey:@"{ABC.sel()}"]',
            f'[[NSThread currentThread] setValue:@"{ABC.sel()}" forKey:@"{ABC.sel()}"]',
        ) + (
            f'[[NSNotificationCenter defaultCenter] postNotificationName:@"{ABC.verb()}" object:nil]',
            # f'[[NSNotificationCenter defaultCenter] postNotificationName:@"{ABC.sel()}" object:@"{ABC.sel()}"]',
        ) + (
            '[[UIApplication sharedApplication] keyWindow]',
            '[[UIApplication sharedApplication] windows]',
            # '[[UIApplication sharedApplication] isStatusBarHidden]',
        ) + (
            '[[UIScreen mainScreen] bounds]',
            '[[UIScreen mainScreen] scale]',
            # '[[UIScreen mainScreen] availableModes]',
            # '[[UIScreen mainScreen] currentMode]',
            # '[[UIScreen mainScreen] wantsSoftwareDimming]',
            # '[[UIScreen mainScreen] brightness]',
            # '[[UIScreen mainScreen] coordinateSpace]',
            # '[[UIScreen mainScreen] fixedCoordinateSpace]',
            '[[UIScreen mainScreen] nativeBounds]',
            '[[UIScreen mainScreen] nativeScale]',
            # '[[UIScreen mainScreen] focusedView]',
            # '[[UIScreen mainScreen] supportsFocus]',
        ) + (
            f'{self.cpp_helper}::C()',
            f'{self.cpp_helper}::D()',
            f'{self.cpp_helper}::E()',
            f'{self.cpp_helper}::F()',
            f'{self.cpp_helper}::G()',
        ) + (
            self._oc_lie_text(1),
            self._oc_lie_text(1),
            self._oc_lie_text(2),
            self._oc_lie_text(2),
            self._oc_lie_text(3),
            self._oc_lie_text(3),
            self._oc_lie_text(4),
            self._oc_lie_list(),
            self._oc_lie_dict(),
            self._oc_lie_set(),
        ) + (
            self._oc_lie_alert(),
            self._oc_lie_viewanim(),
            self._oc_lie_animate(),
            self._oc_lie_button(),
            self._oc_lie_label(),
            self._oc_lie_scrollview(),
        )
        return random.choice(array)

    @staticmethod
    def _oc_type():
        return random.choice((
            'BOOL', 'NSInteger', 'NSUInteger', 'CGFloat',
            'NSRange', 'CGPoint', 'CGSize', 'CGRect',
            'NSData*', 'NSString*', 'NSArray*', 'NSMutableArray*', 'NSDictionary*', 'NSMutableDictionary*',
            'UIColor*', 'UIImage*', 'UIView*', 'UIImageView*', 'UILabel*', 'UIButton*'
        ))

    def _oc_value(self, t):
        if t == 'BOOL':
            return 'YES' if random.random() < 0.5 else 'NO'
        if t == 'NSInteger' or t == 'NSUInteger' or t == 'CGFloat':
            return random.randint(0, 128)
        if t == 'NSRange':
            return f'NSMakeRange({random.randint(0, 8)}, {random.randint(0, 1024)})'
        if t == 'CGPoint':
            return 'CGPointZero' if random.random() < 0.8 else f'CGPointMake({random.randint(0, 1125)}, {random.randint(0, 2436)})'
        if t == 'CGSize':
            return 'CGSizeZero' if random.random() < 0.8 else f'CGSizeMake({random.randint(0, 1125)}, {random.randint(0, 2436)})'
        if t == 'CGRect':
            return 'CGRectZero' if random.random() < 0.8 else f'CGRectMake({random.randint(0, 1125)}, {random.randint(0, 2436)}, {random.randint(0, 1125)}, {random.randint(0, 2436)})'
        if t == 'NSData*':
            return 'nil' if random.random() < 0.6 else '[NSData data]'
        if t == 'NSString*':
            return 'nil' if random.random() < 0.6 else f'[NSString stringWithUTF8String:"{ABC.sel()}"]'
        if t == 'NSArray*':
            return 'nil' if random.random() < 0.6 else f'[NSArray array]'
        if t == 'NSMutableArray*':
            return 'nil' if random.random() < 0.6 else f'[NSMutableArray array]'
        if t == 'NSDictionary*':
            return 'nil' if random.random() < 0.6 else f'[NSDictionary dictionary]'
        if t == 'NSMutableDictionary*':
            return 'nil' if random.random() < 0.6 else f'[NSMutableDictionary dictionary]'
        if t == 'UIColor':
            return self._oc_uicolor()
        return 'nil'

    def _oc_return(self):
        r = random.random()
        if r < 0.60:
            return 'void'
        if r < 0.80:
            return random.choice(('NSInteger', 'NSUInteger', 'CGFloat', 'NSRange', 'CGPoint', 'CGSize', 'CGRect'))
        return self._oc_type()

    @staticmethod
    def _oc_uicolor():
        return random.choice((
            'UIColor.blackColor',
            'UIColor.darkGrayColor',
            'UIColor.lightGrayColor',
            'UIColor.whiteColor',
            'UIColor.grayColor',
            'UIColor.redColor',
            'UIColor.greenColor',
            'UIColor.blueColor',
            'UIColor.cyanColor',
            'UIColor.yellowColor',
            'UIColor.magentaColor',
            'UIColor.orangeColor',
            'UIColor.purpleColor',
            'UIColor.brownColor',
            'UIColor.clearColor',
        ))

    @staticmethod
    def _oc_lie_alert():
        return '''UIAlertController *%(var)s = [UIAlertController alertControllerWithTitle:@"%(title)s" message:@"%(msg)s" preferredStyle:UIAlertControllerStyleAlert];
    [%(var)s addTextFieldWithConfigurationHandler:^(UITextField * _Nonnull textField) {
        textField.keyboardType=UIKeyboardTypeDefault;
    }];
    [%(var)s addTextFieldWithConfigurationHandler:^(UITextField * _Nonnull textField) {
        textField.secureTextEntry=YES;
        textField.keyboardType=UIKeyboardTypeNumberPad;
        textField.returnKeyType=UIReturnKeySearch;
    }]''' % {'var': ABC.sel(), 'title': ABC.sel(), 'msg': ABC.sel()}

    @staticmethod
    def _oc_lie_viewanim():
        return '''UIImageView *%(var)s = [UIImageView new];
    [UIView animateWithDuration:1 animations:^{
        %(var)s.alpha = 0;
    } completion:^(BOOL finished) {
        %(var)s.alpha = 1;
    }]''' % {'var': ABC.sel()}

    def _oc_lie_animate(self):
        v = ABC.sel()
        r, g, b, a = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
        return f'''UIActivityIndicatorView *{v} = [[UIActivityIndicatorView alloc]initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleWhiteLarge];
    {v}.backgroundColor = [UIColor colorWithRed:{r} green:{g} blue:{b} alpha:{a}];
    {v}.center = UIApplication.sharedApplication.keyWindow.center;
    {v}.color = {self._oc_uicolor()};
    {v}.layer.cornerRadius = {random.randint(1, 5)};
    {v}.layer.masksToBounds = YES;
    [{v} startAnimating]'''

    def _oc_lie_button(self):
        v = ABC.sel()
        x, y, w, h = random.randint(0, 300), random.randint(0, 300), random.randint(50, 300), random.randint(50, 300)
        return f'''UIButton *{v} = [[UIButton alloc]initWithFrame:CGRectMake({x}, {y}, {w}, {h})];
    {v}.backgroundColor = {self._oc_uicolor()};
    {v}.layer.cornerRadius = 20;
    {v}.layer.masksToBounds = YES;
    {v}.enabled = YES;
    [{v} setTitle:@"{ABC.sel()}" forState:UIControlStateNormal]'''

    def _oc_lie_label(self):
        v = ABC.noun()
        x, y, w, h = random.randint(0, 300), random.randint(0, 300), random.randint(50, 300), random.randint(50, 300)
        return f'''UILabel *{v} = [[UILabel alloc] init];
    {v}.frame = CGRectMake({x}, {y}, {w}, {h});
    {v}.backgroundColor = {self._oc_uicolor()};
    {v}.text = @"{ABC.noun()}";
    {v}.textAlignment = NSTextAlignmentLeft;
    {v}.textColor = {self._oc_uicolor()};
    {v}.shadowColor = {self._oc_uicolor()};
    {v}.shadowOffset = CGSizeMake(-2, 1);
    {v}.numberOfLines = 0;
    {v}.lineBreakMode = NSLineBreakByWordWrapping;
    {random.choice((
            f'{v}.font = [UIFont systemFontOfSize:{random.randint(12, 30)}.f]',
            f'{v}.font = [UIFont boldSystemFontOfSize:{random.randint(12, 30)}.f]',
            f'{v}.font = [UIFont italicSystemFontOfSize:{random.randint(12, 30)}.f]'))}'''

    @staticmethod
    def _oc_lie_scrollview():
        v = ABC.sel()
        x, y, w, h = random.randint(0, 999), random.randint(0, 999), random.randint(300, 999), random.randint(300, 999)
        return f'''UIScrollView *{v} = [[UIScrollView alloc] initWithFrame:CGRectMake({x}, {y}, {w}, {h})];
    {v}.contentSize=CGSizeMake({w-random.randint(0, 9)}, {h-random.randint(0, 9)});
    {v}.contentInset=UIEdgeInsetsMake({random.randint(0, 64)}, 0.0, {random.randint(0, 44)}, 0.0);
    {v}.scrollIndicatorInsets=UIEdgeInsetsMake({random.randint(0, 64)}, 0.0, {random.randint(0, 44)}, 0.0);
    {v}.minimumZoomScale={random.randint(1, 9) / 10};
    {v}.maximumZoomScale={random.randint(1, 5)}'''

    @staticmethod
    def _oc_lie_text(style):
        v = ABC.sel()
        if style == 4:
            sp = ' ' if random.random() < 0.2 else random.choice(('_', '-'))
        s = f'NSMutableString *{v} = [NSMutableString string];\n'
        for i in range(random.randint(2, 9)):
            if style == 1:
                s += f'\t[{v} appendString:@"{ABC.sel()}"];\n'
            elif style == 2:
                s += f'\t[{v} appendFormat:@"%@", @"{ABC.sel()}"];\n'
            elif style == 3:
                if random.random() < 0.5:
                    s += f'\t[{v} appendFormat:@"%@", @"{ABC.sel()}"];\n'
                else:
                    s += f'\t[{v} appendString:@"{ABC.sel()}"];\n'
            elif style == 4:
                sb = '@"'
                for b in range(random.randint(0, 5)):
                    sb += ABC.sel() + sp
                sb += f'{ABC.sel()}"'
                s += f'\t[{v} appendString:{sb}];\n'
        return s[0:-2]

    @staticmethod
    def _oc_lie_set():
        v = ABC.sel()
        s = f'NSMutableSet *{v} = [NSMutableSet set];\n'
        for i in range(random.randint(2, 9)):
            s += f'\t[{v} addObject:@"{ABC.sel()}"];\n'
        return s[0:-2]

    @staticmethod
    def _oc_lie_list():
        v = ABC.sel()
        s = f'NSMutableArray *{v} = [NSMutableArray array];\n'
        for i in range(random.randint(2, 9)):
            s += f'\t[{v} addObject:@"{ABC.sel()}"];\n'
        return s[0:-2]

    @staticmethod
    def _oc_lie_dict():
        v = ABC.sel()
        n = random.randint(0, 9)
        s = f'NSMutableDictionary *{v} = [NSMutableDictionary dictionary];\n'
        for i in range(random.randint(2, 9)):
            s += f'\t[{v} setObject:@({i+n}) forKey:@"{ABC.sel()}"];\n'
        return s[0:-2]

    def _oc_lie_data(self):
        d = self.max_liebytes - self.use_liebytes
        if d > 4:
            n = random.randint(2, int(d * 0.5) if d > 9999 else d)
        else:
            n = d
        self.use_liebytes += n
        s, w = '', False
        for i in range(n):
            if (i + 1) % 20 == 0:
                s += '\n\t'
            d = self.noabc_bits[random.randint(0, self.noabc_imax)] if w else random.randint(0, 255)
            w = (d == 47 or 64 < d < 91 or 96 < d < 123)  # 不能让'/'或字母连接起来组成不可预测的单词
            s += '0x%x,' % d
        a = ABC.sel()
        b = ABC.sel()
        s = f'static const unsigned char {a}[{n}] = {{{s[0:-1]}}};\n'
        s += f'\tNSMutableData *{b} = [NSMutableData data];\n'
        s += f'\t[{b} appendBytes:{a} length:{n}]'
        return s

    def _oc_nf(self, args=0):  # 无参数函数名
        if args == 0:
            p = self._oc_nf_part()
            return f'{p[0]}{p[1].capitalize()}'
        f = ''
        for i in range(args):
            p = self._oc_nf_part()
            f += f' {p[0]}{p[1].capitalize()}:({self._oc_type()}){p[1]}'
        return f

    def _oc_nf_part(self):
        v, n = ABC.verb(), ABC.noun()
        return (v, n) if len(v + n) < 12 else self._oc_nf_part()

    @staticmethod
    def _oc_nc():  # 类名
        # name = ABC.sel().capitalize()
        # return name if len(name) > random.randint(6, 9) else self._oc_nc()
        return ABC.sel().capitalize()

def make_resource(make_dir, source_dir, target_dir):
    if os.path.isdir(make_dir):
        shutil.rmtree(make_dir)
    shutil.copytree(source_dir, make_dir)
    FS.merge_tree(os.path.join(target_dir, 'skin'), make_dir)
    shutil.copy2(os.path.join(target_dir, 'sdk.json'), make_dir)

def main():
    working_dir = '/Users/joli/Desktop/test/asset'
    # 乱斗
    project_dir = '/Users/joli/proj/sdk_uzone/trunk/projects/luandou'
    target_dir = os.path.join(project_dir, 'luandou_xc/app_tendo/package/wlsg')
    source_dir = os.path.join(project_dir, 'resource/sanguo_new_bt_vn')
    # # 战国
    # project_dir = '/Users/joli/proj/sdk_uzone/trunk/projects/zhanguo'
    # target_dir = os.path.join(project_dir, 'zhanguo_xc/app_tendo/package/sgdyx')
    # source_dir = os.path.join(project_dir, 'resource/dudai_vn')

    # # 打包资源
    magic = b'f-fast'
    build_pkg = os.path.join(working_dir, 'data.bytes')
    build_dir = os.path.join(working_dir, 'resource')
    blur_kb = random.randint(1024, 2048) * 1024
    fill_mb = 5
    make_resource(build_dir, source_dir, target_dir)
    ab = AssetBuilder(magic=magic, blend=True)
    ab.pack(build_pkg, build_dir, blurkb=blur_kb, fillmb=fill_mb)
    with AssetPackage(build_pkg, magic=magic) as ap:
        ap.unpack(os.path.join(working_dir, 'unpack'), build_dir, output=True)
    log.i('AssetBuilder blur=%dkb, fill=%fmb' % (blur_kb/1024, fill_mb))
    FS.explorer(working_dir)

    # # 垃圾文件生成器
    # lb = LitterBuilder()
    # lb.build(('patch1.pkg', 'patch2.pkg'), 937, magic)

    # # 垃圾代码生成器
    # codes_dir = os.path.join(working_dir, 'codes')
    # fb = FakerBuilder(liemb=5)
    # fb.build(codes_dir, num_ac=0, num_ui=21, num_vc=17, num_md=3)
    # log.i('FakerBuilder liebytes:%f/%f' % (fb.use_liebytes/1024/1024, fb.max_liebytes/1024/1024))
    # FS.explorer(codes_dir)

    # # 测试
    # with AssetPackage('/Users/joli/proj/sdk_uzone/trunk/projects/zhanguo/zhanguo_xc/app_tendo/package/sgdyx/game/assets/data.pkg', magic=b'tendo.data') as ap:
    #     ap.unpack(os.path.join(curdir, 'unpack'), mixdir, output=True)
