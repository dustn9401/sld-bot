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


def send_key_press(ahk_win: ahk.window.Window, keys):
    ahk_win.send(keys)


async def send_key_press_async(ahk_win: ahk.window.Window, keys, delay=0.1):
    send_key_press(ahk_win, keys)
    await asyncio.sleep(delay)


def send_click(pos, btn=0):
    ahk_inst.mouse_position = pos
    ahk_inst.click(button='L' if btn == 0 else 'R' if btn == 1 else 'M')


async def send_click_async(pos, btn=0, delay=0.1):
    send_click(pos, btn)
    await asyncio.sleep(delay)