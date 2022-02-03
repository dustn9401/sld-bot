import os

import win32api
import win32con
import win32gui
from ahk import AHK
import Constant.ScreenPositions as Positions
import Constant.Keymaps as KeyMaps

sep = os.path.sep
ahk_inst = AHK(executable_path=f'C:{sep}Program Files{sep}AutoHotkey{sep}AutoHotkey.exe')

if __name__ == '__main__':
    ahk_win = ahk_inst.find_window(class_name=b'StarCraft II')
    ahk_win.activate()
    hwnd = win32gui.FindWindow(None, '스타크래프트 II')

    lParam = win32api.MAKELONG(Positions.TopRight[0], Positions.TopRight[1] - 30)
    win32gui.SendMessage(hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, lParam)
    win32gui.SendMessage(hwnd, win32con.WM_RBUTTONUP, None, lParam)