# -*- coding: utf-8 -*-
# @Time    : 2019/3/25 7:03 PM
# @Author  : Joli
# @Email   : 99755349@qq.com
import os
import re
import time
from jonlin.utils import Log, FS

log = Log.Logger(__file__)

VERSION = 6
RE_COMMA_END = re.compile(',(\s*?)$')  # 行尾逗号
RE_RAW_BEGIN = re.compile('\[(=*?)\[')  # "[==["
RE_RAW_END = re.compile('\](=*?)\]\)(\s*?)$')  # "]==])\n"
RE_SETNODE = re.compile(':setNode\((.*?)\)(\s*?)$')  # setNode()

class LuaCSBuilder:
    def __init__(self, flag_dangling=2, flag_hidden=1, flag_repeat=0):
        self._flag_dangling = flag_dangling
        self._flag_hidden = flag_hidden
        self._flag_repeat = flag_repeat
        self._cstree = CSTree()

    def build(self, src, dst):
        start_t = time.time()
        if os.path.isdir(src):
            self._build_dir(src, dst)
        elif os.path.isfile(src):
            self._build_lua(src, dst)
        log.i('build csui done, 耗时:%.2fs' % (time.time() - start_t))

    def _build_dir(self, src, dst):
        split_pos = len(src) + 1
        for (root, _, files) in os.walk(src):
            for name in files:
                if not name.endswith('.lua'):
                    continue
                src_path = os.path.join(root, name)
                name = src_path[split_pos:]
                dst_path = os.path.join(dst, name)
                if os.path.isfile(dst_path):
                    if not FS.is_meta_modified(src_path, dst_path, ignore_size=True):
                        continue  # 文件未修改
                self._build_lua(src_path, dst_path)
                # shutil.copystat(src_path, dst_path)
                FS.sync_meta_utime(dst_path, src_path)

    def _build_lua(self, src, dst):
        log.i(src)
        self._cstree.input_init()
        with open(src, 'r', encoding='utf-8') as fp:
            line, comma_open = '', False
            for s in fp.readlines():
                if RE_COMMA_END.search(s):
                    line += s.strip()
                    comma_open = True
                    continue
                if comma_open:
                    line += s.strip()
                    self._cstree.input_line(line)
                    line, comma_open = '', False
                else:
                    self._cstree.input_line(s)
        text = self._cstree.build(self._flag_dangling, self._flag_hidden, self._flag_repeat)
        if text is None:
            log.e('build text error:', src)
        else:
            FS.make_parent(dst)
            with open(dst, 'w', encoding='utf-8') as fp:
                fp.write(text)

class CSTree:
    EDGE_VAR = 'edgeEnabled'
    TAB_NAME = 'result'
    KEYWORDS = (TAB_NAME, EDGE_VAR, 'animation', 'root', 'layout', 'innerCSD', 'innerProject', 'localFrame', 'localLuaFile', 'luaCS')

    class CSNode:
        def __init__(self, name, create):
            self.name = name
            self.create = create
            self.parent = ''
            self.childs = set()
            self.config = []
            self.layout = []
            self.layout_enabled = None  # 是否允许布局组件
            self.v_edge = None  # vertical dege
            self.h_edge = None  # horizontal dege
            self.visible = True
            self.opacity = None
            self.is_cell = None  # scrollview cell
            self.inner_ui = None  # innerCSD and innerProject
            self.inner_animate = None  # innerProject.animation
            self.tolua_invokes = None  # 'tolua.cast(%{widget}s:getVirtualRenderer(), "cc.Label"):setLineBreakWithoutSpace(true)'
            self.cascade_color = None
            self.cascade_opacity = None

        def is_edge(self):
            return (self.v_edge is not None) or (self.h_edge is not None)

        def is_hidden(self):
            return not self.visible or self.opacity == 0

        def is_container(self):
            if self.create.startswith('cc.Node'):
                return True
            if self.create.startswith('ccui.Layout'):
                return True
            return len(self.childs) > 0

        def add_tolua(self, s):
            if self.tolua_invokes is None:
                self.tolua_invokes = [s]
            else:
                self.tolua_invokes.append(s)

        def add_inner_anim(self, s):
            if self.inner_animate is None:
                self.inner_animate = [s]
            else:
                self.inner_animate.append(s)

    def build(self, flag_dangling, flag_hidden, flag_repeat):
        if flag_dangling > 0:
            self._check_dangling_node(flag_dangling)
        if flag_hidden > 0:
            self._check_hidden_node(flag_hidden)
        if flag_repeat > 0:
            self._check_repeat_node(flag_repeat)
        share_var, parent_vars = self._check_variables('_a')
        if len(parent_vars) > 99:
            log.w('local variable limit', len(parent_vars))
        return self._make_text(share_var, parent_vars)

    def _make_text(self, share_var, variables):
        s = ''
        s += 'local luaExtend = require "LuaExtend"\n\n'
        s += 'local luaCS = {}\n\n'
        s += 'function luaCS.create(%s)\n' % self.EDGE_VAR
        # 加载资源
        for sf in sorted(self._sprframes):
            s += '\tcc.SpriteFrameCache:getInstance():addSpriteFrames("' + sf + '")\n'
        s += '\n'
        # 声明变量
        s += '\tlocal ' + share_var + ', ' + (', '.join(variables)) + '\n'
        # 初始化 table
        s += '\tlocal %s = {}\n' % self.TAB_NAME
        s += '\tsetmetatable(%s, luaExtend)\n' % self.TAB_NAME
        s += '\n'
        # 生成配置
        for node in self._widgets:
            if node.name in self._anim_nodes:
                var = self.TAB_NAME + "['" + node.name + "']"
            elif node.name in variables:
                var = node.name
            else:
                var = share_var
            if node.parent in self._anim_nodes:
                parent = self.TAB_NAME + "['" + node.parent + "']"
            elif node.parent in variables:
                parent = node.parent
            else:
                parent = share_var
            s += self._make_node(node, var, parent)
        if self._animation:
            s += '\n\t--Create Animation\n'
            for stat in self._animation:
                s += '\t' + stat + '\n'
        # 文件尾
        s += "\t" + self.TAB_NAME + "['root'] = " + self._root + '\n'
        s += '\treturn %s\n' % self.TAB_NAME
        s += 'end\n\n'
        s += 'return luaCS'
        return s

    def _make_node(self, node, var, parent):
        s = ''
        s += '\t--Create ' + node.name + '\n'
        if node.inner_ui:
            for text in node.inner_ui:
                s += '\t' + text + '\n'
        s += '\t' + var + ' = ' + node.create + '\n'
        s += '\t' + var + (':setName("%s")' % node.name) + '\n'
        for expr in node.config:
            s += '\t' + var + expr + '\n'
        if node.layout and (node.layout_enabled or node.name == self._root):
            s += '\tlayout = ccui.LayoutComponent:bindLayoutComponent(%s)\n' % var
            for stat in node.layout:
                s += '\tlayout' + stat + '\n'
        s += self._make_mark(node, var)
        if node.parent:
            if node.is_cell:
                s += '\t' + parent + (':pushBackCustomItem(%s)' % var) + '\n'
            else:
                s += '\t' + parent + (':addChild(%s)' % var) + '\n'
        return s + '\n'

    def _make_mark(self, node, var):
        s = ''
        if node.is_container():
            if node.cascade_color:
                s += '\t%s:setCascadeColorEnabled(%s)\n' % (var, node.cascade_color)
            if node.cascade_opacity:
                s += '\t%s:setCascadeOpacityEnabled(%s)\n' % (var, node.cascade_opacity)
        if node.tolua_invokes:  # 'tolua.cast(%(widget)s:getVirtualRenderer(), "cc.Label"):setLineBreakWithoutSpace(true)'
            for stat in node.tolua_invokes:
                s += '\t' + (stat % {'widget': var}) + '\n'
        if node.inner_animate:
            s += '\tif nil ~= innerProject.animation then\n'
            for stat in node.inner_animate:
                if stat.startswith('innerProject.'):
                    s += '\t\t' + stat + '\n'  # 'innerProject.animation:setTimeSpeed(1.0000)'
                else:
                    # %(widget)s.animation = innerProject.animation
                    # %(widget)s:runAction(innerProject.animation)
                    s += '\t\t' + var + stat + '\n'
            s += '\tend\n'
        if node.is_edge() and (node.parent == self._root):
            s += '\tif %s then\n' % self.EDGE_VAR
            if node.h_edge is not None:
                s += '\t\tCcFuns.csuiEdgeH(%s, %s)\n' % (var, node.h_edge)
            if node.v_edge is not None:
                s += '\t\tCcFuns.csuiEdgeV(%s, %s)\n' % (var, node.v_edge)
            s += '\tend\n'
        if node.name.startswith('EFFECT_'):
            args = node.name.split('_')
            s += '\tCcFuns.csuiFlash(%s, %s)\n' % (var, ', '.join(args[1:]))
        if node.name.startswith('REDDOT_'):
            args = node.name.split('_')
            s += '\tCcFuns.csuiRedDot(%s, %s)\n' % (var, ', '.join(args[1:]))
        return s

    def _check_variables(self, sharevar):
        variables = ['layout']
        if self._has_inner:
            variables.append('innerCSD')
            variables.append('innerProject')
        if self._animation:
            variables.append('localFrame')
        for node in self._widgets:
            if node.childs:  # node is container
                if node.name not in variables:
                    variables.append(node.name)
        while True:
            if sharevar not in variables:
                break
            sharevar += '_'
        return sharevar, variables

    def _check_dangling_node(self, flag_dangling):
        array = set()
        for node in self._widgets:
            if not node.parent and node.name != self._root:
                array.add(node)
        if flag_dangling == 1:
            for node in array:
                log.w('dangling node:', node.name)
        elif flag_dangling == 2:
            self._erase(array)

    def _check_hidden_node(self, flag_hidden):
        array = set()
        for node in self._widgets:
            if node.is_hidden():
                array.add(node)
                for son in node.childs:
                    array.add(self._find_node(son, node.name))
        if flag_hidden == 1:
            for node in array:
                log.w('hidden node:', node.name)
        elif flag_hidden == 2:
            self._erase(array)

    def _check_repeat_node(self, flag_repeat):
        array = set()
        for i in range(len(self._widgets)):
            node = self._widgets[i]
            for j in range(i + 1, len(self._widgets)):
                other = self._widgets[j]
                if node.name == other.name and node.parent == other.parent:
                    array.add(node)
                    break
        if flag_repeat == 1:
            for node in array:
                log.w('dunplicate node:', node.name)
        elif flag_repeat == 2:
            self._erase(array)

    def _erase(self, array):
        for node in array:
            self._widgets.remove(node)

    def input_init(self):
        self._nline = 0
        self._input = False

    def input_line(self, s):
        self._nline += 1
        if s.startswith('--'):
            return
        if s.startswith("setmetatable(result,"):
            self._onstart()
            return
        if s.startswith("result['root'] = "):
            self._onclose(s)
            return
        if not self._input:
            return
        if self._in_animate > 0:
            self._onanimate(s)
            return
        if s.startswith("local "):
            self._onvar(s)
            return
        if self._is_result_token(s):
            self._onsub(s)
        else:
            self._onrow(s)

    def _onstart(self):
        self._root = None
        self._widgets = []
        self._sprframes = set()
        self._animation = []
        self._in_animate = 0
        self._anim_nodes = set()
        self._inner_csd = []
        self._has_inner = False
        self._in_rawstr = 0
        self._rawstring = ''
        self._input = True

    def _onclose(self, s):
        self._root = self._get_node_name(s[s.rfind('=') + 1:].strip())
        self._widgets.reverse()
        if len(self._animation) < 5:
            self._animation = None
        self._input = False

    def _onanimate(self, s):
        self._in_animate += 1
        if self._in_animate == 2:
            return  # 跳过第二行
        s = s.strip()
        if RE_SETNODE.search(s):
            left = s.rfind('(')
            name = self._get_node_name(s[left+1:-1])
            self._anim_nodes.add(name)
            s = s[0:left] + "(" + self.TAB_NAME + "['" + name + "'])"
        self._animation.append(s)

    def _onvar(self, s):
        assign = self._scan_create(s, 6)
        if assign is None:
            log.e('unexpected local variable', s)
            return
        name = s[6:assign].strip()
        create = s[assign+1:].strip()
        self._oncreate(name, create)

    def _onsub(self, s):
        assign = self._scan_create(s, 8)
        if assign is None:
            self._onrow(s)
            return
        name = self._get_subkey(s[0:assign])
        if name == 'animation':
            self._in_animate += 1
            self._animation.append(s.strip())
            return
        create = s[assign+1:].strip()
        self._oncreate(name, create)

    def _oncreate(self, name, create):
        node = self.CSNode(name, create)
        if self._inner_csd:
            node.inner_ui = self._inner_csd
            self._inner_csd = []
        self._widgets.insert(0, node)

    def _onrow(self, s):
        if self._in_rawstr > 0 or RE_RAW_BEGIN.search(s):
            self._onrstr(s)
            return
        if not s.isspace():
            self._onstat(s.strip())

    # raw string
    def _onrstr(self, s):
        self._rawstring += s
        if not RE_RAW_END.search(s):
            self._in_rawstr += 1
            return
        s = self._rawstring
        self._rawstring = ''
        self._in_rawstr = 0
        self._onstat(s.strip())

    def _onstat(self, s):
        if s.startswith('layout') and self._hook_layout(s):
            return
        if s.startswith('cc.SpriteFrameCache:getInstance():addSpriteFrames'):
            self._sprframes.add(s[51:-2])
            return
        if s.startswith('innerCSD = require('):
            self._inner_csd.append(s)
            return
        if s.startswith('innerProject = '):
            self._inner_csd.append(s.replace('callBackProvider', self.EDGE_VAR))
            # self._inner_csd.append(s.replace('callBackProvider', ''))
            return
        if s.find('innerProject.animation') != -1:
            self._hook_inner_anim(s)
            return
        if s.startswith('tolua.'):
            self._hook_tolua(s)
            return
        self._hook_prop(s)

    def _hook_prop(self, s):
        colon_pos = self._find_colon(s)
        if colon_pos is None:
            log.e('cannot found colon in statement', s)
            return
        expr = s[colon_pos:]
        name = self._get_node_name(s[0:colon_pos])
        node = self._find_node(name)
        if node is None:
            log.e('cannot found widget:' + name + ' -- ' + s)
        else:
            self._hook_node_expr(node, expr)

    def _hook_node_expr(self, node, expr):
        func = expr[1:]
        if func.startswith('setTag'):
            return
        if func.startswith('setName'):
            if node.name != self._get_args(func)[1:-1]:
                log.e('unexpected widget name:' + ' -- %s%s' % (node.name, expr))
            return
        if func.startswith('setCascadeColorEnabled'):
            node.cascade_color = self._get_args(func)
            return
        if func.startswith('setCascadeOpacityEnabled'):
            node.cascade_opacity = self._get_args(func)
            return
        if func.startswith('addChild') or func.startswith('pushBackCustomItem'):
            son_name = self._get_node_name(self._get_args(func))
            son_node = self._find_node(son_name)
            if son_node is None:
                log.e('cannot found child:' + son_name + ' -- %s%s' % (node.name, expr))
            else:
                son_node.is_cell = (func == 'pushBackCustomItem')
                son_node.parent = node.name
                node.childs.add(son_name)
            return
        if func.startswith('setOpacity'):
            node.opacity = int(self._get_args(func))
        elif func.startswith('setVisible'):
            node.visible = bool(self._get_args(func))
        elif func.startswith('setLayoutComponentEnabled'):
            node.layout_enabled = bool(self._get_args(func))
        node.config.append(expr)

    def _hook_layout(self, s):
        expr = s[6:]
        if expr.startswith(' =') or expr.startswith('='):
            # parentheses = s.rfind('(')
            # s = s[0:parentheses] + '%(widget)s)'
            # node.layout.append(s)
            return True  # layout = ccui.LayoutComponent:bindLayoutComponent(%(widget)s)
        if expr.startswith(':'):
            func = expr[1:]
            node = self._last_node()
            if func.startswith('setVerticalEdge'):
                node.v_edge = int(self._get_args(func))
            elif func.startswith('setHorizontalEdge'):
                node.h_edge = int(self._get_args(func))
            node.layout.append(expr)
            return True

    def _hook_inner_anim(self, s):
        node = self._last_node()
        if node.inner_ui is None:
            log.e('last widget no innerCSD -- ', s)
            return
        if not s.startswith('innerProject.') or not s.startswith('innerProject:'):
            if s.find('=') != -1:
                s = s[s.find('.'):]  # %(widget)s.animation = innerProject.animation
            elif s.find('runAction') != -1:
                s = s[s.find(':'):]  # %(widget)s:runAction(innerProject.animation)
        node.add_inner_anim(s)
        self._has_inner = True

    def _hook_tolua(self, s):
        func = s[6:]
        if func.startswith('cast('):
            colon_pos = s.find(':', 10)
            name = self._get_node_name(s[11:colon_pos])
            node = self._find_node(name)
            if node is None:
                log.e('cannot found widget:' + name + ' -- ' + s)
                return
            s = s[0:11] + '%(widget)s' + s[colon_pos:]
            node.add_tolua(s)
        else:
            log.w('unexpected tolua api:', s)

    def _get_node_name(self, token):
        return token if not self._is_result_token(token) else self._get_subkey(token)

    def _scan_create(self, s, start):
        assignment = s.find('=', start)
        if -1 != assignment:
            if self._find_colon(s[0:assignment]) is None:  # 排除括号内参数的等于号
                return assignment

    @staticmethod
    def _find_colon(s):
        p = s.find(':')
        if -1 != p:
            return p
        p = s.find('.')
        if -1 != p:
            return p

    @staticmethod
    def _get_subkey(sub, quotes=("'", '"')):
        s, b = '',  False
        for c in sub:
            if b:
                if c in quotes:
                    return s
                s += c
            elif c in quotes:
                b = True

    @staticmethod
    def _is_result_token(s):
        return s.startswith('result[')

    @staticmethod
    def _get_args(func):
        return func[func.rfind('(')+1:func.rfind(')')]

    def _find_node(self, name, parent=None):
        for node in self._widgets:
            if node.name == name and (parent is None or parent == node.parent):
                return node

    def _last_node(self):
        return self._widgets[0]