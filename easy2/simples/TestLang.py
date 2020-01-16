# -*- coding: utf-8 -*-
# @Time    : 2019/5/5 8:06 PM
# @Author  : Joli
# @Email   : 99755349@qq.com

def test_error():
    # 错误基类
    class LuaError(Exception):
        def __init__(self):
            # self.stack = traceback.format_exc()
            # self.stack = traceback.format_stack()
            import traceback
            traceback.print_stack(limit=-1)

    # 文件尾错误
    class LuaEOFError(LuaError):
        def __init__(self):
            LuaError.__init__(self)

        def __str__(self):
            return 'EOF error'

    print('aaaa')
    e = LuaEOFError()
    raise e
    print('bbbb')

def test_number():
    print(int('0X99', 16))
    print(int('066', 8))
    try:
        return int("fasd")
    except ValueError as ve:
        import traceback
        print(ve)
        print(traceback.format_exc())

def test_repr_eval():
    s = '1, "2", \"3\", '
    print(s)
    print(repr(s))
    print(eval(s))

def test_string():
    pass

def test_collections():
    a1 = ['a' for i in range(5)]
    print(a1)

def text_function():
    def f1(a, *b, c):
        print(a)
        print(b)
        print(*b)
        print(c)
    arr = []
    f1(1, c=5)
    f1(1, *arr, c=5)

def main():
    pass
    # test_error()
    # test_repr_eval()
    # test_number()
    # test_string()
    # test_collections()
    # text_function()
