import random
import threading
import uuid

from Controller.Randomizer import Randomizer
from Controller.SC2Window import SC2Window
from Controller.RunConfiguration import RunConfiguration
from Controller.CaptchaSolver import CaptchaSolver

import Constant.Constants as Constants
import Constant.ScreenPositions as pos
import Constant.Keymaps as KeyMaps
from Controller.SessionData import SessionData

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
        self.img_captcha = cv2.imread(r'C:\Users\kys\SLDbot\Images\captcha.png', cv2.IMREAD_GRAYSCALE)
        self.img_pausePopup = cv2.imread(r'C:\Users\kys\SLDbot\Images\popup_pause.png', cv2.IMREAD_GRAYSCALE)
        self.img_jewel_box = cv2.imread(r'C:\Users\kys\SLDbot\Images\jewel_box.png', cv2.IMREAD_GRAYSCALE)
        self.img_btn_jewel_claim = cv2.imread(r'C:\Users\kys\SLDbot\Images\btn_jewel_claim.png', cv2.IMREAD_GRAYSCALE)
        self.img_btn_buy_gus = cv2.imread(r'C:\Users\kys\SLDbot\Images\btn_buy_gus.png', cv2.IMREAD_GRAYSCALE)
        self.screen = None
        self.configuration = configuration
        self.play_count = 0
        self.stopwatch = Stopwatch()
        self.captcha_solver = CaptchaSolver()
        self.client_offset = (-7, 38)

    def capture_screen(self):
        while True:
            self.screen = self.sc2win.grab_screen()
            time.sleep(0.1)

    def test_func(self):
        pass

    async def update(self):
        capture_thread = threading.Thread(target=self.capture_screen)
        capture_thread.daemon = True
        capture_thread.start()

        while self.screen is None:
            await asyncio.sleep(1)

        while True:
            await self.handle_ready_popup()
            await self.handle_prepare_game()
            await self.main_game_update()
            await self.handle_result_popup()
            self.play_count += 1
            print(f'total play count={self.play_count}, total elapsed={self.stopwatch.get_elapsed():.2f}')

    def grab_bbox_from_screen(self, bbox):
        return self.screen[bbox[1]:bbox[1] + bbox[3], bbox[0]:bbox[0] + bbox[2], :]

    async def wait_for_bbox(self, img: numpy.ndarray):
        ret = None
        while ret is None:
            ret = image_search(self.screen, img)
            await asyncio.sleep(1)
        return ret

    async def handle_result_popup(self):
        print('handle_result_popup')
        while not check_similarity(self.screen, self.img_resultPopup, cut_line=0.6):
            await send_click_async(pos.btn_replay, delay=3)

    async def handle_ready_popup(self):
        print('handle_ready_popup')
        while not check_similarity(self.screen, self.img_loadingScreen):
            await send_click_async(pos.btn_game_start, delay=3)

    async def handle_prepare_game(self):
        print('handle_prepare_game')

        # find single button and click
        btn_bbox = await self.wait_for_bbox(self.img_btn_single)
        btn_pos = self.client_to_screen(self.get_bbox_center(btn_bbox))
        await send_click_async(btn_pos)

        # find eternal button and click
        btn_bbox = await self.wait_for_bbox(self.img_btn_eternal)
        btn_pos = self.client_to_screen(self.get_bbox_center(btn_bbox))
        await send_click_async(btn_pos)

        await asyncio.sleep(5)

        # select difficulty
        for i in range(self.configuration.difficulty):
            await send_click_async(pos.btn_difficulty_down, delay=0.05)

        # select game mode
        await send_click_async(pos.btn_DT, delay=0.05)
        await send_click_async(pos.btn_RS, delay=0.05)
        await send_click_async(pos.btn_HY, delay=0.05)
        await send_click_async(pos.btn_RP, delay=0.05)
        await send_click_async(pos.btn_NB, delay=0.05)

        await send_click_async(pos.btn_ready, delay=0.05)
        await asyncio.sleep(10)

    def client_to_screen(self, position):
        return position[0] + self.client_offset[0], position[1] + self.client_offset[1]

    @staticmethod
    def get_bbox_center(bbox):
        return (bbox[0] + bbox[2] // 2), (bbox[1] + bbox[3] // 2)

    def is_locked_by_debuff(self):
        buy_gas_bbox = image_search_from_bbox(self.screen, pos.bbox_main_ui, self.img_btn_buy_gus)
        return buy_gas_bbox is None

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
                await send_click_async(pos.btn_auto_put_money, delay=0.1)
            await send_click_async(pos.btn_put_money)

        async def use_sp():
            await send_key_press_async(self.ahk_win, KeyMaps.Characteristic)
            await send_click_async(pos.btn_load_characteristic)
            await send_key_press_async(self.ahk_win, KeyMaps.Characteristic)

        session_data = SessionData()
        randomizer = Randomizer()

        await setup_start_settings()
        await bank_setting()
        await use_sp()
        await self.change_rally(0)

        while not check_similarity(self.screen, self.img_resultPopup):
            await self.game_update(session_data, randomizer)
            await asyncio.sleep(1)

        print(f'session end, play time = {session_data.stopwatch.get_elapsed()}')

    async def select_center(self):
        await send_key_press_async(self.ahk_win, KeyMaps.Center)

    # noinspection PyMethodMayBeStatic
    async def get_money(self, how_many):
        await send_click_async(pos.btn_get_money_10 if how_many == 10 else pos.btn_get_money_100)

    # noinspection PyMethodMayBeStatic
    async def put_money(self):
        await send_click_async(pos.btn_put_money)

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

        await send_right_click_async(position)

    async def unit_upgrade(self, session_upgrade_count):
        await self.select_center()
        buy_gas_count = random.randint(2, 4 + session_upgrade_count)
        await self.buy_gas(buy_gas_count)
        await send_key_press_async(self.ahk_win, KeyMaps.UpgradeZone)
        for i in range(10):
            await send_key_press_async(self.ahk_win, 'qwerta')
        await self.select_center()

    async def race_upgrade(self, race):
        await self.select_center()
        await send_key_press_async(self.ahk_win, KeyMaps.UpgradeZone)
        for i in range(10):
            await send_key_press_async(self.ahk_win, race)
        await self.select_center()

    async def game_update(self, session_data, randomizer):
        await self.handle_bank(session_data, randomizer)
        await self.handle_lottery_4(session_data, randomizer)
        await self.handle_lottery_8(session_data, randomizer)
        await self.handle_upgrade(session_data, randomizer)
        await self.handle_rune_box(session_data)
        await self.handle_skin_box(session_data)
        await self.handle_merge_units(session_data, randomizer)
        await self.handle_check_game_end(session_data, randomizer)
        await self.handle_pause(session_data)
        await self.handle_captcha(session_data, randomizer)
        await self.handle_jewel_box(session_data)
        await self.handle_apm_noise(session_data, randomizer)

    async def handle_apm_noise(self, session_data, randomizer):
        elapsed = session_data.stopwatch.get_elapsed()
        if len(randomizer.apm_noise_times) > 0 and \
                elapsed > randomizer.apm_noise_times[0]:
            print(f'make apm noise: {elapsed}, remain times: {randomizer.apm_noise_times}')
            randomizer.apm_noise_times.pop(0)
            press_count = random.randint(100, 500)
            for i in range(press_count):
                await send_key_press_async(self.ahk_win, KeyMaps.Center, delay=0.01)
                await send_key_press_async(self.ahk_win, KeyMaps.Units, delay=0.01)
            await send_key_press_async(self.ahk_win, KeyMaps.Center, delay=1)


    async def handle_jewel_box(self, session_data):
        if session_data.force_quit_requested: return
        jewel_box_bbox = image_search(self.screen, self.img_jewel_box, accuracy=0.5)
        if jewel_box_bbox is None: return
        print(f'handle jewel box: {session_data.stopwatch.get_elapsed()}')

        claim_btn_bbox = image_search_from_bbox(self.screen, jewel_box_bbox, self.img_btn_jewel_claim)
        if claim_btn_bbox is None:
            print('cannot find jewel claim btn!!')
            return

        btn_pos = self.client_to_screen(self.get_bbox_center(claim_btn_bbox))
        await send_click_async(btn_pos, delay=0.5)

        empty_slot_pos = None
        idx = 0
        for slot in pos.jewel_slots:
            color = self.screen[slot[1], slot[0]]
            if Constants.jewel_empty_rgb_min[0] <= color[0] <= Constants.jewel_empty_rgb_max[0] and \
                    Constants.jewel_empty_rgb_min[1] <= color[1] <= Constants.jewel_empty_rgb_max[1] and \
                    Constants.jewel_empty_rgb_min[2] <= color[2] <= Constants.jewel_empty_rgb_max[2]:
                empty_slot_pos = slot
                print(f'empty slot idx: {idx}')
                break
            idx += 1

        if empty_slot_pos is not None:
            await send_click_async(empty_slot_pos, delay=0.5)
        else:
            print(f'cannot find empty jewel slot!!')

        await send_key_press_async(self.ahk_win, KeyMaps.Jewel)


    async def handle_pause(self, session_data):
        if session_data.force_quit_requested: return
        if image_search(self.screen, self.img_pausePopup) is None: return
        session_data.stopwatch.pause()
        print(f'paused: {session_data.stopwatch.get_elapsed()}')
        while image_search(self.screen, self.img_pausePopup) is not None:
            await asyncio.sleep(1)
        print('resume')
        session_data.stopwatch.resume()

    async def handle_merge_units(self, session_data, randomizer):
        if session_data.force_quit_requested: return

        elapsed = session_data.stopwatch.get_elapsed()
        if elapsed < randomizer.merge_start_time: return
        if elapsed - session_data.last_merge < randomizer.next_merge_interval: return
        if elapsed > randomizer.stop_lottery_time: return
        if self.is_locked_by_debuff(): return

        session_data.on_merge()
        randomizer.on_merge()

        await send_key_press_async(self.ahk_win, KeyMaps.MergeChart)
        for p in pos.merge_chart_units:
            await send_click_async(p, delay=0.01)
        await send_key_press_async(self.ahk_win, KeyMaps.MergeChart)

    async def handle_captcha(self, session_data, randomizer):
        if session_data.force_quit_requested: return
        elapsed = session_data.stopwatch.get_elapsed()
        if image_search(self.screen, self.img_captcha, accuracy=0.7) is None:
            return

        print(f'start handle captcha: {elapsed}')
        try_count = 0

        while True:
            await send_key_press_async(self.ahk_win, KeyMaps.Pause, delay=0.5)
            session_data.stopwatch.pause()

            captcha_area =  self.screen[pos.captcha_data_bbox[1]:pos.captcha_data_bbox[1] + pos.captcha_data_bbox[3],
                            pos.captcha_data_bbox[0]:pos.captcha_data_bbox[0] + pos.captcha_data_bbox[2],:]
            path = f'C:/Users/kys/SLDbot/Images/Captchas/captcha.png'
            cv2.imwrite(path, captcha_area)

            is_success = False
            result = None

            try:
                result = await self.captcha_solver.solve(path)
            except Exception as e:
                print(e)

            session_data.stopwatch.resume()
            await send_key_press_async(self.ahk_win, KeyMaps.Pause)

            if result is not None:
                captcha_id = result['captchaId']
                captcha_result = result['code']

                await send_click_async(pos.captcha_input)
                await send_key_press_async(self.ahk_win, captcha_result)
                await send_click_async(pos.captcha_submit, delay=0.5)

                is_success = image_search(self.screen, self.img_captcha, accuracy=0.7) is None
                print(f'try={try_count} result={result}, is_success={is_success}')
                self.captcha_solver.report(captcha_id, is_success)

            if is_success:
                break
            else:
                try_count+=1
                if try_count > 10:
                    await self.force_quit_game(session_data)
                    break
                else:
                    await send_click_async(pos.captcha_refresh)

    async def force_quit_game(self, session_data):
        session_data.force_quit_requested = True
        await send_key_press_async(self.ahk_win, KeyMaps.Pause, delay=1)
        await send_key_press_async(self.ahk_win, 'q')

    async def handle_check_game_end(self, session_data, randomizer):
        if session_data.force_quit_requested: return
        if session_data.stopwatch.get_elapsed() < 200: return

        if randomizer.exit_after_90r and session_data.rune_claim_count >= 3:
            await asyncio.sleep(random.randint(1, 20))
            await self.force_quit_game(session_data)
            return

        if randomizer.exit_after_110r and session_data.rune_claim_count >= 4:
            await asyncio.sleep(random.randint(1, 20))
            await self.force_quit_game(session_data)
            return

        if image_search(self.screen, self.img_center, accuracy=0.6) is not None:
            session_data.game_over_counter = 0
        else:
            session_data.game_over_counter += 1
            print(f'game over counter = {session_data.game_over_counter}')
            if session_data.game_over_counter >= 30:
                await self.force_quit_game(session_data)

    async def handle_bank(self, session_data, randomizer):
        if session_data.force_quit_requested: return
        async def increase_interest():
            print(f'increase interest({session_data.increase_interest_count}): {session_data.stopwatch.get_elapsed()}')
            session_data.on_increase_interest()
            await self.get_money(100)
            await send_click_async(pos.btn_increase_interest)
            await self.put_money()

        elapsed = session_data.stopwatch.get_elapsed()
        if elapsed > 280 and session_data.increase_interest_count == 0:
            await increase_interest()
        elif elapsed > 380 and session_data.increase_interest_count == 1:
            await increase_interest()
        elif elapsed > 480 and session_data.increase_interest_count == 2:
            await increase_interest()
        elif elapsed > 650 and session_data.increase_interest_count == 3:
            await increase_interest()
        elif elapsed > 800 and session_data.increase_interest_count == 4:
            await increase_interest()


    async def handle_lottery_8(self, session_data, randomizer):
        if session_data.force_quit_requested: return
        elapsed = session_data.stopwatch.get_elapsed()
        if elapsed > randomizer.stop_lottery_time: return
        if elapsed > randomizer.lottery8_start_time and \
                not session_data.unlock_lottery_8 and \
                not self.is_locked_by_debuff():
            print(f'unlock lottery8: {elapsed}')
            session_data.unlock_lottery_8 = True
            await self.select_center()
            await self.buy_gas(2)
            await send_key_press_async(self.ahk_win, KeyMaps.UpgradeZone)
            await send_key_press_async(self.ahk_win, 'x')
            await self.select_center()

        if session_data.unlock_lottery_8 and \
                elapsed - session_data.last_lottery > randomizer.next_lottery_interval and \
                not self.is_locked_by_debuff():
            print(f'lottery8: {elapsed}')
            randomizer.on_lottery(session_data)
            session_data.on_lottery()
            await self.change_rally(session_data.rally)
            await self.buy_unit(1)

    async def handle_lottery_4(self, session_data, randomizer):
        if session_data.force_quit_requested: return
        elapsed = session_data.stopwatch.get_elapsed()
        # 50%????????? 4?????? ?????? ?????????.
        if elapsed > Constants.Lottery4StartTime + randomizer.randint_1_10 and \
                randomizer.bool_seed and \
                not session_data.unlock_lottery_4 and \
                not self.is_locked_by_debuff():
            print(f'unlock lottery4: {elapsed}')
            session_data.unlock_lottery_4 = True
            await self.select_center()
            await self.buy_gas(1)
            await send_key_press_async(self.ahk_win, KeyMaps.UpgradeZone)
            await send_key_press_async(self.ahk_win, 'z')
            await self.select_center()

        if session_data.unlock_lottery_4 and \
                not session_data.unlock_lottery_8 and \
                session_data.lottery_count < 2 and \
                elapsed - session_data.last_lottery > randomizer.next_lottery_interval and \
                not self.is_locked_by_debuff():
            print(f'lottery4: {elapsed}')
            randomizer.on_lottery(session_data)
            session_data.on_lottery()
            await self.change_rally(session_data.rally)
            await self.buy_unit(0)

    async def handle_upgrade(self, session_data, randomizer):
        if session_data.force_quit_requested: return
        elapsed = session_data.stopwatch.get_elapsed()

        # graph noise
        if randomizer.noise_flag and elapsed > randomizer.noise_time and not self.is_locked_by_debuff():
            randomizer.noise_flag = False
            await self.race_upgrade('q')

        if elapsed > randomizer.upgrade_start_time and \
                session_data.upgrade_count < 6 and \
                elapsed - session_data.last_upgrade > randomizer.next_upgrade_interval and\
                not self.is_locked_by_debuff():
            print(f'unit upgrade: {elapsed}')
            session_data.on_upgrade()
            randomizer.on_upgrade(session_data)
            await self.unit_upgrade(session_data.upgrade_count)

    async def handle_rune_box(self, session_data):
        if session_data.force_quit_requested: return
        if image_search(self.screen, self.img_rune_box, 0.7) is None: return
        session_data.on_claim_rune()
        await send_click_async(pos.btn_start_roulette, delay=8)
        await send_click_async(pos.btn_claim_rune, delay=0.5)
        await self.handle_rune_result_if_possible(session_data)
        await self.handle_check_playtime_rune(session_data)

    async def handle_check_playtime_rune(self, session_data: SessionData):
        await send_click_async(pos.btn_claim_playtime_rune, delay=0.5)
        await self.handle_rune_result_if_possible(session_data)

    async def handle_rune_result_if_possible(self, session_data: SessionData):
        if image_search(self.screen, self.img_rune_result, 0.7) is None: return
        if self.configuration.rune_gain_behaviour == 0:
            print(f'sell rune: {session_data.stopwatch.get_elapsed()}')
            await send_click_async(pos.btn_sell_rune, delay=0.5)
        elif self.configuration.rune_gain_behaviour == 1:
            print(f'reinforce rune slot: {self.configuration.rune_reinforce_slot_index}')
            await send_click_async(pos.btn_reinforce_rune, delay=0.5)
            await send_click_async(pos.rune_reinforce_positions[self.configuration.rune_reinforce_slot_index],
                                   delay=0.5)
        else:
            pass

    async def handle_skin_box(self, session_data):
        if session_data.force_quit_requested: return
        if image_search(self.screen, self.img_skin_box) is None: return
        print(f'handle skin box: {session_data.stopwatch.get_elapsed()}')
        await send_click_async(pos.btn_open_skin_box, delay=5)
        await send_click_async(pos.btn_open_skin_box, delay=1)
        await send_click_async(pos.btn_close_skin_popup, delay=1)




