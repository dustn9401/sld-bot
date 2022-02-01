import asyncio
import random
import threading
import time

import ahk.keys
import cv2
import win32gui

from Controller.SC2Window import SC2Window
import Constant.Constants as Constants
import Constant.ScreenPositions as pos
import Constant.Keymaps as KeyMaps

from Utils.ImageHelper import *
from Utils.InputWrapper import *
from Utils.Stopwatch import Stopwatch


ResultPopup, ReadyPopup, LoadingScreen, SelectEternal, SelectDifficulty, PlayMain \
    = 0, 1, 2, 3, 4, 5


class BotController:
    def __init__(self, sc2win: SC2Window, difficulty: int, rune_reinforce = 1):
        self.sc2win = sc2win
        self.ahk_win = self.sc2win.ahk_win
        self.img_loadingScreen = cv2.imread(r'C:\Users\kys\SLDbot\Images\ingame_loading.png')
        self.img_readyPopup = cv2.imread(r'C:\Users\kys\SLDbot\Images\popup_ready.png')
        self.img_resultPopup = cv2.imread(r'C:\Users\kys\SLDbot\Images\popup_result.png')
        self.img_btn_single = cv2.imread(r'C:\Users\kys\SLDbot\Images\btn_single.png', cv2.IMREAD_GRAYSCALE)
        self.img_btn_eternal = cv2.imread(r'C:\Users\kys\SLDbot\Images\btn_eternal.png', cv2.IMREAD_GRAYSCALE)
        self.img_rune_box = cv2.imread(r'C:\Users\kys\SLDbot\Images\rune_rullet.png', cv2.IMREAD_GRAYSCALE)
        self.img_rune_result = cv2.imread(r'C:\Users\kys\SLDbot\Images\rune_result.png', cv2.IMREAD_GRAYSCALE)
        self.img_skin_box = cv2.imread(r'C:\Users\kys\SLDbot\Images\skinbox.png', cv2.IMREAD_GRAYSCALE)
        self.state = ReadyPopup
        self.screen = None
        self.difficulty = difficulty
        self.play_count = 0
        self.stopwatch = Stopwatch()
        self.rune_reinforce = rune_reinforce

    def capture_screen(self):
        while True:
            self.screen = self.sc2win.grab_screen()
            # cv2.imshow('sc2', self.screen)
            cv2.waitKey(1)

    async def update(self):
        capture_thread = threading.Thread(target=self.capture_screen)
        capture_thread.daemon = True
        capture_thread.start()

        while True:
            # cur_pos = win32gui.GetCursorPos()
            # local_pos = win32gui.ScreenToClient(self.sc2win.hwnd, cur_pos)
            # print(f'cur={cur_pos}, local={local_pos}')
            if self.state == ReadyPopup:
                await self.handle_ready_popup()
            elif self.state == LoadingScreen:
                await self.handle_loading_screen()
            elif self.state == SelectEternal:
                await self.handle_select_eternal()
            elif self.state == SelectDifficulty:
                await self.handle_select_difficulty()
            elif self.state == PlayMain:
                await self.main_game_update()

            self.play_count += 1

    async def wait_for_screen(self, img: numpy.ndarray):
        while not check_similarity(self.screen, img):
            await asyncio.sleep(1)
        await asyncio.sleep(1)

    async def wait_for_bbox(self, img: numpy.ndarray):
        ret = None
        while ret is None:
            ret = image_search(self.screen, img)
            await asyncio.sleep(1)
        return ret

    async def handle_ready_popup(self):
        print('handle_ready_popup')
        await send_click_hwnd_async(self.sc2win.hwnd, pos.btn_game_start)
        await self.wait_for_screen(self.img_loadingScreen)
        await asyncio.sleep(1)
        self.state = LoadingScreen

    async def handle_loading_screen(self):
        print('handle_loading_screen')
        btn_bbox = await self.wait_for_bbox(self.img_btn_single)
        print(f"find single btn: {btn_bbox}")
        await send_click_hwnd_async(self.sc2win.hwnd, self.get_center_pos(btn_bbox))
        await asyncio.sleep(3)
        self.state = SelectEternal

    async def handle_select_eternal(self):
        btn_bbox = await self.wait_for_bbox(self.img_btn_eternal)
        print(f"find eternal btn: {btn_bbox}")
        await send_click_hwnd_async(self.sc2win.hwnd, self.get_center_pos(btn_bbox))
        await asyncio.sleep(5)
        self.state = SelectDifficulty

    def get_center_pos(self, bbox):
        return (bbox[0] + bbox[2] // 2), (bbox[1] + bbox[3] // 2)

    async def handle_select_difficulty(self):
        for i in range(self.difficulty):
            await send_click_hwnd_async(self.sc2win.hwnd, pos.btn_difficulty_down)
        await send_click_hwnd_async(self.sc2win.hwnd, pos.btn_DT)
        await send_click_hwnd_async(self.sc2win.hwnd, pos.btn_RS)
        await send_click_hwnd_async(self.sc2win.hwnd, pos.btn_HY)
        await send_click_hwnd_async(self.sc2win.hwnd, pos.btn_RP)
        await send_click_hwnd_async(self.sc2win.hwnd, pos.btn_NB)
        await send_click_hwnd_async(self.sc2win.hwnd, pos.btn_ready)
        await asyncio.sleep(10)
        self.state = PlayMain

    async def main_game_update(self):
        self.ahk_win.activate()

        async def setup_start_settings():
            await send_key_press_async(self.ahk_win, KeyMaps.Setting)
            await send_click_hwnd_async(self.sc2win.hwnd, pos.btn_optimize)
            await send_key_press_async(self.ahk_win, KeyMaps.Setting)

        async def bank_setting():
            await send_key_press_async(self.ahk_win, KeyMaps.Bank)
            for i in range(10):
                send_click_hwnd(self.sc2win.hwnd, pos.btn_auto_put_money)
                await asyncio.sleep(0.01)
            await send_click_hwnd_async(self.sc2win.hwnd, pos.btn_put_money)

        async def use_sp():
            await send_key_press_async(self.ahk_win, KeyMaps.Characteristic)
            await send_click_hwnd_async(self.sc2win.hwnd, pos.btn_load_characteristic)
            await send_key_press_async(self.ahk_win, KeyMaps.Characteristic)

        async def setup_rally():
            await self.select_center()
            await send_right_click_hwnd_async(self.sc2win.hwnd, pos.TopLeft)

        session_data = SessionData()
        randomizer = Randomizer()

        await setup_start_settings()
        await bank_setting()
        await use_sp()
        await setup_rally()

        while not check_similarity(self.screen, self.img_resultPopup):
            await self.game_update(session_data, randomizer)
            await asyncio.sleep(1)

        print(f'session end, play time = {session_data.stopwatch.get_elapsed()}')

    async def handle_result_popup(self):
        await send_click_hwnd_async(self.sc2win.hwnd, pos.btn_replay)
        await self.wait_for_screen(self.img_readyPopup)
        await asyncio.sleep(3)
        self.state = ReadyPopup

    async def select_center(self):
        await send_key_press_async(self.ahk_win, KeyMaps.Center)

    async def get_money(self, how_many):
        # await send_key_press_async(self.ahk_win, KeyMaps.Bank)
        await send_click_hwnd_async(self.sc2win.hwnd, pos.btn_get_money_10 if how_many == 10 else pos.btn_get_money_100)
        # await send_key_press_async(self.ahk_win, KeyMaps.Bank)

    async def put_money(self):
        # await send_key_press_async(self.ahk_win, KeyMaps.Bank)
        await send_click_hwnd_async(self.sc2win.hwnd, pos.btn_put_money)
        # await send_key_press_async(self.ahk_win, KeyMaps.Bank)

    async def buy_gas(self, how_many):
        await self.get_money(100 if how_many > 2 else 10)
        for i in range(how_many):
            await send_key_press_async(self.ahk_win, 'd')
        await self.put_money()

    async def buy_unit(self, lotto_type):
        await self.get_money(10)
        await send_key_press_async(self.ahk_win, 'w' if lotto_type == 0 else 'e')

    async def change_rally(self, rally):
        await self.select_center()
        position = pos.TopLeft if rally == 0 else \
            pos.BottomLeft if rally == 1 else \
                pos.TopRight if rally == 2 else \
                    pos.BottomRight
        await send_click_hwnd_async(self.sc2win.hwnd, position, 1)

    async def unit_upgrade(self, session_upgrade_count):
        await self.select_center()
        await self.buy_gas(session_upgrade_count * 2)
        await send_key_press_async(self.ahk_win, KeyMaps.UpgradeZone)

        for i in range(5):
            await send_key_press_async(self.ahk_win, 'q')
            await send_key_press_async(self.ahk_win, 'w')
            await send_key_press_async(self.ahk_win, 'e')
            await send_key_press_async(self.ahk_win, 'r')
            await send_key_press_async(self.ahk_win, 't')
            await send_key_press_async(self.ahk_win, 'a')


    async def game_update(self, session_data, randomizer):
        print(f'elapsed={session_data.stopwatch.get_elapsed()}')
        await self.handle_bank(session_data, randomizer)
        await self.handle_lottery_4(session_data, randomizer)
        await self.handle_lottery_8(session_data, randomizer)
        await self.handle_upgrade(session_data, randomizer)
        await self.handle_rune_box(session_data)
        await self.handle_skin_box(session_data)

    async def handle_bank(self, session_data, randomizer):
        async def increase_interest():
            print(f'increase interest: {session_data.stopwatch.get_elapsed()}')
            session_data.on_increase_interest()
            await self.get_money(100)
            await send_click_hwnd_async(self.sc2win.hwnd, pos.btn_increase_interest)
            await self.put_money()

        elapsed = session_data.stopwatch.get_elapsed()
        if elapsed > 300 and session_data.increase_interest_count == 0:
            await increase_interest()
        elif elapsed > 375 and session_data.increase_interest_count == 1:
            await increase_interest()
        elif elapsed > 450 and session_data.increase_interest_count == 2:
            await increase_interest()
        elif elapsed > 510 and session_data.increase_interest_count == 3:
            await increase_interest()
        elif elapsed > 670 and session_data.increase_interest_count == 4:
            await increase_interest()
        elif elapsed > 730 and session_data.increase_interest_count == 5:
            await increase_interest()


    async def handle_lottery_8(self, session_data, randomizer):
        elapsed = session_data.stopwatch.get_elapsed()
        if elapsed > Constants.Lottery8StartTime + randomizer.randint_1_10 and \
                not session_data.unlock_lottery_8:
            print(f'unlock lottery8: {elapsed}')
            session_data.unlock_lottery_8 = True
            await self.select_center()
            await self.buy_gas(2)
            await send_key_press_async(self.ahk_win, KeyMaps.UpgradeZone)
            await send_key_press_async(self.ahk_win, 'x')
            await self.select_center()

        if session_data.unlock_lottery_8 and \
                time.time() - session_data.last_lottery > randomizer.next_lottery_interval:
            print(f'lottery8: {elapsed}')
            randomizer.on_lottery(session_data)
            session_data.on_lottery()
            await self.change_rally(session_data.rally)
            await self.buy_unit(1)

    async def handle_lottery_4(self, session_data, randomizer):
        elapsed = session_data.stopwatch.get_elapsed()
        if elapsed > Constants.Lottery4StartTime + randomizer.randint_1_10 and \
                not session_data.unlock_lottery_4:
            print(f'unlock lottery4: {elapsed}')
            session_data.unlock_lottery_4 = True
            await self.select_center()
            await self.buy_gas(1)
            await send_key_press_async(self.ahk_win, KeyMaps.UpgradeZone)
            await send_key_press_async(self.ahk_win, 'z')
            await self.select_center()

        if session_data.unlock_lottery_4 and \
                not session_data.unlock_lottery_8 and \
                time.time() - session_data.last_lottery > randomizer.next_lottery_interval:
            print(f'lottery4: {elapsed}')
            randomizer.on_lottery(session_data)
            session_data.on_lottery()
            await self.change_rally(session_data.rally)
            await self.buy_unit(0)

    async def handle_upgrade(self, session_data, randomizer):
        elapsed = session_data.stopwatch.get_elapsed()
        if elapsed > Constants.UpgradeStartTime + randomizer.randint_1_10 and \
                session_data.upgrade_count < 10 and\
                time.time() - session_data.last_upgrade > randomizer.next_upgrade_interval:
            print(f'unit upgrade: {elapsed}')
            session_data.on_upgrade()
            randomizer.on_upgrade(session_data)
            await self.unit_upgrade(session_data.upgrade_count)

    async def handle_rune_box(self, session_data):
        if image_search(self.screen, self.img_rune_box, 0.7) is None: return
        print(f'handle rune box: {session_data.stopwatch.get_elapsed()}')
        await send_click_hwnd_async(self.sc2win.hwnd, pos.btn_start_roulette, delay=10)
        await send_click_hwnd_async(self.sc2win.hwnd, pos.btn_reinforce_rune, delay=0.5)
        await send_click_hwnd_async(self.sc2win.hwnd, pos.rune_reinforce_positions[self.rune_reinforce], delay=0.5)

    async def handle_skin_box(self, session_data):
        if image_search(self.screen, self.img_skin_box) is None: return
        print(f'handle skin box: {session_data.stopwatch.get_elapsed()}')
        await send_click_hwnd_async(self.sc2win.hwnd, pos.btn_open_skin_box, delay=5)
        await send_click_hwnd_async(self.sc2win.hwnd, pos.btn_open_skin_box, delay=1)
        await send_click_hwnd_async(self.sc2win.hwnd, pos.btn_close_skin_popup, delay=1)


class SessionData:
    def __init__(self):
        self.stopwatch = Stopwatch()
        self.unlock_lottery_4 = False
        self.unlock_lottery_8 = False
        self.last_lottery = 0
        self.lottery_count = 0
        self.rally = 0
        self.last_upgrade = 0
        self.upgrade_count = 0
        self.increase_interest_count = 0

    def on_lottery(self):
        self.last_lottery = time.time()
        self.rally = (self.rally + 1) % 4
        self.lottery_count += 1

    def on_upgrade(self):
        self.last_upgrade = time.time()
        self.upgrade_count += 1

    def on_increase_interest(self):
        self.increase_interest_count += 1


class Randomizer:
    def __init__(self):
        self.seed = random.randint(1, 1000000)
        self.bool_seed = random.randint(0, 1) == 0
        self.randint_1_10 = 0
        self.randint_1_100 = 0
        self.next_lottery_interval = 0
        self.next_upgrade_interval = 0
        self.refresh_random_values()

    def on_lottery(self, session_data: SessionData):
        def get_interval_by_lottery_count(lottery_count):
            if lottery_count < 3: return 80
            if lottery_count < 5: return 60
            if lottery_count < 7: return 40
            return 30

        interval = get_interval_by_lottery_count(session_data.lottery_count)
        self.next_lottery_interval = random.randint(interval - self.randint_1_10, interval + self.randint_1_10)
        if random.randint(0, 1) == 0:
            self.refresh_random_values()

    def on_upgrade(self, session_data: SessionData):
        def get_interval():
            elapsed = session_data.stopwatch.get_elapsed()
            if elapsed < 400: return 120
            if elapsed < 600: return 100
            return 80

        interval = get_interval()
        if self.bool_seed:
            self.next_upgrade_interval = interval + random.randint(self.randint_1_10, self.randint_1_100)
        else:
            self.next_upgrade_interval = interval - (random.randint(self.randint_1_10, self.randint_1_100) // 2)

        if random.randint(0, 1) == 0:
            self.refresh_random_values()

    def refresh_random_values(self):
        self.randint_1_10 = random.randint(4, 7) if self.bool_seed else random.randint(1, 3) if random.randint(0, 1) == 0 else random.randint(8, 10)
        self.randint_1_100 = random.randint(40, 70) if self.bool_seed else random.randint(1, 39) if random.randint(0, 1) == 0 else random.randint(71, 100)

