import asyncio
import math
import os

import cv2
import numpy
import win32con
from ahk import AHK
import win32gui
import win32ui

from Utils.InputWrapper import *

from Constant import Constants

sep = os.path.sep
ahk = AHK(executable_path=f'C:{sep}Program Files{sep}AutoHotkey{sep}AutoHotkey.exe')
Resolution = (1280, 720)


class SC2Window:
    def __init__(self):
        # 창 찾고 바운드 저장
        self.offset_x = -7
        self.offset_y = 0

        self.ahk_win = ahk.find_window(class_name=b'StarCraft II')
        self.ahk_win.activate()
        self.ahk_win.set_always_on_top(False)
        self.ahk_win.move(self.offset_x, self.offset_y, *Resolution)

        self.hwnd = win32gui.FindWindow(None, '스타크래프트 II')
        self.rect = win32gui.GetWindowRect(self.hwnd)
        self.clientRect = win32gui.GetClientRect(self.hwnd)
        self.titleBarHeight = self.rect[3] - self.clientRect[3]

        self.hwndDC = win32gui.GetWindowDC(self.hwnd)
        self.mfcDC = win32ui.CreateDCFromHandle(self.hwndDC)
        self.captureDC = self.mfcDC.CreateCompatibleDC()
        self.captureBitMap = win32ui.CreateBitmap()
        self.captureBitMap.CreateCompatibleBitmap(self.mfcDC, self.clientRect[2], self.clientRect[3])
        self.captureDC.SelectObject(self.captureBitMap)

    def __del__(self):
        self.captureDC.DeleteDC()
        self.mfcDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, self.hwndDC)
        win32gui.DeleteObject(self.captureBitMap.GetHandle())
        cv2.destroyAllWindows()

    def grab_screen(self) -> numpy.ndarray:
        self.captureDC.BitBlt((0, 0), (self.clientRect[2], self.clientRect[3]), self.mfcDC, (-self.offset_x, self.titleBarHeight + self.offset_x), win32con.SRCCOPY)
        signed_ints_array = self.captureBitMap.GetBitmapBits(True)
        ret = numpy.frombuffer(signed_ints_array, dtype='uint8')
        ret.shape = (self.clientRect[3], self.clientRect[2], 4)
        return ret
