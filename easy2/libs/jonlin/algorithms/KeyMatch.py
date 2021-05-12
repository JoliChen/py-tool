# -*- coding: utf-8 -*-
# @Time    : 2019/4/15 5:56 PM
# @Author  : Joli
# @Email   : 99755349@qq.com
# 关键词匹配算法

class DFA:
    class EOF:
        pass

    def __init__(self, source, span=True):
        self._span = span
        self._tree = {}
        if source:
            for w in sorted(source.split('\n')):
                w = w.strip()
                if w:
                    self.add(w)
        # print(self._tree)

    def add(self, word):
        n = len(word)
        e = n - 1
        node = self._tree
        for i in range(n):
            c = word[i]
            if self._span and c.isspace():
                continue  # 忽略空格
            nn = node.get(c)
            if nn is None:
                if i != e:
                    nn = {}
                    node[c] = nn
                    node = nn
                else:
                    node[c] = self.EOF
            else:
                if nn != self.EOF:
                    node = nn

    def _find_greed(self, text, node, i, n):
        for i in range(i, n):
            c = text[i]
            if self._span and c.isspace():
                continue  # 忽略空格
            nn = node.get(c)
            if nn is None:
                return i
            if nn == self.EOF:
                return self._find_greed(text, node, i + 1, n)
            node = nn
        return i

    def find(self, text, greed=True, times=0):
        mths = []
        node = None
        b, i, n = 0, 0, len(text)
        while i < n:
            c = text[i]
            if self._span and c.isspace():
                i += 1
                continue  # 忽略空格
            if node is None:
                # match root node
                node = self._tree.get(c)
                if node:
                    if node == self.EOF:
                        mths.append((i, i + 1))
                        if times > 0 and (len(mths) >= times):
                            return mths
                        node = None
                    else:
                        b = i
            else:
                # match next node utils meet eof
                nn = node.get(c)
                if nn == self.EOF:
                    if greed:
                        e = self._find_greed(text, node, i + 1, n)
                        mths.append((b, e))
                        if times > 0 and (len(mths) >= times):
                            return mths
                        i = e - 1
                    else:
                        mths.append((b, i + 1))
                        if times > 0 and (len(mths) >= times):
                            return mths
                    node = None
                else:
                    node = nn
            i += 1
        return mths

class HAS:
    def __init__(self, source, span=True):
        self._span = span
        self._tree = {}
        if source:
            for word in sorted(source.split('\n')):
                word = word.strip()
                if word:
                    self.add(word)
        # print(self._tree)

    def add(self, word):
        f, s = '', ''
        if self._span:
            for c in word:
                if not c.isspace():
                    if not f:
                        f = c
                    else:
                        s += c
        else:
            f = word[0]
            s = word[1:]
        dic = self._tree.get(f)
        if not dic:
            dic = {}
            self._tree[f] = dic
        t = len(s)
        if t > 0:
            arr = dic.get(t)
            if not arr:
                arr = []
                dic[t] = arr
            if s in arr:
                pass
            else:
                arr.append(s)

    def find(self, text, greed=True, times=0):
        mths = []
        i, n = 0, len(text)
        while i < n:
            f, i = self._peek_one(text, i, n)
            if f is None:
                i += 1
                continue
            dic = self._tree.get(f)
            if dic is None:
                i += 1
                continue
            keys = dic.keys()
            if len(keys) > 0:
                for t in sorted(keys, reverse=greed):
                    ss, sl, si = self._peek_all(text, i + 1, n, t)
                    if sl < t:
                        continue
                    if ss in dic[t]:
                        mths.append((i, si + 1))
                        if times > 0 and (len(mths) >= times):
                            return mths
                        i = si
                        break
            else:
                mths.append((i, i + 1))
                if times > 0 and (len(mths) >= times):
                    return mths
            i += 1
        return mths

    def _peek_one(self, text, i, n):
        ss = ''
        while i < n:
            c = text[i]
            if not self._span or not c.isspace():
                ss = c
                break
            i += 1
        return ss, i

    def _peek_all(self, text, i, n, m):
        ss, sl = '', 0
        while i < n:
            c = text[i]
            if not self._span or not c.isspace():
                ss += c
                sl += 1
                if sl == m:
                    break
            i += 1
        return ss, sl, i