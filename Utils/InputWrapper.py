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


def send_click(ahk_win: ahk.window.Window, pos, btn=0):
    ahk_inst.click(pos, button='L' if btn == 0 else 'R' if btn == 1 else 'M')
    # ahk_win.click(pos, button='L' if btn == 0 else 'R' if btn == 1 else 'M')


async def send_click_async(ahk_win: ahk.window.Window, pos, btn=0, delay=0.1):
    send_click(ahk_win, pos, btn)
    await asyncio.sleep(delay)


def send_click_hwnd(hwnd, pos):
    lparam = win32api.MAKELONG(pos[0], pos[1] - 31)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
    time.sleep(0.1)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, None, lparam)

async def send_click_hwnd_async(hwnd, pos, btn=0, delay=0.5):
    send_click_hwnd(hwnd, pos)
    await asyncio.sleep(delay)

def send_right_click_hwnd(hwnd, pos):
    lparam = win32api.MAKELONG(pos[0], pos[1] - 31)
    win32gui.PostMessage(hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, lparam)
    time.sleep(0.1)
    win32gui.PostMessage(hwnd, win32con.WM_RBUTTONUP, None, lparam)

async def send_right_click_hwnd_async(hwnd, pos, delay=0.5):
    send_right_click_hwnd(hwnd, pos)
    await asyncio.sleep(delay)