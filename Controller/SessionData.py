from Utils.Stopwatch import Stopwatch


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
        self.force_quit_requested = False
        self.rune_claim_count = 0
        self.spend_all = False
        self.last_playtime_rune_check = 0

    def on_lottery(self):
        self.last_lottery = self.stopwatch.get_elapsed()
        self.rally = (self.rally + 1) % 4
        self.lottery_count += 1

    def on_upgrade(self):
        self.last_upgrade = self.stopwatch.get_elapsed()
        self.upgrade_count += 1

    def on_increase_interest(self):
        self.increase_interest_count += 1

    def on_merge(self):
        self.last_merge = self.stopwatch.get_elapsed()

    def on_claim_rune(self):
        self.rune_claim_count += 1
