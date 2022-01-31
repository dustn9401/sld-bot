import asyncio
import os

import cv2
import numpy as np
import win32con
from ahk import AHK
import win32gui
import win32ui

from Constant import Constants

sep = os.path.sep
ahk = AHK(executable_path=f'C:{sep}Program Files{sep}AutoHotkey{sep}AutoHotkey.exe')

Resolution = (1280, 720)
class SC2Window:

    def __init__(self):
        # 창 찾고 바운드 저장
        self.hwnd = win32gui.FindWindow(None, Constants.WindowName)
        self.offset_x = -7
        self.offset_y = 0
        win32gui.MoveWindow(self.hwnd, self.offset_x, self.offset_y, Resolution[0], Resolution[1], True)
        win32gui.SetForegroundWindow(self.hwnd)
        self.hwndDC = win32gui.GetWindowDC(self.hwnd)
        self.mfcDC = win32ui.CreateDCFromHandle(self.hwndDC)
        self.captureDC = self.mfcDC.CreateCompatibleDC()
        self.captureBitMap = win32ui.CreateBitmap()
        self.captureBitMap.CreateCompatibleBitmap(self.mfcDC, Resolution[0], Resolution[1])
        self.captureDC.SelectObject(self.captureBitMap)
        self.ahk_win = ahk.find_window(title=Constants.WindowName.encode('utf-8'))

    def __del__(self):
        self.captureDC.DeleteDC()
        self.mfcDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, self.hwndDC)
        win32gui.DeleteObject(self.captureBitMap.GetHandle())
        cv2.destroyAllWindows()

    def grab_screen(self):
        self.captureDC.BitBlt((0, 0), (self.w, self.h), self.mfcDC, (0, 0), win32con.SRCCOPY)
        signed_ints_array = self.captureBitMap.GetBitmapBits(True)
        ret = np.frombuffer(signed_ints_array, dtype='uint8')
        ret.shape = (self.h, self.w, 4)
        return ret

    async def update(self):
        while True:
            screen = self.grab_screen()
            await self.check_hp(screen)
            await self.check_sub_skill(screen)

            await asyncio.sleep(0.1)