import asyncio
import threading
import time


class Stopwatch:
    def __init__(self):
        self.elapsed = 0
        self.paused = False
        self.thread = threading.Thread(target=self.__update__)
        self.thread.daemon = True
        self.thread.start()

    def get_elapsed(self):
        return self.elapsed

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def __update__(self):
        while True:
            if self.paused: continue
            time.sleep(0.333)
            self.elapsed += 0.333
