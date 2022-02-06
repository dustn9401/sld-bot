import random

from Constant import Constants
from Controller import SessionData


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
        self.stop_lottery_time = random.randint(1800, 2500)
        self.merge_start_time = random.randint(800, 1500)
        self.upgrade_start_time = random.randint(200, 300) if self.bool_seed else random.randint(300, 400)
        self.lottery8_start_time = Constants.Lottery8StartTime + (random.randint(0, 10) if self.bool_seed else random.randint(11, 20))
        self.noise_flag = random.randint(0, 1) == 0
        self.noise_time = random.randint(30, self.upgrade_start_time)
        self.spend_all_time = random.randint(800, 1200)
        self.apm_noise_times = [random.randint(100, 3000) for i in range(random.randint(3, 10))]
        self.apm_noise_times = sorted(self.apm_noise_times)
        self.exit_after_110r = random.randint(0, 2) <= 1
        self.exit_after_90r = random.randint(0, 4) == 4
        print(f'randomizer: 90r={self.exit_after_90r}, 110r={self.exit_after_110r}')

    def on_merge(self):
        self.next_merge_interval = random.randint(100, 200)

    def on_lottery(self, session_data: SessionData):
        def get_base_interval():
            if session_data.lottery_count < (3 if self.bool_seed else 1): return 60
            if session_data.lottery_count < (5 if self.bool_seed else 3): return 50
            if session_data.lottery_count < (7 if self.bool_seed else 5): return 40
            if session_data.lottery_count > 40: return random.randint(1, 50)
            return 35

        interval = get_base_interval()
        self.next_lottery_interval = random.randint(interval - self.randint_1_10, interval + self.randint_1_10)

    def on_upgrade(self, session_data: SessionData):
        def get_base_interval():
            if session_data.upgrade_count <= 1: return random.randint(80, 120)
            if session_data.upgrade_count == 2: return random.randint(1, 10) if self.randint_1_10 < 2 else random.randint(60, 80) if self.bool_seed else random.randint(10, 150)
            if session_data.upgrade_count == 3: return random.randint(70, 100) if self.bool_seed else random.randint(10, 150)
            return random.randint(10, 200)

        interval = get_base_interval()
        self.next_upgrade_interval = interval + random.randint(self.randint_1_10, self.randint_1_10 + self.randint_1_100)

    def refresh_random_values(self):
        self.randint_1_10 = random.randint(4, 7) if self.bool_seed else random.randint(1, 3) if random.randint(0, 1) == 0 else random.randint(8, 10)
        self.randint_1_100 = random.randint(40, 70) if self.bool_seed else random.randint(1, 39) if random.randint(0, 1) == 0 else random.randint(71, 100)
