# -*- coding: utf-8 -*-
# @Time    : 2019/6/6 3:03 PM
# @Author  : Joli
# @Email   : 99755349@qq.com

# import os
# import random
# from jonlin.utils import Log, FS, Rand
#
# log = Log.Logger(__file__)

# class AbcMom:
#     def __init__(self):
#         ecdict_res = os.path.join(os.path.dirname(__file__), '../../../extension/ECDICT/res')
#         starnoun = os.path.join(ecdict_res, 'starnoun.txt')
#         if os.path.isfile(starnoun):
#             starnoun = FS.read_text(starnoun)
#             self._nounset = tuple(starnoun.split('\n'))
#         starverb = os.path.join(ecdict_res, 'starverb.txt')
#         if os.path.isfile(starverb):
#             starverb = FS.read_text(starverb)
#             self._verbset = tuple(starverb.split('\n'))
#
#     def gen_abc(self):
#         return self.gen_noun() if random.random() < 0.5 else self.gen_verb()
#
#     def gen_noun(self):  # 随机名词
#         w = random.choice(self._nounset)
#         return self.gen_noun() if (w in _FUCKWORDS) else w
#
#     def gen_verb(self):  # 随机动词
#         w = random.choice(self._verbset)
#         return self.gen_verb() if (w in _FUCKWORDS) else w
#
#     def gen_mult_noun(self, nums):
#         array = []
#         for i in range(nums):
#             w = self.gen_noun()
#             while w in array:
#                 w = self.gen_noun()
#             array.append(w)
#         return array
# ABC_MOM = AbcMom()  # 单词生成器
#
# class NumMom:
#     def __init__(self):
#         self._max = random.randint(10000, 1000000000)
#         self._min = -self._max
#
#     def gen_digit(self, area):
#         return random.randint(max(area[0], self._min), min(area[1], self._max))
#
#     def gen_float(self, area):
#         nmin, nmax = max(area[0], self._min), min(area[1], self._max)
#         return random.random() * (nmax - nmin) + nmin
# NUM_MOM = NumMom()  # 数字生成器

# class OC:
#     class Symbol:
#         def __init__(self, name):
#             self.name = name
#
#     class Variant:
#         def __init__(self, kind):
#             self.kind = kind
#
#     class Boolean(Variant):
#         def __init__(self, kind, yes, no):
#             super().__init__(kind)
#             self.yes = yes
#             self.no = no
#
#     class Number(Variant):
#         def __init__(self, kind, area):
#             super().__init__(kind)
#             self.area = area
#
#     class Struct(Variant):
#         def __init__(self, kind, *attrs):
#             super().__init__(kind)
#             self.attrs = attrs
#
#     class Protocol(Variant):
#         def __init__(self, kind):
#             super().__init__(kind)
#             self.uses = None
#             self.funcs = []
#
#         def dec(self, name, mod, ret, *args):
#             func = OC.Func(name, mod, ret, *args)
#             self.funcs.append(func)
#             return func
#
#         def get_func(self, name):
#             for func in self.funcs:
#                 if func.name == name:
#                     return func
#
#     class Interface(Variant):
#         def __init__(self, kind, base=None, apis=None):
#             super().__init__(kind)
#             self.base = base
#             self.apis = apis
#             self.uses = None
#             self.funcs = []
#             self.attrs = []
#
#         def var(self, name, isa, value=None):
#             attr = OC.Var(name, isa, value)
#             self.attrs.append(attr)
#             return attr
#
#         def dec(self, name, mod, ret, *args):
#             func = OC.Func(name, mod, ret, *args)
#             self.funcs.append(func)
#             return func
#
#         def get_func(self, name):
#             for func in self.funcs:
#                 if func.name == name:
#                     return func
#
#         def get_attr(self, name):
#             for attr in self.attrs:
#                 if attr.name == name:
#                     return attr
#
#     class Var:  # 变量
#         def __init__(self, name, isa, value=None):
#             self.name = name
#             self.isa = isa
#             self.value = value
#
#         def edit(self):
#             return '%s %s' % (self.isa.kind, self.name)
#
#     class Ptr(Var):  # 指针
#         def __init__(self, name, isa, value=None):
#             super().__init__(name, isa, value)
#
#         def edit(self):
#             return '%s *%s' % (self.isa.kind, self.name)
#
#     class Pid(Var):  # ID Pointer
#         def __init__(self, name, isa, value=None):
#             super().__init__(name, isa, value)
#
#         def edit(self):
#             if isinstance(self.isa, OC.Protocol):
#                 return 'id<%s> %s' % (self.isa.kind, self.name)
#             return 'id %s' % self.name
#
#     class Func:
#         def __init__(self, name, mod, ret, *args):
#             self.name = name
#             self.ret = ret
#             self.mod = mod
#             self.args = args
#
#     class Scope:
#         def __init__(self):
#             self.layer = 0
#             self.attrs = []
#
#         def indent(self, offset=0):
#             return '\t' * (self.layer + offset)
#
#         def new_attr(self, isa):
#             name = ABC_MOM.gen_abc()
#             if self.get_attr(name) is not None:
#                 return self.new_attr(isa)
#             var = OC.create_var(name, isa)
#             self.attrs.append(var)
#             return var
#
#         def get_attr(self, name):
#             for attr in self.attrs:
#                 if attr.name == name:
#                     return attr
#
#         def list_isa_attrs(self, isa, nullalbe=True):
#             array = []
#             for attr in self.attrs:
#                 if (attr.isa == isa) and (nullalbe or not OC.is_null(attr.value)):
#                     array.append(attr)
#             return array
#
#         def list_digit_attrs(self):
#             array = []
#             for attr in self.attrs:
#                 if attr.isa in OC.DIGITS:
#                     array.append(attr)
#             return array
#
#         def list_collect_attrs(self):
#             array = []
#             for attr in self.attrs:
#                 if attr.isa in OC.NSCOLLECTS:
#                     array.append(attr)
#             return array
#
#     STATIC = 1  # 静态的
#     MEMBER = 2  # 成员的
#     VAARGS = Symbol('...')  # 任意变长参数
#     VOID = Symbol('void')  # 无
#     NULL = Symbol('nil')  # 空
#     INIT = Symbol('init')  # 初始
#     ID = Symbol('id')  # id
#
#     BOOL = Boolean('BOOL', 'YES', 'NO')
#     # bool = Boolean('bool', 'true', 'false')
#
#     I8 = Number('char', (-128, 127))  # (-2^7, 2^7-1)
#     U8 = Number('unsigned char', (0, 255))  # (0, 2^8)
#     I16 = Number('short', (-32768, 32767))  # (-2^15, 2^15-1)
#     U16 = Number('unsigned short', (0, 65536))  # (0, 2^16)
#     I32 = Number('int', (-2147483648, 2147483647))  # (-2^31, 2^31-1)
#     U32 = Number('unsigned int', (0, 4294967296))  # (0, 2^64)
#     I64 = Number('long long', (-9223372036854775808, 9223372036854775807))  # (-2^63, 2^63-1)
#     U64 = Number('unsigned long long', (0, 18446744073709551616))  # (0, 2^64)
#     F32 = Number('float', (-3.4e38, 3.4e38))  # 4字节
#     F64 = Number('double', (-1.7e308, 1.7e308))  # 8字节
#
#     NSInteger = Number('NSInteger', I32.area)
#     NSUInteger = Number('NSUInteger', U32.area)
#     CGFloat = Number('CGFloat', F32.area)
#
#     NSRange = Struct('NSRange', Var('location', NSUInteger), Var('length', NSUInteger))
#     CGPoint = Struct('CGPoint', Var('x', CGFloat), Var('y', CGFloat))
#     CGSize = Struct('CGSize', Var('width', CGFloat), Var('height', CGFloat))
#     CGRect = Struct('CGRect', Var('x', CGFloat), Var('y', CGFloat), Var('width', CGFloat), Var('height', CGFloat))
#
#     NSObject = Interface('NSObject')
#     NSData = Interface('NSData', NSObject)
#     NSString = Interface('NSString', NSObject)
#     NSArray = Interface('NSArray', NSObject)
#     NSMutableArray = Interface('NSMutableArray', NSArray)
#     NSSet = Interface('NSSet', NSObject)
#     NSMutableSet = Interface('NSMutableSet', NSSet)
#     NSDictionary = Interface('NSDictionary', NSObject)
#     NSMutableDictionary = Interface('NSMutableDictionary', NSDictionary)
#
#     UIColor = Interface('UIColor', NSObject)
#     UIImage = Interface('UIImage', NSObject)
#     UIFont = Interface('UIFont', NSObject)
#
#     UIResponder = Interface('UIResponder', NSObject)
#     UIViewController = Interface('UIViewController', UIResponder)
#     UINavigationController = Interface('UINavigationController', UIViewController)
#     # UITableController = Interface('UITableController', UIViewController)
#
#     UIView = Interface('UIView', NSObject)
#     UIWindow = Interface('UIWindow', UIView)
#     UIAlertView = Interface('UIAlertView', UIView)
#     UIProgressView = Interface('UIProgressView', UIView)
#     UIActivityIndicatorView = Interface('UIActivityIndicatorView', UIView)
#     UIScrollView = Interface('UIScrollView', UIView)
#     # UITableView = Interface('UITableView', UIView)
#     # UIGridView = Interface('UIGridView', UIView)
#
#     UIImageView = Interface('UIImageView', UIView)
#     UILabel = Interface('UILabel', UIView)
#     UIControl = Interface('UIControl', UIView)
#     UIButton = Interface('UIButton', UIControl)
#     UISwitch = Interface('UISwitch', UIControl)
#     UISlider = Interface('UISlider', UIControl)
#     UIStepper = Interface('UIStepper', UIControl)
#     UITextField = Interface('UITextField', UIControl)
#
#     UIAlertViewDelegate = Protocol('UIAlertViewDelegate')
#     UIAlertViewDelegate.dec('alertView:clickedButtonAtIndex:', MEMBER, VOID, Ptr('alertView', UIAlertView), Var('buttonIndex', NSInteger))
#
#     UITextFieldDelegate = Protocol('UITextFieldDelegate')
#     UITextFieldDelegate.dec('textFieldShouldBeginEditing:', MEMBER, BOOL, Ptr('textField', UITextField))
#     UITextFieldDelegate.dec('textFieldDidBeginEditing:', MEMBER, VOID, Ptr('textField', UITextField))
#     UITextFieldDelegate.dec('textFieldShouldEndEditing:', MEMBER, BOOL, Ptr('textField', UITextField))
#     UITextFieldDelegate.dec('textFieldDidEndEditing:', MEMBER, VOID, Ptr('textField', UITextField))
#     UITextFieldDelegate.dec('textFieldShouldClear:', MEMBER, BOOL, Ptr('textField', UITextField))
#     UITextFieldDelegate.dec('textFieldShouldReturn:', MEMBER, BOOL, Ptr('textField', UITextField))
#
#     DIGITS = (I8, U8, I16, U16, I32, U32, I64, I64, NSInteger, NSUInteger)
#     FLOATS = (F32, F64, CGFloat)
#     NSCOLLECTS = (NSSet, NSMutableSet, NSArray, NSMutableArray, NSDictionary, NSMutableDictionary)
#     NSBASICS = (NSString, NSData) + NSCOLLECTS
#
#     @classmethod
#     def is_null(cls, value):
#         return value is None or value == cls.NULL
#
#     @classmethod
#     def topscope(cls, cla, func=None):
#         scope = cls.Scope()
#         scope.layer = 1
#         if cla.attrs:
#             scope.attrs.extend(cla.attrs)
#         if func and func.args:
#             scope.attrs.extend(func.args)
#         return scope
#
#     @classmethod
#     def subscope(cls, parent, offset=0):
#         scope = cls.Scope()
#         scope.layer = parent.layer + offset + 1
#         scope.attrs.extend(parent.attrs)
#         return scope
#
#     @classmethod
#     def create_var(cls, name, isa):
#         if isinstance(isa, cls.Boolean):
#             return cls.Var(name, isa, isa.no)
#         if isinstance(isa, cls.Number):
#             return cls.Var(name, isa, 0)
#         if isinstance(isa, cls.Struct):
#             return cls.Var(name, isa, cls.INIT)
#         if isinstance(isa, cls.Interface):
#             return cls.Ptr(name, isa, cls.NULL)
#         if isa == cls.ID or isinstance(isa, cls.Protocol):
#             return cls.Pid(name, isa, cls.NULL)
#         log.e('unexpected kind on create_var:', isa)
#
#     @classmethod
#     def create_ins(cls, isa):
#         return '[[[%s malloc] init] autorelease]' % isa.kind
#
#     @classmethod
#     def rand_number(cls):
#         r = random.random()
#         if r < 0.4:
#             return cls.NSInteger
#         if r < 0.7:
#             return cls.NSUInteger
#         if r < 0.85:
#             return cls.CGFloat
#         return random.choice(cls.FLOATS) if r < 0.90 else random.choice(cls.DIGITS)
#
#     @classmethod
#     def rand_nsbase(cls):
#         r = random.random()
#         if r < 0.05:
#             return cls.NSData
#         if r < 0.15:
#             return cls.NSArray
#         if r < 0.25:
#             return cls.NSMutableArray
#         if r < 0.30:
#             return cls.NSSet
#         if r < 0.35:
#             return cls.NSMutableSet
#         if r < 0.45:
#             return cls.NSDictionary
#         if r < 0.55:
#             return cls.NSMutableDictionary
#         return cls.NSString
#
#     @classmethod
#     def rand_uivc(cls):
#         return cls.UIViewController if random.random() < 0.90 else cls.UINavigationController
#
#     @classmethod
#     def rand_uiview(cls):
#         r = random.random()
#         if r < 0.05:
#             return cls.UIWindow
#         if r < 0.10:
#             return cls.UIAlertView
#         if r < 0.15:
#             return cls.UIProgressView
#         if r < 0.20:
#             return cls.UIActivityIndicatorView
#         if r < 0.25:
#             return cls.UIScrollView
#         if r < 0.30:
#             return cls.UIImageView
#         return cls.UIView
#
#     @classmethod
#     def rand_widget(cls):
#         r = random.random()
#         if r < 0.30:
#             return cls.UIImageView
#         if r < 0.55:
#             return cls.UILabel
#         if r < 0.80:
#             return cls.UIButton
#         if r < 0.85:
#             return cls.UISwitch
#         if r < 0.90:
#             return cls.UISlider
#         if r < 0.95:
#             return cls.UIStepper
#         return cls.UITextField
#
#     @classmethod
#     def rand_uidata(cls):
#         r = random.random()
#         if r < 0.10:
#             return cls.UIFont
#         if r < 0.40:
#             return cls.UIColor
#         return cls.UIImage
#
#     @classmethod
#     def rand_uiprot(cls):
#         return cls.UIAlertViewDelegate if random.random() < 0.9 else cls.UITextFieldDelegate
#
#     @classmethod
#     def rand_struct(cls):
#         r = random.random()
#         if r < 0.25:
#             return cls.CGPoint
#         if r < 0.50:
#             return cls.CGSize
#         if r < 0.75:
#             return cls.CGRect
#         return cls.NSRange
#
#     @classmethod
#     def rand_value(cls, isa, scope, nullalbe=True):
#         if random.random() < 0.5:
#             attrs = scope.list_isa_attrs(isa, nullalbe)
#             if attrs:
#                 return random.choice(attrs).name
#         if isinstance(isa, cls.Boolean):
#             return isa.yes if random.random() < 0.5 else isa.no
#         if isinstance(isa, cls.Number):
#             return NUM_MOM.gen_float(isa.area) if isa in cls.FLOATS else NUM_MOM.gen_digit(isa.area)
#         if isinstance(isa, cls.Struct):
#             return cls.rand_struct_value(isa, scope)
#         if isinstance(isa, cls.Protocol):
#             attrs = scope.list_isa_attrs(isa, nullalbe=True)
#             return random.choice(attrs).name if attrs else cls.NULL
#         if isinstance(isa, cls.Interface):
#             if isa in cls.NSBASICS:
#                 return cls.rand_nsbase_value(isa, scope, nullalbe)
#             if random.random() < 0.8 or not nullalbe:
#                 return cls.create_ins(isa)
#             return cls.NULL
#
#     @classmethod
#     def rand_struct_value(cls, isa, scope):
#         if isa == cls.NSRange:
#             attrs = scope.list_isa_attrs(cls.NSUInteger)
#             if attrs:
#                 random.shuffle(attrs)
#                 d1 = attrs[0].name
#                 attrs.pop(0)
#             else:
#                 d1 = str(random.randint(0, 50))
#             d2 = attrs[0].name if attrs else str(random.randint(51, 100))
#             return 'NSMakeRange(%s, %s)' % (d1, d2)
#         if isa == cls.CGPoint:
#             if random.random() < 0.5:
#                 return 'CGPointZero'
#             attrs = scope.list_isa_attrs(cls.CGFloat)
#             if attrs:
#                 random.shuffle(attrs)
#                 d1 = attrs[0].name
#                 attrs.pop(0)
#             else:
#                 d1 = str(random.randint(0, 1125))
#             d2 = attrs[0].name if attrs else str(random.randint(0, 2436))
#             return 'CGPointMake(%s, %s)' % (d1, d2)
#         if isa == cls.CGSize:
#             if random.random() < 0.5:
#                 return 'CGSizeZero'
#             attrs = scope.list_isa_attrs(cls.CGFloat)
#             if attrs:
#                 random.shuffle(attrs)
#                 d1 = attrs[0].name
#                 attrs.pop(0)
#             else:
#                 d1 = str(random.randint(0, 1125))
#             d2 = attrs[0].name if attrs else str(random.randint(0, 2436))
#             return 'CGSizeMake(%s, %s)' % (d1, d2)
#         if isa == cls.CGRect:
#             if random.random() < 0.5:
#                 return 'CGRectZero' if random.random() < 0.8 else 'CGRectNull'
#             attrs = scope.list_isa_attrs(cls.CGFloat)
#             if attrs:
#                 random.shuffle(attrs)
#                 d1 = attrs[0].name
#                 attrs.pop(0)
#             else:
#                 d1 = str(random.randint(0, 1125))
#             if attrs:
#                 d2 = attrs[0].name
#                 attrs.pop(0)
#             else:
#                 d2 = str(random.randint(0, 2436))
#             if attrs:
#                 d3 = attrs[0].name
#                 attrs.pop(0)
#             else:
#                 d3 = str(random.randint(0, 1125))
#             d4 = attrs[0].name if attrs else str(random.randint(0, 2436))
#             return 'CGRectMake(%d, %d, %d, %d)' % (d1, d2, d3, d4)
#         log.e('unexpected struct on rand_struct_value:', isa)
#
#     @classmethod
#     def rand_nsbase_value(cls, isa, scope, nullalbe=False):
#         if isa == cls.NSString:
#             return cls.rand_string_value(scope, nullalbe)
#         if isa == cls.NSData:
#             return cls.rand_nsdata_value(scope, nullalbe)
#         if isa == cls.NSSet or isa == cls.NSMutableSet:
#             if random.random() < 0.1 and nullalbe:
#                 return cls.NULL
#             return '[%s setWithObjects:%snil]' % (isa.kind, cls.rand_seq(random.randint(0, 9), scope))
#         if isa == cls.NSArray or isa == cls.NSMutableArray:
#             if random.random() < 0.1 and nullalbe:
#                 return cls.NULL
#             return '[%s arrayWithObjects:%snil]' % (isa.kind, cls.rand_seq(random.randint(0, 9), scope))
#         if isa == cls.NSDictionary or isa == cls.NSMutableDictionary:
#             if random.random() < 0.1 and nullalbe:
#                 return cls.NULL
#             return '[%s dictionaryWithObjectsAndKeys:%snil]' % (isa.kind, cls.rand_kvs(random.randint(0, 9), scope))
#
#     @classmethod
#     def rand_string_value(cls, scope, nullalbe=False):
#         r = random.random()
#         if r < 0.10:
#             return '[NSString stringWithFormat:@"%%@%%d", @"%s", %d]' % (ABC_MOM.gen_abc(), random.randint(0, 9))
#         if r < 0.30:
#             attrs = scope.list_isa_attrs(cls.NSString, nullalbe=False)
#             if attrs:
#                 return '[NSString stringWithString:"%s"]' % random.choice(attrs).name
#         if r < 0.80:
#             return '[NSString stringWithUTF8String:"%s"]' % ABC_MOM.gen_abc()
#         if r < 0.90 or not nullalbe:
#             return '[NSString string]'
#         return cls.NULL
#
#     @classmethod
#     def rand_nsdata_value(cls, scope, nullalbe=False):
#         r = random.random()
#         if r < 0.10:
#             return '[NSData dataWithContentsOfFile:@"%s"]' % ABC_MOM.gen_noun()
#         if r < 0.35:
#             attrs = scope.list_isa_attrs(cls.NSString, nullalbe=False)
#             if attrs:
#                 token = random.choice(attrs).name
#             else:
#                 token = '@"%s"' % ABC_MOM.gen_noun()
#             return '[NSData dataWithBytes:["%s" UTF8String] length:["%s" length]]' % (token, token)
#         if r < 0.90 or not nullalbe:
#             return '[NSData data]'
#         return cls.NULL
#
#     @classmethod
#     def rand_seq(cls, size, scope):
#         s = ''
#         if random.random() < 0.5:
#             style = random.random() < 0.5
#             for i in range(size):
#                 s += '@"%s", ' % (ABC_MOM.gen_noun() if style else ABC_MOM.gen_verb())
#         else:
#             offset = max(0, random.randint(-9999, 9999))
#             digits = scope.list_digit_attrs()
#             if digits:
#                 random.shuffle(digits)
#             for i in range(size):
#                 if digits and random.random() < 0.5:
#                     s += '@(%s), ' % digits[0].name
#                     digits.pop(0)
#                 else:
#                     s += '@(%d), ' % (i + offset)
#         return s
#
#     @classmethod
#     def rand_kvs(cls, size, scope):
#         s = ''
#         style = random.random() < 0.5
#         offset = max(0, random.randint(-9999, 9999))
#         digits = scope.list_digit_attrs()
#         if digits:
#             random.shuffle(digits)
#         if random.random() < 0.5:
#             for i in range(size):
#                 s += '@"%s", ' % (ABC_MOM.gen_noun() if style else ABC_MOM.gen_verb())
#                 if digits and random.random() < 0.5:
#                     s += '@(%s), ' % digits[0].name
#                     digits.pop(0)
#                 else:
#                     s += '@(%d), ' % (i + offset)
#         else:
#             for i in range(size):
#                 if digits and random.random() < 0.5:
#                     s += '@(%s), ' % digits[0].name
#                     digits.pop(0)
#                 else:
#                     s += '@(%d), ' % (i + offset)
#                 s += '@"%s", ' % (ABC_MOM.gen_noun() if style else ABC_MOM.gen_verb())
#         return s
#
# class LieMom:
#     def __init__(self):
#         self._obj_map = {}
#
#     def sprout(self, napis, nclas, zones):
#         self._zones = zones
#         self.myapis = []
#         self.myclas = []
#         self.vclist = []
#         self.uilist = []
#         nvc = min(nclas, random.randint(1, int(nclas * 0.1)))
#         nclas -= nvc
#         nui = min(nclas, random.randint(nvc, nvc * 2))
#         nclas -= nui
#         if random.random() < 0.7:
#             vc_tail, ui_tail = 'ViewController', 'View'
#         else:
#             vc_tail, ui_tail = '', ''
#         for i in range(napis):
#             self.myapis.append(self.gen_api())
#         for i in range(nclas):
#             self.myclas.append(self.gen_cla(napi=max(0, random.randint(-9, 3))))
#         for i in range(nvc):
#             self.vclist.append(self.gen_cla(OC.rand_uivc(), tail=vc_tail))
#         for i in range(nui):
#             self.uilist.append(self.gen_cla(OC.rand_uiview(), tail=ui_tail))
#
#     def gen_api(self):
#         name = self._rand_obj_name(self._rand_api_tail())
#         api = OC.Protocol(name)
#         self._obj_map[name] = api
#         return api
#
#     def gen_cla(self, base=OC.NSObject, napi=0, tail=''):
#         apis = Rand.sampling(self.myapis, napi) if napi > 0 else None
#         name = self._rand_obj_name(tail)
#         cla = OC.Interface(name, base, apis)
#         self._obj_map[name] = cla
#         return cla
#
#     def gen_func(self, cla, mod, ret, nargs):  # 声明一个函数
#         func_name = ABC_MOM.gen_verb()
#         arguments = []
#         if nargs > 0:
#             argnames = ABC_MOM.gen_mult_noun(nargs)
#             act_rate = random.random()  # 命名风格
#             act_verb = ABC_MOM.gen_verb()
#             for i in range(nargs):
#                 arg_name = argnames[i]
#                 if 0 == i:
#                     if random.random() < 0.8:
#                         func_name += arg_name.capitalize()
#                 else:
#                     func_name += ':'
#                     if act_rate < 0.4:
#                         func_name += act_verb + arg_name.capitalize()
#                     elif act_rate < 0.8:
#                         func_name += ABC_MOM.gen_verb() + arg_name.capitalize()
#                     else:
#                         func_name += arg_name
#                 arguments.append(OC.create_var(arg_name, self._rand_arg_kind(cla)))
#         else:
#             if random.random() < 0.6:
#                 func_name += ABC_MOM.gen_noun().capitalize()
#         if cla.get_func(func_name) is None:
#             func = cla.dec(func_name, mod, ret, *arguments)
#         else:
#             func = self.gen_func(cla, mod, ret, nargs)  # 函数重名处理
#         return func
#
#     # def auto_gen_func(self, cla, mod):
#     #     # mod = OC.MEMBER if random.random() < 0.8 else OC.STATIC
#     #     ret = self._rand_ret_kind(cla)
#     #     return self.gen_func(cla, mod, ret, nargs=random.randint(0, 3))
#
#     def gen_var(self, cla, name):
#         return OC.create_var(name, self._rand_var_kind(cla))
#
#     def gen_ret(self, cla, func, scope):
#         s = ''
#         return s
#
#     def gen_block(self, cla, func, scope, size):
#         s = ''
#         for i in range(size):
#             s += self.gen_statement(cla, func, scope) + '\n'
#         return s
#
#     def gen_statement(self, cla, func, scope):
#         r = random.random()
#         if r < 0.03:
#             s = self.gen_switch(cla, func, scope)
#         elif r < 0.06:
#             s = self.gen_for(cla, func, scope)
#         elif r < 0.10:
#             s = self.gen_while(cla, func, scope)
#         elif r < 0.20:
#             s = self.gen_if(cla, func, scope)
#         else:
#             s = self.gen_expr(cla, func, scope)
#         return s if s else self.gen_statement(cla, func, scope)
#
#     def gen_if(self, cla, func, scope):
#         s = ''
#         cond = self._rand_cond(cla, func, scope)
#         if not cond:
#             return s
#         s += scope.indent() + 'if (%s) {\n' % cond
#         if random.random() < 0.85:
#             s += self.gen_block(cla, func, OC.subscope(scope), max(1, random.randint(-3, 3)))
#         else:
#             s += self.gen_ret(cla, func, OC.subscope(scope))
#         s += scope.indent() + '}'
#         for i in range(random.randint(0, 3)):
#             cond = self._rand_cond(cla, func, scope)
#             if not cond:
#                 continue
#             s += ' else if (%s) {\n' % cond
#             if random.random() < 0.90:
#                 s += self.gen_block(cla, func, OC.subscope(scope), max(1, random.randint(-3, 3)))
#             else:
#                 s += self.gen_ret(cla, func, OC.subscope(scope))
#             s += scope.indent() + '}'
#         if random.random() < 0.5:
#             s += ' else {\n'
#             if random.random() < 0.85:
#                 s += self.gen_block(cla, func, OC.subscope(scope), max(1, random.randint(-3, 3)))
#             else:
#                 s += self.gen_ret(cla, func, OC.subscope(scope))
#             s += scope.indent() + '}'
#         return s
#
#     def gen_switch(self, cla, func, scope):
#         s = ''
#         attrs = scope.list_digit_attrs()
#         if attrs:
#             cond = random.choice(attrs).name
#         else:
#             return s
#         s += scope.indent() + 'switch(%s) {\n' % cond
#         case_base = max(0, random.randint(-9999, 9999))
#         for i in range(random.randint(1, 4)):
#             s += scope.indent(1) + 'case %d: {\n' % (i + case_base)
#             s += self.gen_block(cla, func, OC.subscope(scope, 1), max(1, random.randint(-3, 3)))
#             s += scope.indent(2) + 'break;\n'
#             s += scope.indent(1) + '}\n'
#         if random.random() < 0.5:
#             s += scope.indent(1) + 'default: {\n'
#             s += self.gen_block(cla, func, OC.subscope(scope, 1), max(1, random.randint(-3, 3)))
#             s += scope.indent(1) + '}\n'
#         s += scope.indent() + '}'
#         return s
#
#     def gen_while(self, cla, func, scope):
#         s = ''
#         cond = self._rand_cond(cla, func, scope)
#         if not cond:
#             return s
#         s += scope.indent() + 'while(%s) {\n' % cond
#         cond = self._rand_true_cond(cla, func, scope)
#         if cond and random.random() < 0.2:
#             s += scope.indent(1) + 'if (%s) {\n' % cond
#             if random.random() < 0.85:
#                 s += scope.indent(2) + 'break;\n'
#             else:
#                 s += self.gen_ret(cla, func, OC.subscope(scope, 1))
#             s += scope.indent(1) + '}\n'
#             stop = True
#         else:
#             stop = False
#         s += self.gen_block(cla, func, OC.subscope(scope, 1), max(1, random.randint(-3, 3)))
#         if not stop:
#             s += scope.indent(1) + 'if (%s) {\n' % (self._rand_true_cond(cla, func, scope) or OC.BOOL.yes)
#             if random.random() < 0.85:
#                 s += scope.indent(2) + 'break;\n'
#             else:
#                 s += self.gen_ret(cla, func, OC.subscope(scope, 1))
#             s += scope.indent(1) + '}\n'
#         s += scope.indent() + '}'
#         return s
#
#     def gen_for(self, cla, func, scope):
#         s = ''
#         # scope = OC.subscope(scope)
#         attrs = scope.list_collect_attrs()
#         if attrs:
#             exp = self._rand_var_kind()
#         else:
#             attrs = scope.list_digit_attrs()
#             if not attrs:
#                 return s
#
#         s += scope.indent() + 'for(%s) {\n' % c
#
#
#         c = ';;' if random.random() < 0.5 else ';%s;' % self._rand_cond(cla, fun)
#         s += scope.indent() + 'for(%s) {\n' % c
#         if random.random() < 0.3:
#             s += ('\t' * (indent + 1)) + 'if (%s) {\n' % self._rand_true_cond(cla, fun)
#             if random.random() < 0.85:
#                 s += ('\t' * (indent + 2)) + 'break;\n'
#             else:
#                 s += self._edit_rets(cla, fun, indent + 2)
#             s += ('\t' * (indent + 1)) + '}\n'
#             b = True
#         s += self._edit_segs(cla, fun, max(1, random.randint(-2, 2)), indent + 1)
#         if not b:
#             s += ('\t' * (indent + 1)) + 'if (%s) {\n' % self._rand_true_cond(cla, fun)
#             if random.random() < 0.85:
#                 s += ('\t' * (indent + 2)) + 'break;\n'
#             else:
#                 s += self._edit_rets(cla, fun, indent + 2)
#             s += ('\t' * (indent + 1)) + '}\n'
#         s += ('\t' * indent) + '}'
#         return s
#
#     def gen_expr(self, cla, func, scope):
#         s = ''
#         return s
#
#     def _rand_cond(self, cla, func, scope):
#         return ''
#
#     def _rand_true_cond(self, cla, func, scope):
#         return ''
#
#     def _rand_obj_name(self, tail=''):
#         zone = random.choice(self._zones) if self._zones else ''
#         name = zone + ABC_MOM.gen_noun().capitalize() + tail
#         return self._rand_obj_name(tail) if name in self._obj_map else name
#
#     @staticmethod
#     def _rand_api_tail():
#         r = random.random()
#         if r < 0.05:
#             return 'Protocol'
#         if r < 0.30:
#             return'Delegate'
#         return ''
#
#     def _rand_api(self):
#         if random.random() < 0.85 and self.myapis:
#             return random.choice(self.myapis)
#         return OC.rand_uiprot()
#
#     def _rand_ret_kind(self, cla):
#         return OC.VOID if random.random() < 0.7 else self._rand_arg_kind(cla)
#
#     def _rand_arg_kind(self, cla):
#         r = random.random()
#         if r < 0.10 and cla.uses:
#             return random.choice(cla.uses)
#         if r < 0.20:
#             return OC.BOOL
#         if r < 0.50:
#             return OC.rand_number()
#         if r < 0.80:
#             return OC.rand_nsbase()
#         if r < 0.85:
#             return OC.rand_struct()
#         if r < 0.90:
#             return OC.rand_uidata()
#         if r < 0.93:
#             return OC.rand_widget()
#         if r < 0.94:
#             return OC.rand_uiview()
#         if r < 0.95:
#             return OC.rand_uivc()
#         return self._rand_api()
#
#     def _rand_var_kind(self, cla):
#         r = random.random()
#         if r < 0.10 and cla.uses:
#             return random.choice(cla.uses)
#         if r < 0.15:
#             return OC.BOOL
#         if r < 0.35:
#             return OC.rand_number()
#         if r < 0.55:
#             return OC.rand_nsbase()
#         if r < 0.60:
#             return OC.rand_struct()
#         if r < 0.65:
#             return OC.rand_uidata()
#         if r < 0.85:
#             return OC.rand_widget()
#         if r < 0.90:
#             return OC.rand_uiview()
#         if r < 0.95:
#             return OC.rand_uivc()
#         return self._rand_api()

# class Fake:
#     VA_ARGS = 'VA_ARGS'  # 变长参数
#     Compact = 'Compact'  # 非指针类型
#     FSTATIC = 0
#     FMEMBER = 1
#
#     class IFace:  # 接口
#         def __init__(self, name, funs=None):
#             self.name = name
#             self.funs = funs
#             self.uses = None
#
#     class Class:  # 类祖
#         def __init__(self, name, base=None):
#             self.name = name
#             self.base = base
#             self.apis = None
#             self.uses = None
#             self.hdef = None
#             self.cimp = None
#
#     class Digit(Class):  # 数字类型
#         def __init__(self, name, base, area):
#             super().__init__(name, base)
#             self.area = area
#
#     class Basic(Class):  # 复杂类型
#         def __init__(self, name, base):
#             super().__init__(name, base)
#
#     class BFace(Class):  # 系统定义类型
#         def __init__(self, name, base):
#             super().__init__(name, base)
#
#     class CFace(Class):  # 自定义类型
#         def __init__(self, name, base=None):
#             super().__init__(name, base)
#             self.vars = None
#             self.funs = None
#             self.uses = None
#
#     class Fun:  # 函数
#         def __init__(self, name, *args, rets=None):
#             self.name = name
#             self.args = args
#             self.rets = rets
#             self.mine = Fake.FMEMBER
#             self.vars = None
#             self.refs = None
#             self.cmds = None  # 自定义指令
#
#     class Var:  # 变量
#         def __init__(self, name, isa, val=None):
#             self.name = name
#             self.isa = isa
#             self.val = val
#
#     @classmethod
#     def create_func(cls, name, args, rets, mine):
#         func = cls.Fun(name)
#         func.args = args
#         func.rets = rets
#         func.mine = mine
#         return func
#
#     @classmethod
#     def is_compact(cls, obj):
#         if isinstance(obj, cls.IFace):
#             return False
#         return obj.base == cls.Compact
#
#     @staticmethod
#     def find_predef(obj):  # 查找前置声明
#         array = []
#         for fun in obj.funs:
#             if fun.rets in obj.uses:
#                 array.append(fun.rets)
#             if fun.args:
#                 for a in fun.args:
#                     if a.isa in obj.uses:
#                         array.append(a.isa)
#         return array
#
#     @classmethod
#     def find_static_fun(cls, obj):
#         array = []
#         for fun in obj.funs:
#             if fun.mine == Fake.FSTATIC:
#                 array.append(fun)
#         return array
#
#     @classmethod
#     def find_member_fun(cls, obj):
#         array = []
#         for fun in obj.funs:
#             if fun.mine == Fake.FMEMBER:
#                 array.append(fun)
#         return array
#
#     @classmethod
#     def isin_fun_refers(cls, src_fun, dst_fun):
#         if src_fun == dst_fun:
#             return True
#         if not src_fun.refs:
#             return False
#         for fun in src_fun.refs:
#             if cls.isin_fun_refers(fun, dst_fun):
#                 return True
#         return False
#
# class EnvContext:
#     def __init__(self):
#         self._ed = EDict()
#         self._es = []
#
#     def reg_env(self, env):
#         self._es.append(env)
#
#     def get_env(self, name):
#         for env in self._es:
#             if env.name == name:
#                 return env
#
#     def get_obj(self, name):
#         for env in self._es:
#             if name in env.objmap:
#                 return env.objmap[name]
#
#     def get_isa(self, isa):
#         if isinstance(isa, str):
#             if isa.endswith('*'):
#                 isa = isa[0:-1]
#             return self.get_obj(isa)
#         return isa
#
#     def get_isa_vars(self, varlist, *isa):
#         if varlist:
#             zones = [self.get_isa(v) for v in isa]
#             return [v for v in varlist if self.get_isa(v.isa) in zones]
#
#     def get_int_vars(self, varlist):
#         return self.get_isa_vars(
#             varlist,
#             'short',
#             'unsigned short',
#             'int',
#             'unsigned int',
#             'long long',
#             'unsigned long long',
#             'NSInteger',
#             'NSUInteger'
#         )
#
#     def get_scope_vars(self, cla, fun):
#         array = []
#         if fun.vars:
#             array.extend(fun.vars)
#         if fun.args:
#             array.extend(fun.args)
#         if (fun.mine == Fake.FMEMBER) and cla.vars:
#             array.extend(cla.vars)
#         for var in array:
#             var.isa = self.get_isa(var.isa)
#         return array
#
#     def rand_noun(self):
#         return self._ed.get_noun()
#
#     def rand_verb(self):
#         return self._ed.get_verb()
#
#     def rand_varname(self, scope):
#         n = self.rand_noun()
#         return self.rand_varname(scope) if n in scope else n
#
#     def rand_objname(self, zone, tail=''):
#         name = zone + self.rand_noun().capitalize() + tail
#         return name if self.get_obj(name) is None else self.rand_objname(zone, tail)
#
# class EnvBase:
#     def __init__(self, name, context):
#         self.ctx = context
#         self.name = name
#         self.objmap = {}
#         context.reg_env(self)
#
#     def regist_objs(self, array):
#         for obj in array:
#             self.objmap[obj.name] = obj
#
# class CxEnv(EnvBase):  # C++ 环境
#     def __init__(self, context):
#         super().__init__('cx', context)
#
#     def setup(self, zone, numiface, numclass):
#         pass
#
# class OCEnv(EnvBase):  # Objective-C 环境
#     def __init__(self, context):
#         super().__init__('oc', context)
#         if random.random() < 0.5:
#             self._tail_vc = ''
#             self._tail_ui = ''
#         else:
#             self._tail_vc = 'ViewController'
#             self._tail_ui = 'View'
#
#     def setup(self, zone, numiface, numclass):
#         self._declare_digits()
#         self._declare_basics()
#         self._declare_uikits()
#         self._declare_myifas(zone, numiface)
#         self._declare_myclas(zone, numclass)
#
#     def _declare_digits(self):
#         self.ints = (
#             # Fake.Digit('char', Fake.Compact, (-128, 127)),  # (-2^7, 2^7-1)
#             # Fake.Digit('unsigned char', Fake.Compact, (0, 255)),  # (0, 2^8)
#             Fake.Digit('short', Fake.Compact, (-32768, 32767)),  # (-2^15, 2^15-1)
#             Fake.Digit('unsigned short', Fake.Compact, (0, 65536)),  # (0, 2^16)
#             # Fake.Digit('long long', Fake.Compact, (-9223372036854775808, 9223372036854775807)),  # (-2^63, 2^63-1)
#             # Fake.Digit('unsigned long long', Fake.Compact, (0, 18446744073709551616)),  # (0, 2^64)
#             Fake.Digit('long long', Fake.Compact, (-2147483648, 2147483647)),  # (-2^63, 2^63-1)
#             Fake.Digit('unsigned long long', Fake.Compact, (0, 4294967296)),  # (0, 2^64)
#             Fake.Digit('NSInteger', Fake.Compact, (-2147483648, 2147483647)),  # (-2^31, 2^31-1)
#             Fake.Digit('NSUInteger', Fake.Compact, (0, 4294967296)),  # (0, 2^32)
#         )
#         self.digits = self.ints + (
#             Fake.Digit('float', Fake.Compact, (-3.4e38, 3.4e38)),  # 4字节
#             Fake.Digit('double', Fake.Compact, (-1.7e308, 1.7e308)),  # 8字节
#             Fake.Digit('CGFloat', Fake.Compact, (-3.4e38, 3.4e38)),  # 4字节
#         )
#         self.regist_objs(self.digits)
#
#     def _declare_basics(self):
#         self.basics = (
#             Fake.Basic('NSString', 'NSObject'),
#             Fake.Basic('NSData', 'NSObject'),
#             Fake.Basic('NSArray', 'NSObject'),
#             Fake.Basic('NSMutableArray', 'NSObject'),
#             Fake.Basic('NSSet', 'NSObject'),
#             Fake.Basic('NSMutableSet', 'NSObject'),
#             Fake.Basic('NSDictionary', 'NSObject'),
#             Fake.Basic('NSMutableDictionary', 'NSObject'),
#             Fake.Basic('NSRange', Fake.Compact),
#             Fake.Basic('CGPoint', Fake.Compact),
#             Fake.Basic('CGSize', Fake.Compact),
#             Fake.Basic('CGRect', Fake.Compact),
#             Fake.Basic('BOOL', Fake.Compact)
#         )
#         self.regist_objs(self.basics)
#
#     def _declare_uikits(self):
#         self.uifaces = (
#             Fake.IFace('UIAlertViewDelegate', (
#                 Fake.Fun('alertView:clickedButtonAtIndex:', Fake.Var('alertView', 'UIAlertView*'), Fake.Var('buttonIndex', 'NSInteger')),
#             )),
#             Fake.IFace('UITextFieldDelegate', (
#                 Fake.Fun('heightForRowAtIndexPath:', Fake.Var('textField', 'UITextField*'), rets='BOOL'),
#                 Fake.Fun('textFieldShouldBeginEditing:', Fake.Var('textField', 'UITextField*')),
#                 Fake.Fun('textFieldDidBeginEditing:', Fake.Var('textField', 'UITextField*')),
#                 Fake.Fun('textFieldShouldEndEditing:', Fake.Var('textField', 'UITextField*'), rets='BOOL'),
#                 Fake.Fun('textFieldDidEndEditing:', Fake.Var('textField', 'UITextField*')),
#                 Fake.Fun('textFieldShouldClear:', Fake.Var('textField', 'UITextField*'), rets='BOOL'),
#                 Fake.Fun('textFieldShouldReturn:', Fake.Var('textField', 'UITextField*'), rets='BOOL'),
#                 Fake.Fun('textField:shouldChangeCharactersInRange:replacementString:', Fake.Var('textField', 'UITextField*'), Fake.Var('range', 'NSRange'), Fake.Var('string', 'NSString*'), rets='BOOL')
#             ))
#             # Fake.IFace('UITableViewDataSource', (
#             #     Fake.Fun('tableView:numberOfRowsInSection:', Fake.Var('tableView', 'UITableView*'), Fake.Var('section', 'NSInteger')),
#             #     Fake.Fun('tableView:cellForRowAtIndexPath:', Fake.Var('tableView', 'UITableView*'), Fake.Var('indexPath', 'NSIndexPath*'))
#             # )),
#             # Fake.IFace('UITableViewDelegate', (
#             #     Fake.Fun('tableView:heightForRowAtIndexPath:', Fake.Var('tableView', 'UITableView*'), Fake.Var('indexPath', 'NSIndexPath*'), rets='CGFloat'),
#             #     Fake.Fun('tableView:heightForHeaderInSection:', Fake.Var('tableView', 'UITableView*'), Fake.Var('section', 'NSInteger'), rets='CGFloat'),
#             #     Fake.Fun('tableView:heightForFooterInSection:', Fake.Var('tableView', 'UITableView*'), Fake.Var('section', 'NSInteger'), rets='CGFloat'),
#             #     Fake.Fun('tableView:didSelectRowAtIndexPath:', Fake.Var('tableView', 'UITableView*'), Fake.Var('indexPath', 'NSIndexPath*'))
#             # ))
#         )
#         self.regist_objs(self.uifaces)
#         # UIViewController
#         self.uictrls = (
#             Fake.BFace('UIViewController', 'UIResponder'),
#             # Fake.BFace('UITableController', 'UIViewController'),
#             Fake.BFace('UINavigationController', 'UIViewController')
#         )
#         self.regist_objs(self.uictrls)
#         # UIView
#         self.uiviews = (
#             Fake.BFace('UIWindow', 'UIView'),
#             Fake.BFace('UIAlertView', 'UIView'),
#             Fake.BFace('UIProgressView', 'UIView'),
#             Fake.BFace('UIActivityIndicatorView', 'UIView')
#         )
#         self.regist_objs(self.uiviews)
#         # widgets
#         self.uiwidgs = (
#             Fake.BFace('UIColor', 'NSObject'),
#             Fake.BFace('UIImage', 'NSObject'),
#             Fake.BFace('UIFont', 'NSObject'),
#             Fake.BFace('UILabel', 'UIView'),
#             Fake.BFace('UIImageView', 'UIView'),
#             Fake.BFace('UIScrollView', 'UIView'),
#             # Fake.BFace('UITableView', 'UIView'),
#             # Fake.BFace('UIGridView', 'UIView'),
#             Fake.BFace('UIButton', 'UIControl'),
#             Fake.BFace('UISwitch', 'UIControl'),
#             Fake.BFace('UISlider', 'UIControl'),
#             Fake.BFace('UIStepper', 'UIControl'),
#             Fake.BFace('UITextField', 'UIControl')
#         )
#         self.regist_objs(self.uiwidgs)
#
#     def _declare_myifas(self, zone, nums):
#         array = []
#         for i in range(nums):
#             ifa = Fake.IFace(self.ctx.rand_objname(zone, random.choice(('', 'Delegate'))))
#             array.append(ifa)
#             self.objmap[ifa.name] = ifa
#         self.myfaces = tuple(array)
#
#     def _declare_myclas(self, zone, nums):
#         num_viewobj = int(nums * (random.randint(10, 15) / 100))
#         num_ctrlobj = int(nums * (random.randint(15, 25) / 100))
#         num_implobj = nums - num_viewobj - num_ctrlobj
#         # UIView
#         array = []
#         for i in range(num_viewobj):
#             cla = Fake.CFace(self.ctx.rand_objname(zone, self._tail_ui), self._rand_choice_view())
#             self.objmap[cla.name] = cla
#             array.append(cla)
#         self.myviews = tuple(array)
#         # UIViewController
#         array = []
#         for i in range(num_ctrlobj):
#             cla = Fake.CFace(self.ctx.rand_objname(zone, self._tail_vc), self._rand_choice_ctrl())
#             self.objmap[cla.name] = cla
#             array.append(cla)
#         self.myctrls = tuple(array)
#         # Implementations
#         array = []
#         for i in range(num_implobj):
#             cla = Fake.CFace(self.ctx.rand_objname(zone))
#             self.objmap[cla.name] = cla
#             array.append(cla)
#         self.myimpls = tuple(array)
#
#     def declare_func(self, cla, nargs, scope):  # 随机声明一个函数
#         name = self.ctx.gen_verb()
#         if nargs > 0:
#             args, arg_scope = [], set()
#             verb = self.ctx.gen_verb()
#             want = random.random()
#             for i in range(nargs):
#                 n = self.ctx.rand_varname(arg_scope)
#                 arg_scope.add(n)  # 记录参数名称
#                 if 0 == i:
#                     if random.random() < 0.5:
#                         name += n.capitalize()
#                 else:
#                     if want < 0.5:  # 保持命名风格
#                         name += ':' + verb + n.capitalize()
#                     elif want < 0.8:
#                         name += ':' + self.ctx.gen_verb() + n.capitalize()
#                     else:
#                         name += ':' + n
#                 args.append(Fake.Var(n, self._rand_choice_isa(cla)))
#         else:
#             args = None
#             if random.random() < 0.5:
#                 name += self.ctx.gen_noun().capitalize()
#         if name in scope:  # 防止重名
#             return self.declare_func(cla, nargs, scope)
#         scope.add(name)
#         args = None if args is None else tuple(args)
#         rets = None if random.random() < 0.6 else self._rand_choice_isa(cla)
#         mine = Fake.FMEMBER if random.random() < 0.8 else Fake.FSTATIC
#         return Fake.create_func(name, args, rets, mine)
#
#     def declare_vars(self, cla, nvars, scope):
#         array = []
#         for i in range(nvars):
#             name = self.ctx.rand_varname(scope)
#             scope.add(name)
#             array.append(Fake.Var(name, self._rand_choice_isa(cla)))
#         cla.vars = array
#
#     @staticmethod
#     def _rand_choice_view():
#         r = random.random()
#         if r < 0.85:
#             return 'UIView'
#         if r < 0.90:
#             return 'UIAlertView'
#         if r < 0.95:
#             return 'UIActivityIndicatorView'
#         return 'UIWindow'
#
#     @staticmethod
#     def _rand_choice_ctrl():
#         r = random.random()
#         if r < 0.90:
#             return 'UIViewController'
#         # if r < 0.95:
#         #     return 'UITableController'
#         return 'UINavigationController'
#
#     def _rand_choice_isa(self, cla):
#         r = random.random()
#         if r < 0.40:
#             return random.choice(self.digits)
#         if r < 0.80:
#             return random.choice(self.basics)
#         if r < 0.85 and cla.uses:
#             return random.choice(cla.uses)
#         if r < 0.93:
#             return random.choice(self.uiwidgs)
#         if r < 0.96:
#             return random.choice(self.uiviews)
#         if r < 0.97:
#             return random.choice(self.uictrls)
#         return self.ctx.get_isa('NSString')
#         # return random.choice(self.uifaces)
#
#     def edit_iface(self, ifa):
#         h = ''
#         if ifa.uses:
#             for uc in Fake.find_predef(ifa):
#                 h += '@class %s;\n' % uc.name
#             h += '\n'
#         h += '@protocol %s <NSObject>\n\n' % ifa.name
#         if ifa.funs:
#             for fun in ifa.funs:
#                 h += self._edit_fun_h(fun) + '\n'
#         h += '@end'
#         return h
#
#     def edit_class(self, cla):
#         h, m = '', ''
#         # header
#         if cla.hdef:
#             for c, s in cla.hdef.items():
#                 h += '#define %s %s\n' % (c, s)
#             h += '\n'
#         if cla.apis:
#             for c in cla.apis:
#                 if c in self.uifaces:
#                     pass
#                 else:
#                     h += '#import "%s.h"\n' % c.name
#         if cla.uses:
#             for c in Fake.find_predef(cla):
#                 h += '@class %s;\n' % c.name
#             h += '\n'
#         h += '@interface %s : %s' % (cla.name, 'NSObject' if cla.base is None else cla.base)
#         if cla.apis:
#             s = ''
#             for c in cla.apis:
#                 s += c.name + ','
#             h += '<' + s[0:-1] + '>'
#         h += '\n\n'
#         for fun in cla.funs:
#             h += self._edit_fun_h(fun) + '\n'
#         h += '@end'
#         # implementation
#         if cla.funs:
#             for fun in cla.funs:
#                 m += self._edit_fun_m(cla, fun) + '\n'
#         if cla.apis:
#             for c in cla.apis:
#                 m += '#pragma-mark %s\n\n' % c.name
#                 for fun in c.funs:
#                     m += self._edit_fun_m(cla, fun) + '\n'
#         s = m
#         m = ''
#         m += '#import "%s.h"\n' % cla.name
#         if cla.uses:
#             for c in cla.uses:
#                 m += '#import "%s.h"\n' % c.name
#         if cla.cimp:
#             for c in cla.cimp:
#                 m += '#import "%s.h"\n' % c.name
#         m += '\n'
#         m += '@implementation %s' % cla.name
#         if cla.vars:
#             m += ' {\n'
#             for var in cla.vars:
#                 m += '\t' + self._edit_var(var) + ';\n'
#             m += '}'
#         m += '\n\n' + s + '@end'
#         return h, m
#
#     def _edit_fun_h(self, fun):
#         s = ('+', '-')[fun.mine]
#         s += '(' + self._edit_isa(fun.rets) + ')'
#         msgs = fun.name.split(':')
#         for i in range(len(msgs)):
#             if not msgs[i]:
#                 continue
#             s += ' ' + msgs[i]
#             if fun.args:
#                 a = fun.args[i]
#                 s += ':(' + self._edit_isa(a.isa) + ')' + a.name
#         s += ';\n'
#         return s
#
#     def _edit_fun_m(self, cla, fun):
#         s = ('+', '-')[fun.mine]
#         s += '(%s)' % self._edit_isa(fun.rets)
#         msgs = fun.name.split(':')
#         for i in range(len(msgs)):
#             if not msgs[i]:
#                 continue
#             s += ' ' + msgs[i]
#             if fun.args:
#                 a = fun.args[i]
#                 s += ':(%s)%s' % (self._edit_isa(a.isa), a.name)
#         fun.vars = []
#         for i in range(max(0, random.randint(-6, 3))):
#             fun.vars.append(self._rand_local_var(cla, fun))
#         s += '{\n'
#         for v in fun.vars:
#             a = cla.vars if fun.mine == Fake.FMEMBER else None
#             s += '\t' + self._edit_var(v) + ' = ' + self._edit_var_value(v, a) + ';\n'
#         if fun.cmds:
#             s += self._edit_segs(cla, fun, random.randint(1, 2))
#             s += '\t' + fun.cmds + ';\n'
#             s += self._edit_segs(cla, fun, random.randint(1, 2))
#         else:
#             s += self._edit_segs(cla, fun, random.randint(1, 5))
#         if fun.rets is not None:
#             s += self._edit_rets(cla, fun, 1)
#         s += '}\n'
#         return s
#
#     def _edit_segs(self, cla, fun, size, indent=1):
#         s = ''
#         for i in range(size):
#             r = random.random()
#             if r < 0.10:
#                 s += self._edit_if(cla, fun, indent)
#             elif r < 0.15:
#                 s += self._edit_switch(cla, fun, indent)
#             elif r < 0.20:
#                 s += self._edit_while(cla, fun, indent)
#             elif r < 0.25:
#                 s += self._edit_for(cla, fun, indent)
#             else:
#                 s += self._edit_stat(cla, fun, indent)
#             s += '\n'
#         return s
#
#     def _edit_if(self, cla, fun, indent):
#         s = ''
#         s += ('\t' * indent) + 'if (%s) {\n' % self._rand_cond(cla, fun)
#         if random.random() < 0.85:
#             s += self._edit_segs(cla, fun, max(1, random.randint(-2, 2)), indent + 1)
#         else:
#             s += self._edit_rets(cla, fun, indent + 1)
#         s += ('\t' * indent) + '} '
#         for i in range(random.randint(0, 2)):
#             s += 'else if (%s) {\n' % self._rand_cond(cla, fun)
#             if random.random() < 0.90:
#                 s += self._edit_segs(cla, fun, max(1, random.randint(-2, 2)), indent + 1)
#             else:
#                 s += self._edit_rets(cla, fun, indent + 1)
#             s += ('\t' * indent) + '} '
#         if random.random() < 0.5:
#             s += 'else {\n'
#             if random.random() < 0.85:
#                 s += self._edit_segs(cla, fun, max(1, random.randint(-2, 2)), indent + 1)
#             else:
#                 s += self._edit_rets(cla, fun, indent + 1)
#             s += ('\t' * indent) + '}'
#         return s
#
#     def _edit_switch(self, cla, fun, indent):
#         s = ''
#         myvars = self.ctx.get_scope_vars(cla, fun)
#         objs = self.ctx.get_int_vars(myvars)
#         if objs:
#             var = random.choice(objs)
#         else:
#             var = self._rand_local_var(cla, fun, random.choice(self.ints))
#             if random.random() < 0.8 and fun.mine == Fake.FMEMBER:
#                 o = var.name + ' = ' + self._edit_var_value(var, myvars)
#                 cla.vars.append(var)
#             else:
#                 o = self._edit_var(var) + ' = ' + self._edit_var_value(var, myvars)
#                 if 1 == indent:
#                     fun.vars.append(var)
#             s += ('\t' * indent) + o + ';\n'
#         s += ('\t' * indent) + 'switch(%s) {\n' % var.name
#         o = random.randint(0, 3)
#         for i in range(random.randint(1, 4)):
#             s += ('\t' * (indent + 1)) + 'case %d: {\n' % (i + o)
#             s += self._edit_segs(cla, fun, max(1, random.randint(-2, 2)), indent + 2)
#             s += ('\t' * (indent + 2)) + 'break;\n'
#             s += ('\t' * (indent + 1)) + '}\n'
#         if random.random() < 0.5:
#             s += ('\t' * (indent + 1)) + 'default: {\n'
#             s += self._edit_segs(cla, fun, max(1, random.randint(-2, 2)), indent + 2)
#             s += ('\t' * (indent + 1)) + '}\n'
#         s += ('\t' * indent) + '}'
#         return s
#
#     def _edit_while(self, cla, fun, indent):
#         s, b = '', False
#         s += ('\t' * indent) + 'while(%s) {\n' % self._rand_cond(cla, fun)
#         if random.random() < 0.3:
#             s += ('\t' * (indent + 1)) + 'if (%s) {\n' % self._rand_true_cond(cla, fun)
#             if random.random() < 0.85:
#                 s += ('\t' * (indent + 2)) + 'break;\n'
#             else:
#                 s += self._edit_rets(cla, fun, indent + 2)
#             s += ('\t' * (indent + 1)) + '}\n'
#             b = True
#         s += self._edit_segs(cla, fun, max(1, random.randint(-2, 2)), indent + 1)
#         if not b:
#             s += ('\t' * (indent + 1)) + 'if (%s) {\n' % self._rand_true_cond(cla, fun)
#             if random.random() < 0.85:
#                 s += ('\t' * (indent + 2)) + 'break;\n'
#             else:
#                 s += self._edit_rets(cla, fun, indent + 2)
#             s += ('\t' * (indent + 1)) + '}\n'
#         s += ('\t' * indent) + '}'
#         return s
#
#     def _edit_for(self, cla, fun, indent):
#         s, b = '', False
#         c = ';;' if random.random() < 0.5 else ';%s;' % self._rand_cond(cla, fun)
#         s += ('\t' * indent) + 'for(%s) {\n' % c
#         if random.random() < 0.3:
#             s += ('\t' * (indent + 1)) + 'if (%s) {\n' % self._rand_true_cond(cla, fun)
#             if random.random() < 0.85:
#                 s += ('\t' * (indent + 2)) + 'break;\n'
#             else:
#                 s += self._edit_rets(cla, fun, indent + 2)
#             s += ('\t' * (indent + 1)) + '}\n'
#             b = True
#         s += self._edit_segs(cla, fun, max(1, random.randint(-2, 2)), indent + 1)
#         if not b:
#             s += ('\t' * (indent + 1)) + 'if (%s) {\n' % self._rand_true_cond(cla, fun)
#             if random.random() < 0.85:
#                 s += ('\t' * (indent + 2)) + 'break;\n'
#             else:
#                 s += self._edit_rets(cla, fun, indent + 2)
#             s += ('\t' * (indent + 1)) + '}\n'
#         s += ('\t' * indent) + '}'
#         return s
#
#     def _edit_rets(self, cla, fun, indent):
#         s = ''
#         if fun.rets is None:
#             s += 'return'
#         else:
#             myvars = self.ctx.get_scope_vars(cla, fun)
#             s += 'return ' + self._edit_isa_value(fun.rets, myvars)
#         return ('\t' * indent) + s + ';\n'
#
#     def _edit_stat(self, cla, fun, indent):
#         myvars = self.ctx.get_scope_vars(cla, fun)
#         # 函数调用语句
#         if random.random() < 0.8:
#             s = self._edit_fun_apply(cla, fun, myvars)
#             if s is not None:
#                 return ('\t' * indent) + s + ';'
#         # 赋值语句
#         s = self._edit_assignment(cla, fun, myvars)
#         if s is not None:
#             return ('\t' * indent) + s + ';'
#         # 变量定义语句
#         v = self._rand_local_var(cla, fun)
#         if random.random() < 0.8 and fun.mine == Fake.FMEMBER:
#             s = v.name + ' = ' + self._edit_var_value(v, myvars)
#             cla.vars.append(v)
#         else:
#             s = self._edit_var(v) + ' = ' + self._edit_var_value(v, myvars)
#             if indent == 1:
#                 fun.vars.append(v)  # 函数的局部变量
#         return ('\t' * indent) + s + ';'
#
#     def _edit_fun_apply(self, cla, fun, myvars):
#         if random.random() < 0.5 and cla.uses:
#             clazz = random.choice(cla.uses)
#             sfuns = Fake.find_static_fun(clazz)
#             afunc = random.choice(sfuns) if sfuns else None
#             if not afunc or random.random() < 0.2:
#                 afunc = random.choice(clazz.funs)
#             return self._call_class_fun(clazz, afunc, myvars)
#         if fun.mine == Fake.FMEMBER:
#             sfuns = Fake.find_member_fun(cla)
#             for i in range(len(sfuns)-1, -1, -1):
#                 if Fake.isin_fun_refers(sfuns[i], fun):
#                     sfuns.pop(i)
#             if sfuns:
#                 afunc = random.choice(sfuns)
#                 if not fun.refs:
#                     fun.refs = [afunc]
#                 else:
#                     fun.refs.append(afunc)
#                 return self._call_fun(cla, afunc, 'self', myvars)
#         if fun.mine == Fake.FSTATIC:
#             sfuns = Fake.find_static_fun(cla)
#             for i in range(len(sfuns)-1, -1, -1):
#                 if Fake.isin_fun_refers(sfuns[i], fun):
#                     sfuns.pop(i)
#             if sfuns:
#                 afunc = random.choice(sfuns)
#                 if not fun.refs:
#                     fun.refs = [afunc]
#                 else:
#                     fun.refs.append(afunc)
#                 return self._call_fun(cla, afunc, cla.name, myvars)
#
#     def _edit_assignment(self, cla, fun, myvars):
#         r = random.random()
#         if fun.args and r < 0.30:  # 函数参数赋值语句
#             v = random.choice(fun.args)
#             myvars.remove(v)  # 不能自己等于自己
#             return v.name + ' = ' + self._edit_var_value(v, myvars)
#         if fun.vars and r < 0.60:  # 局部变量赋值语句
#             v = random.choice(fun.vars)
#             myvars.remove(v)  # 不能自己等于自己
#             return v.name + ' = ' + self._edit_var_value(v, myvars)
#         if fun.mine == Fake.FMEMBER and cla.vars and r < 0.90:
#             v = random.choice(cla.vars)
#             myvars.remove(v)  # 不能自己等于自己
#             return v.name + ' = ' + self._edit_var_value(v, myvars)
#
#     def _edit_var(self, var):
#         return self._edit_isa(var.isa) + ' ' + var.name
#
#     def _edit_isa(self, isa):
#         isa = self.ctx.get_isa(isa)
#         if isa is None:
#             return 'void'
#         return isa.name if Fake.is_compact(isa) else (isa.name + '*')
#
#     def _rand_local_var(self, cla, fun, isa=None):
#         name = self.ctx.gen_noun()
#         if fun.args:
#             for v in fun.args:
#                 if v.name == name:
#                     return self._rand_local_var(cla, fun, isa)
#         if fun.vars:
#             for v in fun.vars:
#                 if v.name == name:
#                     return self._rand_local_var(cla, fun, isa)
#         if isa is None:
#             isa = self._rand_choice_isa(cla)
#         return Fake.Var(name, isa)
#
#     def _rand_cond(self, cla, fun, myvars=None):
#         if myvars is None:
#             myvars = self.ctx.get_scope_vars(cla, fun)
#         if myvars:
#             bset, ptrs, ints = [], [], []
#             for v in myvars:
#                 if Fake.is_compact(v.isa):
#                     if isinstance(v.isa, Fake.Digit):
#                         ints.append(v)
#                     elif v.isa.name == 'BOOL':
#                         bset.append(v)
#                 else:
#                     ptrs.append(v)
#             if bset:
#                 return random.choice(bset).name
#             if ptrs and random.random() < 0.5:
#                 return random.choice(ptrs).name
#             if ints:
#                 return '%s %s %d' % (random.choice(ints).name, self._rand_symbol(), random.randint(-1, 1))
#         return self._rand_true_cond(cla, fun, myvars)
#
#     def _rand_true_cond(self, cla, fun, myvars=None):
#         if myvars is None:
#             myvars = self.ctx.get_scope_vars(cla, fun)
#         if myvars:
#             ints = self.ctx.get_int_vars(myvars)
#             if ints:
#                 v = random.choice(ints)
#                 r = random.random()
#                 if r < 0.25:
#                     return '%d < %s' % (v.isa.area[0] - random.randint(1, 8), v.name)
#                 if r < 0.50:
#                     return '%d <= %s' % (v.isa.area[0] - random.randint(0, 8), v.name)
#                 if r < 0.75:
#                     return '%d > %s' % (v.isa.area[1] + random.randint(1, 8), v.name)
#                 if r < 1.00:
#                     return '%d >= %s' % (v.isa.area[1] + random.randint(0, 8), v.name)
#         return 'nil != ' + self._rand_singleton()
#
#     @staticmethod
#     def _rand_symbol():
#         return random.choice(('>', '<', '>=', '<=', '=='))
#
#     @staticmethod
#     def _rand_singleton():
#         return random.choice((
#             '[[NSBundle mainBundle] infoDictionary]',
#             '[NSUserDefaults standardUserDefaults]',
#             '[NSThread currentThread]',
#             '[NSRunLoop currentRunLoop]',
#             '[NSProcessInfo processInfo]',
#             '[NSFileManager defaultManager]',
#             '[NSNotificationCenter defaultCenter]',
#             '[UIApplication sharedApplication]',
#             '[UIScreen mainScreen]',
#             '[UIDevice currentDevice]'
#         ))
#
#     def _call_class_fun(self, cla, fun, myvars):
#         if fun.mine == Fake.FMEMBER:
#             target = '[[[%s alloc] init] autorelease]' % cla.name
#         else:
#             target = cla.name
#         return self._call_fun(cla, fun, target, myvars)
#
#     def _call_fun(self, cla, fun, target, myvars=None):
#         s = '[' + target
#         msgs = fun.name.split(':')
#         for i in range(len(msgs)):
#             if not msgs[i]:
#                 continue
#             s += ' ' + msgs[i]
#             if fun.args:
#                 s += ':' + self._edit_var_value(fun.args[i], myvars, isargs=True)
#         s += ']'
#         return s
#
#     def _edit_var_value(self, var, myvars, isargs=False):
#         return self._edit_isa_value(var.isa, myvars, isargs)
#
#     def _edit_isa_value(self, isa, myvars, isargs=False):
#         isa = self.ctx.get_isa(isa)
#         if myvars and random.random() < 0.3:
#             objs = self.ctx.get_isa_vars(myvars, isa)
#             if objs:
#                 return random.choice(objs).name
#         if isinstance(isa, Fake.IFace):
#             objs = self.ctx.get_isa_vars(myvars, isa)
#             return random.choice(objs).name if objs else 'nil'
#         if isinstance(isa, Fake.Digit):
#             return self._edit_digit_value(isa)
#         if isinstance(isa, Fake.Basic):
#             return self._edit_basic_value(isa, myvars)
#         if isinstance(isa, Fake.BFace):
#             return '[[[%s alloc] init] autorelease]' % isa.name if random.random() < 0.6 else 'nil'
#         if isinstance(isa, Fake.CFace):
#             if isargs:
#                 objs = self.ctx.get_isa_vars(myvars, isa)
#                 return random.choice(objs).name if objs else 'nil'
#             return '[[[%s alloc] init] autorelease]' % isa.name if random.random() < 0.8 else 'nil'
#         log.e('unknow support isa:', isa)
#
#     @staticmethod
#     def _edit_digit_value(cla):
#         d = random.randint(cla.area[0], cla.area[1])
#         if cla.name == 'float' or cla.name == 'double' or cla.name == 'CGFloat':
#             return '%g' % d
#         return str(d)
#
#     def _edit_basic_value(self, cla, myvars):
#         objs = self.ctx.get_isa_vars(myvars, cla)
#         noun = self.ctx.gen_noun()
#         rate = random.random()
#         if cla.name == 'NSData':
#             if rate < 0.1 and objs:
#                 return random.choice(objs).name
#             if rate < 0.8:
#                 if random.random() < 0.2:
#                     return '[NSData dataWithContentsOfFile:@"%s"]' % noun
#                 else:
#                     return '[NSData dataWithBytes:[@"%s" UTF8String] length:[@"%s" length]]' % (noun, noun)
#             if rate < 0.9:
#                 return '[NSData data]'
#             return 'nil'
#         if cla.name == 'NSString':
#             if rate < 0.1 and objs:
#                 return random.choice(objs).name
#             if rate < 0.5:
#                 return '[NSString stringWithFormat:@"%%@%%d", @"%s", %d]' % (noun, random.randint(0, 9))
#             if rate < 0.9:
#                 return '[NSString stringWithUTF8String:"%s"]' % noun
#             return 'nil'
#         if cla.name.endswith('Array'):
#             if rate < 0.1 and objs:
#                 return random.choice(objs).name
#             if rate < 0.9:
#                 return '[%s arrayWithObjects:%snil]' % (cla.name, self._edit_seq(myvars))
#             return 'nil'
#         if cla.name.endswith('Set'):
#             if rate < 0.1 and objs:
#                 return random.choice(objs).name
#             if rate < 0.9:
#                 return '[%s setWithObjects:%snil]' % (cla.name, self._edit_seq(myvars))
#             return 'nil'
#         if cla.name.endswith('Dictionary'):
#             if rate < 0.1 and objs:
#                 return random.choice(objs).name
#             if rate < 0.9:
#                 return '[%s dictionaryWithObjectsAndKeys:%snil]' % (cla.name, self._edit_vks(myvars))
#             return 'nil'
#         if cla.name == 'NSRange':
#             return 'NSMakeRange(%d, %d)' % (random.randint(0, 8), random.randint(8, 16))
#         if cla.name == 'CGPoint':
#             if rate < 0.5:
#                 return 'CGPointMake(%d, %d)' % (random.randint(0, 1125), random.randint(0, 2436))
#             return 'CGPointZero'
#         if cla.name == 'CGSize':
#             if rate < 0.5:
#                 return 'CGSizeMake(%d, %d)' % (random.randint(1, 1125), random.randint(1, 2436))
#             return 'CGSizeZero'
#         if cla.name == 'CGRect':
#             if rate < 0.4:
#                 return 'CGRectMake(%d, %d, %d, %d)' % (
#                     random.randint(0, 1125), random.randint(0, 2436), random.randint(1, 1125), random.randint(1, 2436))
#             if rate < 0.8:
#                 return 'CGRectZero'
#             return 'CGRectNull'
#         if cla.name == 'BOOL':
#             return 'YES' if rate < 0.5 else 'NO'
#
#     def _edit_seq(self, myvars):
#         s = ''
#         if random.random() < 0.5:
#             noun = random.random() < 0.5
#             for i in range(random.randint(3, 8)):
#                 s += '@"%s", ' % (self.ctx.gen_noun() if noun else self.ctx.gen_verb())
#         else:
#             offs = random.randint(0, 9999)
#             ints = self.ctx.get_int_vars(myvars)
#             if ints:
#                 random.shuffle(ints)
#             for i in range(random.randint(3, 8)):
#                 if ints and random.random() < 0.5:
#                     s += '@(%s), ' % ints[0].name
#                     ints.pop(0)
#                 else:
#                     s += '@(%d), ' % (i + offs)
#         return s
#
#     def _edit_vks(self, myvars):
#         s = ''
#         noun = random.random() < 0.5
#         offs = random.randint(0, 9999)
#         ints = self.ctx.get_int_vars(myvars)
#         if ints:
#             random.shuffle(ints)
#         if random.random() < 0.5:
#             for i in range(random.randint(3, 8)):
#                 s += '@"%s", ' % (self.ctx.gen_noun() if noun else self.ctx.gen_verb())
#                 if ints and random.random() < 0.5:
#                     s += '@(%s), ' % ints[0].name
#                     ints.pop(0)
#                 else:
#                     s += '@(%d), ' % (i + offs)
#         else:
#             for i in range(random.randint(3, 8)):
#                 if ints and random.random() < 0.5:
#                     s += '@(%s), ' % ints[0].name
#                     ints.pop(0)
#                 else:
#                     s += '@(%d), ' % (i + offs)
#                 s += '@"%s", ' % (self.ctx.gen_noun() if noun else self.ctx.gen_verb())
#         return s
#
# class ConfuseMaker:
#     def __init__(self):
#         pass
#
#     def build(self, cla):
#         pass
#
# class FakerBuilder:  # 垃圾代码生成器
#     def __init__(self):
#         res = os.path.join(os.path.dirname(__file__), '../../extension/ECDICT/res')
#         self.nouns = FS.read_text(os.path.join(res, 'starnoun.txt')).split('\n')[0:-1]
#         self.verbs = FS.read_text(os.path.join(res, 'starverb.txt')).split('\n')[0:-1]
#
#         ctx = EnvContext()
#         self._cxenv = CxEnv(ctx)
#         self._ocenv = OCEnv(ctx)
#         self._context = ctx
#         self._confuse = ConfuseMaker()
#
#     def build(self, dest, zone, nums):
#         numiface = max(0, Rand.scaling(int(nums * 0.05), -0.2))
#         numclass = max(0, nums - numiface)
#         log.d('build faker: iface(%d)+class(%d)=%d' % (numiface, numclass, nums))
#         self._ocenv.setup(zone, numiface, numclass)
#         self._calc_ocuse_tree()
#         self._full_ocifa_apis()
#         self._full_occla_impl()
#         self._output(dest)
#         print('faker build done', self._mymain.name)
#
#     def _calc_ocuse_tree(self):  # 生成引用树
#         self._mymain = self._ocenv.myimpls[0]  # 入口类
#         samp = None
#         temp = self._ocenv.myimpls[1:]
#         for i in range(min(random.randint(2, 9), len(temp)), 0, -1):  # 引用层级
#             nums = Rand.bonus(len(temp), i, 2)
#             part = [temp[x] for x in range(nums)]
#             temp = temp[nums:]
#             if samp is None:
#                 self._mymain.uses = part
#                 self._mymain.uses.extend(Rand.sampling(self._ocenv.myviews, random.randint(-3, 3)))
#                 self._mymain.uses.extend(Rand.sampling(self._ocenv.myctrls, random.randint(-3, 3)))
#             else:
#                 for cla in samp:
#                     cla.uses = Rand.auto_sampling(part, 1, 10)
#                     cla.uses.extend(Rand.sampling(self._ocenv.myviews, random.randint(-3, 3)))
#                     cla.uses.extend(Rand.sampling(self._ocenv.myctrls, random.randint(-3, 3)))
#             samp = part
#         for cla in self._ocenv.myviews:
#             cla.uses = Rand.auto_sampling(samp, 1, 8)
#         for cla in self._ocenv.myctrls:
#             cla.uses = Rand.auto_sampling(samp, 1, 8)
#             cla.uses.extend(Rand.sampling(self._ocenv.myviews, random.randint(-3, 3)))
#         # interface
#         temp = samp[0:int(len(samp) * 0.5)]
#         for ifa in self._ocenv.myfaces:
#             ifa.uses = Rand.sampling(temp, random.randint(-6, 3))
#         for cla in samp[int(len(samp) * 0.5):]:
#             cla.apis = Rand.sampling(self._ocenv.myfaces, random.randint(0, 1))
#             cla.apis.extend(Rand.sampling(self._ocenv.uifaces, random.randint(-1, 2)))
#
#     def _full_ocifa_apis(self):
#         for ifa in self._ocenv.myfaces:
#             less = len(ifa.uses) if ifa.uses else 1
#             array = []
#             for i in range(random.randint(less, less + random.randint(0, 3))):
#                 array.append(self._ocenv.declare_func(ifa, max(0, random.randint(-1, 3)), set()))
#             ifa.funs = tuple(array)
#
#     def _full_occla_impl(self):
#         array, scope = [], set()
#         for cla in self._ocenv.myviews:
#             self._ocenv.declare_vars(cla, max(0, random.randint(-5, 3)), scope)
#             less = len(cla.uses) if cla.uses else 1
#             for i in range(random.randint(less, less + random.randint(0, 16))):
#                 array.append(self._ocenv.declare_func(cla, max(0, random.randint(-1, 3)), set(scope)))
#             cla.funs = tuple(array)
#             array.clear()
#             scope.clear()
#         for cla in self._ocenv.myctrls:
#             self._ocenv.declare_vars(cla, max(0, random.randint(-5, 3)), scope)
#             less = len(cla.uses) if cla.uses else 1
#             for i in range(random.randint(less, less + random.randint(0, 16))):
#                 array.append(self._ocenv.declare_func(cla, max(0, random.randint(-1, 3)), set(scope)))
#             cla.funs = tuple(array)
#             array.clear()
#             scope.clear()
#         for cla in self._ocenv.myimpls:
#             self._ocenv.declare_vars(cla, max(0, random.randint(-5, 3)), scope)
#         # if self._mymain != cla:
#             less = len(cla.uses) if cla.uses else 1
#             for i in range(random.randint(less, less + random.randint(0, 16))):
#                 array.append(self._ocenv.declare_func(cla, max(0, random.randint(-1, 3)), set(scope)))
#             cla.funs = tuple(array)
#             array.clear()
#         # else:
#         #     self._confuse.build(cla)
#             scope.clear()
#
#     def _output(self, dest):
#         FS.cleanup_dir(dest)
#         for i, cla in enumerate(self._ocenv.myfaces):
#             log.d('output face:', i + 1, cla.name)
#             h = self._ocenv.edit_iface(cla)
#             FS.write_text(os.path.join(dest, cla.name + '.h'), h)
#         for i, cla in enumerate(self._ocenv.myviews):
#             log.d('output view:', i + 1, cla.name)
#             h, m = self._ocenv.edit_class(cla)
#             FS.write_text(os.path.join(dest, cla.name + '.h'), h)
#             FS.write_text(os.path.join(dest, cla.name + '.m'), m)
#         for i, cla in enumerate(self._ocenv.myctrls):
#             log.d('output ctrl:', i + 1, cla.name)
#             h, m = self._ocenv.edit_class(cla)
#             FS.write_text(os.path.join(dest, cla.name + '.h'), h)
#             FS.write_text(os.path.join(dest, cla.name + '.m'), m)
#         for i, cla in enumerate(self._ocenv.myimpls):
#             log.d('output impl:', i + 1, cla.name)
#             h, m = self._ocenv.edit_class(cla)
#             FS.write_text(os.path.join(dest, cla.name + '.h'), h)
#             FS.write_text(os.path.join(dest, cla.name + '.m'), m)