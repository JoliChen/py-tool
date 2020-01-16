# -*- coding: utf-8 -*-
# @Time    : 2019/7/17 4:23 PM
# @Author  : Joli
# @Email   : 99755349@qq.com
import os
import threading
import time

from PIL import Image
import wx
import wx.lib.agw.aui as aui

from jonlin.utils import FS, Log

log = Log.Logger(__file__)

class Kit:
    # def is_gray(image):
    #     return len(image.getbands()) == 1

    # def calc_pixel_rect(image):
    #     pixels = image.load()
    #     w, h = image.size
    #     box = [w, h, 0, 0]
    #     for x in range(w):
    #         for y in range(h):
    #             if pixels[x, y][3] > 0:
    #                 # print(x, y, pixels[x, y][3])
    #                 if x < box[0]:
    #                     box[0] = x
    #                 elif x > box[2]:
    #                     box[2] = x
    #                 if y < box[1]:
    #                     box[1] = y
    #                 elif y > box[3]:
    #                     box[3] = y
    #     return box

    @staticmethod
    def is_rect_equal(a, b):
        return a == b

    @staticmethod
    def is_rect_outside(a, b):
        return a[0] < b[0] or a[1] < b[1] or a[2] > b[2] or a[3] > b[3]

    @staticmethod
    def do_offset(frames, sx=0, sy=0):
        newframes = []
        for image in frames:
            if 0 == sx and 0 == sy:
                newframes.append(image)
            else:
                w, h = image.size
                box = (w + abs(sx), h + abs(sy))
                new_image = Image.new('RGBA', box)
                box = [0, 0]
                if sx > 0:
                    box[0] = sx
                if sy > 0:
                    box[1] = sy
                new_image.paste(image, box)
                newframes.append(new_image)
        return newframes

    @staticmethod
    def do_scale(frames, scale):
        newframes = []
        for image in frames:
            if 1.0 == scale:
                newframes.append(image)
            else:
                w, h = image.size
                box = (int(w * scale), int(h * scale))
                new_image = image.resize(box, Image.ANTIALIAS)
                newframes.append(new_image)
        return newframes

    @classmethod
    def do_crop(cls, frames, box):
        newframes = []
        for image in frames:
            w, h = image.size
            if cls.is_rect_equal(box, (0, 0, w, h)):
                newframes.append(image)
            else:
                # pixel_box = image.split()[3].getbbox()
                # if is_rect_outside(pixel_box, box):
                #     return frames  # 不能把颜色区域检测掉
                cut_image = image.crop(box)
                newframes.append(cut_image)
        return newframes

class Timeline(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # self._muetx = threading.Lock()

    def run(self):
        ms = 0
        while True:
            # self._muetx.acquire()
            dt = self._delay
            # self._muetx.release()
            cs = time.clock() * 1000
            nf = int((cs - ms) / dt)
            ms += nf * dt
            while nf > 0:
                self._tickfunc(dt)
                nf -= 1

    def set_tickfunc(self, tick):
        # self._muetx.acquire()
        self._tickfunc = tick
        # self._muetx.release()

    def set_fps(self, fps):
        # self._muetx.acquire()
        self._fps = fps
        self._delay = 1000 / fps
        # self._muetx.release()

# class Avatar(wx.StaticBitmap):
class Avatar(wx.Panel):
    def __init__(self, parent):
        # wx.StaticBitmap.__init__(self, parent, wx.ID_ANY, wx.NullBitmap)
        wx.Panel.__init__(self, parent, size=(1080, 1080))
        self._images = None
        self._frames = None
        self._findex = 0
        self._fcount = 0
        self._active = False
        # self._bmd = wx.StaticBitmap(self, wx.ID_ANY, wx.NullBitmap)
        # self._bmd.Hide()

    def get_index(self):
        return self._findex

    def get_count(self):
        return self._fcount

    def load(self, folder, active=False):
        files = FS.walk_files(folder, ewhites=['.png'], cut=len(folder) + 1)
        if not files:
            log.i('no file input', folder)
            return
        files.sort()
        images, frames = [], []
        for name in files:
            image = wx.Image(os.path.join(folder, name), wx.BITMAP_TYPE_PNG)
            # image.GetSize()
            images.append(image)
            frames.append(wx.Bitmap(image))
        self._fcount = len(frames)
        self._findex = 0
        self._frames = frames
        self._images = images
        self._active = active
        # self._bmd.SetBitmap(self._frames[0])

    def goto_and_stop(self, index):
        if index < 0 or index >= self._fcount:
            log.d('index out of range')
            return
        self._active = False
        self._findex = index
        # self._bmd.SetBitmap(self._frames[index])

    def goto_and_play(self, index):
        if index < 0 or index >= self._fcount:
            log.d('index out of range')
            return
        self._findex = index
        # self._bmd.SetBitmap(self._frames[index])
        self._active = True

    def play(self):
        self._active = True

    def pause(self):
        self._active = False

    def tick(self):
        if self._active and self._fcount > 0:
            i = (self._findex + 1) % self._fcount
            # self._bmd.SetBitmap(self._frames[i])
            self._findex = i
            # print(self.GetPosition(), self.GetSize())

            ax, ay = self.GetPosition()
            aw, ah = self.GetSize()
            # print(ax, ay, aw, ah)

            dc = wx.ClientDC(self)
            dc.SetBackground(wx.TRANSPARENT_BRUSH)
            dc.SetPen(wx.GREEN_PEN)
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.Clear()

            if self.getbmd():
                dc.DrawBitmap(self.getbmd(), 0, 0, True)
            dc.DrawRectangle(1, 1, aw + 1, ah + 1)
            dc.DrawLine(200, 200, 400, 400)

    def getbmd(self):
        return self._frames[self._findex] if self._frames else None

class Window(wx.Frame):
    FPS = 60
    TEXT_IMPORT = '导入'
    TEXT_EXPORT = '导出'
    TEXT_ANCHOR = '刷新锚点'
    TEXT_OFFSET = '刷新偏移'
    TEXT_SCALE  = '刷新缩放'

    def __init__(self, parent):
        wx.Frame.__init__(self, parent=parent, title='Model Editor', size=(1200, 1200))
        self._drag_object = None
        self._loadui()
        self._clock = 0
        self._ticks = 0
        self._timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._ontick, self._timer)
        self._timer.Start(1000 / self.FPS)

    def _loadui(self):
        self._top_panel = self._build_top()
        bottom_panel = self._build_bottom()

        self._layout = aui.AuiManager()
        self._layout.SetManagedWindow(self)
        self._layout.AddPane(
            self._top_panel,
            aui.AuiPaneInfo().Name("TopView").CenterPane().Show()
        )
        self._layout.AddPane(
            bottom_panel,
            aui.AuiPaneInfo().Name("BottomView").Bottom().MinSize((-1, 110)).CaptionVisible(False)
        )

        self._anchorx_text.SetLabelText('0.5')
        self._anchory_text.SetLabelText('0.3')
        self._offsetx_text.SetLabelText('0')
        self._offsety_text.SetLabelText('0')
        self._scalex_text.SetLabelText('0')
        self._scaley_text.SetLabelText('0')
        self._layout.Update()

    def _build_top(self):
        panel = wx.Panel(self)
        panel.SetBackgroundColour('Black')

        avatar = Avatar(panel)
        avatar.Bind(wx.EVT_LEFT_DOWN, self._onmouse_down)
        avatar.Bind(wx.EVT_MOTION, self._onmouse_move)
        avatar.Bind(wx.EVT_LEFT_UP, self._onmouse_up)
        self._avatar = avatar

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(avatar, proportion=100, flag=wx.ALIGN_CENTER)
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hbox, proportion=100, flag=wx.ALIGN_CENTER)
        panel.SetSizer(vbox)
        return panel

    def _build_bottom(self):
        panel = wx.Panel(self)
        # panel.SetBackgroundColour('White')

        self._src_text = wx.TextCtrl(panel, style=wx.TE_LEFT)
        self._src_text.SetEditable(False)
        import_btn = wx.Button(panel, label=self.TEXT_IMPORT)
        import_btn.Bind(wx.EVT_BUTTON, self._onclick_import)
        export_btn = wx.Button(panel, label=self.TEXT_EXPORT)
        export_btn.Bind(wx.EVT_BUTTON, self._onclick_export)
        src_box = wx.BoxSizer(wx.HORIZONTAL)
        src_box.Add(self._src_text, proportion=6, border=3, flag=wx.ALL)
        src_box.Add(import_btn, proportion=2, border=3, flag=wx.ALL)
        src_box.Add(export_btn, proportion=2, border=3, flag=wx.ALL)

        left_pannel = self._build_bottom_left(panel)
        right_pannel = self._build_bottom_right(panel)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(left_pannel, proportion=0, border=60, flag=wx.RIGHT)
        hbox.Add(right_pannel)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(src_box, proportion=0, border=0, flag=wx.ALL)
        vbox.Add(hbox, proportion=0, border=0, flag=wx.ALL)
        panel.SetSizer(vbox)
        return panel

    def _build_bottom_left(self, parent):
        panel = wx.Panel(parent)

        self._anchorx_text = wx.TextCtrl(panel, style=wx.TE_LEFT)
        self._anchory_text = wx.TextCtrl(panel, style=wx.TE_LEFT)
        anchorx_label = wx.StaticText(panel, label='x:', style=wx.RIGHT)
        anchory_label = wx.StaticText(panel, label='y:', style=wx.RIGHT)
        anchor_btn = wx.Button(panel, label=self.TEXT_ANCHOR)
        # anchor_btn.Bind(wx.EVT_BUTTON, self._onbtn_click)
        anchor_box = wx.BoxSizer(wx.HORIZONTAL)
        anchor_box.Add(anchorx_label, proportion=0, border=0, flag=wx.RIGHT)
        anchor_box.Add(self._anchorx_text, proportion=0, border=5, flag=wx.RIGHT)
        anchor_box.Add(anchory_label, proportion=0, border=0, flag=wx.RIGHT)
        anchor_box.Add(self._anchory_text, proportion=0, border=10, flag=wx.RIGHT)
        anchor_box.Add(anchor_btn)

        self._offsetx_text = wx.TextCtrl(panel, style=wx.TE_LEFT)
        self._offsety_text = wx.TextCtrl(panel, style=wx.TE_LEFT)
        offsetx_label = wx.StaticText(panel, label='x:', style=wx.RIGHT)
        offsety_label = wx.StaticText(panel, label='y:', style=wx.RIGHT)
        offset_btn = wx.Button(panel, label=self.TEXT_OFFSET)
        offset_btn.Bind(wx.EVT_BUTTON, self._onclick_offset)
        offset_box = wx.BoxSizer(wx.HORIZONTAL)
        offset_box.Add(offsetx_label, proportion=0, border=0, flag=wx.RIGHT)
        offset_box.Add(self._offsetx_text, proportion=0, border=5, flag=wx.RIGHT)
        offset_box.Add(offsety_label, proportion=0, border=0, flag=wx.RIGHT)
        offset_box.Add(self._offsety_text, proportion=0, border=10, flag=wx.RIGHT)
        offset_box.Add(offset_btn)

        self._scalex_text = wx.TextCtrl(panel, style=wx.TE_LEFT)
        self._scaley_text = wx.TextCtrl(panel, style=wx.TE_LEFT)
        scalex_label = wx.StaticText(panel, label='x:', style=wx.RIGHT)
        scaley_label = wx.StaticText(panel, label='y:', style=wx.RIGHT)
        scale_btn = wx.Button(panel, label=self.TEXT_SCALE)
        scale_btn.Bind(wx.EVT_BUTTON, self._onclick_scale)
        scale_box = wx.BoxSizer(wx.HORIZONTAL)
        scale_box.Add(scalex_label, proportion=0, border=0, flag=wx.RIGHT)
        scale_box.Add(self._scalex_text, proportion=0, border=5, flag=wx.RIGHT)
        scale_box.Add(scaley_label, proportion=0, border=0, flag=wx.RIGHT)
        scale_box.Add(self._scaley_text, proportion=0, border=10, flag=wx.RIGHT)
        scale_box.Add(scale_btn)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(anchor_box, proportion=0, border=0, flag=wx.ALL)
        vbox.Add(offset_box, proportion=0, border=0, flag=wx.ALL)
        vbox.Add(scale_box, proportion=0, border=0, flag=wx.ALL)
        panel.SetSizer(vbox)
        return panel

    def _build_bottom_right(self, parent):
        panel = wx.Panel(parent)
        # scalex_label = wx.StaticText(panel, label='x:', style=wx.RIGHT)
        return panel

    def _onmouse_down(self, evt):
        obj = evt.EventObject
        if obj == self._avatar:
            obj.drag_origin = obj.GetPosition()
            obj.drag_mousep = wx.GetMousePosition()
            self._drag_object = obj
            self._avatar.CaptureMouse()

    def _onmouse_move(self, evt):
        if evt.Dragging() and evt.LeftIsDown():
            obj = self._drag_object
            if obj is not None:
                mp = obj.drag_origin + (wx.GetMousePosition() - obj.drag_mousep)
                obj.SetPosition(mp)
                evt.Skip()

    def _onmouse_up(self, evt):
        obj = evt.EventObject
        if obj == self._avatar:
            self._drag_object = None
            self._avatar.ReleaseMouse()

    def _onclick_import(self, evt):
        dialog = wx.DirDialog(self, u'选择导入目录', style=wx.DD_DEFAULT_STYLE)
        if dialog.ShowModal() != wx.ID_OK:
            return
        folder = dialog.GetPath()
        dialog.Destroy()
        log.i('import', folder)
        self._avatar.load(folder, active=True)
        # print(self._avatar.GetPosition(), self._avatar.GetSize())
        self._top_panel.Layout()

    def _onclick_export(self, evt):
        pass

    def _onclick_offset(self, evt):
        pass

    def _onclick_scale(self, evt):
        pass

    def _ontick(self, evt):
        self._avatar.tick()
        self._ticks += 1
        clock = time.time()
        sec = clock - self._clock
        if sec > 1:
            print('fps', sec, sec * 1000 / self._ticks)
            self._clock = clock
            self._ticks = 0
        # print(sec)

        # tms = self._tms + (cms - self._cms)
        # while tms > self._fms:
        #     print(tms, cms)
        #     tms -= self._fms
        #     if self._avatar:
        #         self._avatar.tick()
        # self._cms = cms
        # self._tms = tms

class App(wx.App):
    def __init__(self):
        wx.App.__init__(self)
        self._window = Window(None)

    def launch(self):
        self._window.Show()
        self.MainLoop()

def test(src, dst):
    # filelist = FS.walk_files(src, ext_whites=['.png'], cut_pos=len(src) + 1)
    # frames = []
    # for filename in filelist:
    #     image = Image.open(os.path.join(src, filename))
    #     frames.append(image)
    # frames = Kit.do_crop(frames, (20, 20, 50, 50))
    # for i in range(len(frames)):
    #     image = frames[i]
    #     filepath = os.path.join(dst, filelist[i])
    #     FS.make_parent(filepath)
    #     image.save(filepath)
    App().launch()