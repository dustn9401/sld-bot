import asyncio
import os
import time

import ahk.window
import win32api
import win32con
import win32gui
from ahk import AHK

sep = os.path.sep
ahk_inst = AHK(executable_path=f'C:{sep}Program Files{sep}AutoHotkey{sep}AutoHotkey.exe')


async def send_key_press_async(ahk_win: ahk.window.Window, keys, delay=0.2):
    ahk_win.send(keys, blocking=False)
    await asyncio.sleep(delay)


async def send_click_async(ahk_win: ahk.window.Window, pos, delay=0.2):
    ahk_win.click(pos, blocking=False, button='L')
    await asyncio.sleep(delay)