import asyncio
import random
import threading
import time

import ahk.keys
import cv2
import win32gui

from Controller.SC2Window import SC2Window
from Controller.RunConfiguration import RunConfiguration

import Constant.Constants as Constants
import Constant.ScreenPositions as pos
import Constant.Keymaps as KeyMaps

from Utils.ImageHelper import *
from Utils.InputWrapper import *
from Utils.Stopwatch import Stopwatch


ResultPopup, ReadyPopup, LoadingScreen, SelectEternal, SelectDifficulty, PlayMain \
    = 0, 1, 2, 3, 4, 5


class BotController:
    def __init__(self, sc2win: SC2Window, configuration: RunConfiguration):
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
        self.img_center = cv2.imread(r'C:\Users\kys\SLDbot\Images\center.png', cv2.IMREAD_GRAYSCALE)
        self.state = ReadyPopup
        self.screen = None
        self.configuration = configuration
        self.play_count = 0
        self.stopwatch = Stopwatch()

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
            elif self.state == ResultPopup:
                await self.handle_result_popup()

            self.play_count += 1

    async def wait_for_screen(self, img: numpy.ndarray, similarity = 0.8):
        while not check_similarity(self.screen, img, cut_line=similarity):
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
        await send_click_async(pos.btn_game_start)
        await self.wait_for_screen(self.img_loadingScreen)
        await asyncio.sleep(1)
        self.state = LoadingScreen

    async def handle_loading_screen(self):
        print('handle_loading_screen')
        btn_bbox = await self.wait_for_bbox(self.img_btn_single)
        print(f"single btn: {btn_bbox}")
        await send_click_async(self.get_center_pos(btn_bbox))
        await asyncio.sleep(3)
        self.state = SelectEternal

    async def handle_select_eternal(self):
        btn_bbox = await self.wait_for_bbox(self.img_btn_eternal)
        print(f"eternal btn: {btn_bbox}")
        await send_click_async(self.get_center_pos(btn_bbox))
        await asyncio.sleep(5)
        self.state = SelectDifficulty

    def get_center_pos(self, bbox):
        return (bbox[0] + bbox[2] // 2), (bbox[1] + bbox[3] // 2)

    async def handle_select_difficulty(self):
        for i in range(self.configuration.difficulty):
            await send_click_async(pos.btn_difficulty_down, delay=0.05)
        await send_click_async(pos.btn_DT, delay=0.05)
        await send_click_async(pos.btn_RS, delay=0.05)
        await send_click_async(pos.btn_HY, delay=0.05)
        await send_click_async(pos.btn_RP, delay=0.05)
        await send_click_async(pos.btn_NB, delay=0.05)
        await send_click_async(pos.btn_ready, delay=0.05)
        await asyncio.sleep(10)
        self.state = PlayMain

    async def main_game_update(self):
        self.ahk_win.activate()

        async def setup_start_settings():
            await send_key_press_async(self.ahk_win, KeyMaps.Setting)
            await send_click_async(pos.btn_optimize)
            await send_click_async(pos.btn_improverag_off)
            await send_key_press_async(self.ahk_win, KeyMaps.Setting)

        async def bank_setting():
            await send_key_press_async(self.ahk_win, KeyMaps.Bank)
            for i in range(10):
                send_click(pos.btn_auto_put_money)
                await asyncio.sleep(0.01)
            await send_click_async(pos.btn_put_money)

        async def use_sp():
            await send_key_press_async(self.ahk_win, KeyMaps.Characteristic)
            await send_click_async(pos.btn_load_characteristic)
            await send_key_press_async(self.ahk_win, KeyMaps.Characteristic)

        async def setup_rally():
            await self.select_center()
            await send_click_async(pos.TopLeft, btn=1)

        session_data = SessionData()
        randomizer = Randomizer()

        await setup_start_settings()
        await bank_setting()
        await use_sp()
        await setup_rally()

        while not check_similarity(self.screen, self.img_resultPopup):
            await self.game_update(session_data, randomizer)
            await asyncio.sleep(1)

        self.state = ResultPopup
        print(f'session end, play time = {session_data.stopwatch.get_elapsed()}')

    async def handle_result_popup(self):
        await send_click_async(pos.btn_replay)
        await self.wait_for_screen(self.img_readyPopup, similarity=0.6)
        await asyncio.sleep(5)
        self.state = ReadyPopup

    async def select_center(self):
        await send_key_press_async(self.ahk_win, KeyMaps.Center)

    async def get_money(self, how_many):
        # await send_key_press_async(self.ahk_win, KeyMaps.Bank)
        await send_click_async(pos.btn_get_money_10 if how_many == 10 else pos.btn_get_money_100)
        # await send_key_press_async(self.ahk_win, KeyMaps.Bank)

    async def put_money(self):
        # await send_key_press_async(self.ahk_win, KeyMaps.Bank)
        await send_click_async(pos.btn_put_money)
        # await send_key_press_async(self.ahk_win, KeyMaps.Bank)

    async def buy_gas(self, how_many):
        await self.get_money(100 if how_many > 2 else 10)
        for i in range(how_many):
            await send_key_press_async(self.ahk_win, 'd', delay=0.5)
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
        await send_click_async(position, 1)

    async def unit_upgrade(self, session_upgrade_count):
        await self.select_center()
        buy_count = min(session_upgrade_count + 1, 5)
        await self.buy_gas(buy_count)
        await send_key_press_async(self.ahk_win, KeyMaps.UpgradeZone)

        for i in range(5):
            await send_key_press_async(self.ahk_win, 'q')
            await send_key_press_async(self.ahk_win, 'w')
            await send_key_press_async(self.ahk_win, 'e')
            await send_key_press_async(self.ahk_win, 'r')
            await send_key_press_async(self.ahk_win, 't')
            await send_key_press_async(self.ahk_win, 'a')


    async def game_update(self, session_data, randomizer):
        await self.handle_bank(session_data, randomizer)
        await self.handle_lottery_4(session_data, randomizer)
        await self.handle_lottery_8(session_data, randomizer)
        await self.handle_upgrade(session_data, randomizer)
        await self.handle_rune_box(session_data)
        await self.handle_skin_box(session_data)
        await self.handle_merge_units(session_data, randomizer)
        await self.handle_check_game_end(session_data, randomizer)

    async def handle_merge_units(self, session_data, randomizer):
        if session_data.stopwatch.get_elapsed() < randomizer.merge_start_time: return
        if time.time() - session_data.last_merge < randomizer.next_merge_interval: return
        if session_data.stopwatch.get_elapsed() > randomizer.stop_lottery_time: return
        print(f'merge units: {session_data.stopwatch.get_elapsed()}')
        session_data.on_merge()
        randomizer.on_merge()

        await send_key_press_async(self.ahk_win, KeyMaps.MergeChart)
        for p in pos.merge_chart_units:
            await send_click_async(p, delay=0.01)
        await send_key_press_async(self.ahk_win, KeyMaps.MergeChart)

    async def handle_check_game_end(self, session_data, randomizer):
        if session_data.stopwatch.get_elapsed() < 200: return
        if image_search(self.screen, self.img_center, accuracy=0.6) is not None:
            session_data.game_over_counter = 0
            return

        session_data.game_over_counter += 1
        print(f'game over counter = {session_data.game_over_counter}')
        if session_data.game_over_counter < 10: return
        await send_key_press_async(self.ahk_win, KeyMaps.Pause, delay=0.5)
        await send_key_press_async(self.ahk_win, 'Q', delay=10)

    async def handle_bank(self, session_data, randomizer):
        async def increase_interest():
            print(f'increase interest: {session_data.stopwatch.get_elapsed()}')
            session_data.on_increase_interest()
            await self.get_money(100)
            await send_click_async(pos.btn_increase_interest)
            await self.put_money()

        elapsed = session_data.stopwatch.get_elapsed()
        if elapsed > 300 and session_data.increase_interest_count == 0:
            await increase_interest()
        elif elapsed > 420 and session_data.increase_interest_count == 1:
            await increase_interest()
        elif elapsed > 540 and session_data.increase_interest_count == 2:
            await increase_interest()
        elif elapsed > 700 and session_data.increase_interest_count == 3:
            await increase_interest()
        elif elapsed > 850 and session_data.increase_interest_count == 4:
            await increase_interest()


    async def handle_lottery_8(self, session_data, randomizer):
        elapsed = session_data.stopwatch.get_elapsed()
        if elapsed > randomizer.stop_lottery_time: return
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
        if elapsed > randomizer.upgrade_start_time and \
                session_data.upgrade_count < 8 and\
                time.time() - session_data.last_upgrade > randomizer.next_upgrade_interval:
            print(f'unit upgrade: {elapsed}')
            session_data.on_upgrade()
            randomizer.on_upgrade(session_data)
            await self.unit_upgrade(session_data.upgrade_count)

    async def handle_rune_box(self, session_data):
        if image_search(self.screen, self.img_rune_box, 0.7) is None: return
        print(f'handle rune box: {session_data.stopwatch.get_elapsed()}')
        await send_click_async(pos.btn_start_roulette, delay=10)
        await send_click_async(pos.btn_claim_rune, delay=0.5)

        if image_search(self.screen, self.img_rune_result, 0.7) is None: return
        if self.configuration.rune_gain_behaviour == 0:
            print(f'sell rune: {session_data.stopwatch.get_elapsed()}')
            await send_click_async(pos.btn_sell_rune, delay=0.5)
        elif self.configuration.rune_gain_behaviour == 1:
            print(f'reinforce rune slot: {self.configuration.rune_reinforce_slot_index}')
            await send_click_async(pos.btn_reinforce_rune, delay=0.5)
            await send_click_async(pos.rune_reinforce_positions[self.configuration.rune_reinforce_slot_index], delay=0.5)
        else:
            pass

    async def handle_skin_box(self, session_data):
        if image_search(self.screen, self.img_skin_box) is None: return
        print(f'handle skin box: {session_data.stopwatch.get_elapsed()}')
        await send_click_async(pos.btn_open_skin_box, delay=5)
        await send_click_async(pos.btn_open_skin_box, delay=1)
        await send_click_async(pos.btn_close_skin_popup, delay=1)


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
        self.game_over_counter = 0
        self.last_merge = 0

    def on_lottery(self):
        self.last_lottery = time.time()
        self.rally = (self.rally + 1) % 4
        self.lottery_count += 1

    def on_upgrade(self):
        self.last_upgrade = time.time()
        self.upgrade_count += 1

    def on_increase_interest(self):
        self.increase_interest_count += 1

    def on_merge(self):
        self.last_merge = time.time()


class Randomizer:
    def __init__(self):
        self.seed = random.randint(1, 1000000)
        self.bool_seed = random.randint(0, 1) == 0
        self.randint_1_10 = 0
        self.randint_1_100 = 0
        self.next_lottery_interval = 0
        self.next_upgrade_interval = 0
        self.refresh_random_values()
        self.next_merge_interval = 0
        self.stop_lottery_time = random.randint(2000, 3000)
        self.merge_start_time = random.randint(800, 1500)
        self.upgrade_start_time = random.randint(200, 300) if self.bool_seed else random.randint(300, 400)
        self.exit_manually = random.randint(0, 2) < 2

    def on_merge(self):
        self.next_merge_interval = random.randint(100, 200)

    def on_lottery(self, session_data: SessionData):
        def get_interval():
            if session_data.lottery_count < 3: return 70
            if session_data.lottery_count < 5: return 55
            if session_data.lottery_count < 7: return 45
            if session_data.lottery_count > 40: return random.randint(1, 50)
            return 35

        interval = get_interval()
        self.next_lottery_interval = random.randint(interval - self.randint_1_10, interval + self.randint_1_10)
        if random.randint(0, 1) == 0:
            self.refresh_random_values()

    def on_upgrade(self, session_data: SessionData):
        def get_interval():
            elapsed = session_data.stopwatch.get_elapsed()
            if elapsed < 400: return random.randint(40, 60) if self.bool_seed else random.randint(30, 50)
            if elapsed < 600: return random.randint(70, 100) if self.bool_seed else random.randint(50, 70)
            return random.randint(70, 110)

        interval = get_interval()
        self.next_upgrade_interval = interval + random.randint(self.randint_1_10, self.randint_1_10 + self.randint_1_100)

        if random.randint(0, 1) == 0:
            self.refresh_random_values()

    def refresh_random_values(self):
        self.randint_1_10 = random.randint(4, 7) if self.bool_seed else random.randint(1, 3) if random.randint(0, 1) == 0 else random.randint(8, 10)
        self.randint_1_100 = random.randint(40, 70) if self.bool_seed else random.randint(1, 39) if random.randint(0, 1) == 0 else random.randint(71, 100)

