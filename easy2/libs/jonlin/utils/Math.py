# -*- coding: utf-8 -*-
# @Time    : 2019/4/16 4:22 PM
# @Author  : Joli
# @Email   : 99755349@qq.com

class Rect:
    def __init__(self, x=0, y=0, width=0, height=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def get_left(self):
        return self.x

    def set_left(self, left):
        self.x = left

    def get_right(self):
        return self.x + self.width

    def set_right(self, right):
        self.width = right - self.x

    def get_top(self):
        return self.y

    def set_top(self, top):
        self.y = top

    def get_bottom(self):
        return self.y + self.height

    def set_bottom(self, bottom):
        self.height = bottom - self.y